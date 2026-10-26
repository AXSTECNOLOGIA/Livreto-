#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auditoria_TSE_2026.py
=====================

Auditoria estatística do comparecimento por seção eleitoral — cargo Presidente
da República, Eleições Gerais 2026, 1º turno x 2º turno.

Este script NÃO contém, estima nem simula resultados eleitorais. Todo número
dos relatórios é calculado a partir dos arquivos oficiais do TSE efetivamente
lidos e registrados no manifesto (URL, data de acesso, versão e SHA-256).
Se uma fonte não puder ser obtida, a falha é registrada e os relatórios
declaram a auditoria como PARCIAL ou NÃO EXECUTADA.

Requisitos
----------
Python >= 3.10
    pip install -r requirements.txt
    (pandas>=2.0, numpy>=1.24, requests>=2.31, XlsxWriter>=3.1, reportlab>=4.0)

Execução
--------
1) Coleta automática (API CKAN do Portal de Dados Abertos do TSE):
       python Auditoria_TSE_2026.py --saida ./saida

2) Arquivos já baixados manualmente, com os nomes publicados pelo TSE:
       python Auditoria_TSE_2026.py --entrada ./dados_tse --saida ./saida

3) Subconjunto de UFs (auditoria PARCIAL, sinalizada nos relatórios):
       python Auditoria_TSE_2026.py --ufs DF,AC,RR --saida ./saida

Arquivos reconhecidos (nome publicado pelo TSE)
-----------------------------------------------
    detalhe_votacao_secao_2026[_UF].zip|csv  aptos, comparecimento, abstenções e votos
                                             por tipo, por seção e cargo   (OBRIGATÓRIO)
    votacao_secao_2026_UF.zip|csv            votos por votável e seção     (conferência)
    bweb_1t_UF_<versao>.zip|csv              boletins de urna 1º turno     (validação)
    bweb_2t_UF_<versao>.zip|csv              boletins de urna 2º turno     (validação)
    eleitorado_local_votacao_2026*.zip|csv   seções agregadas, eleitorado por seção
    secoes_eleitorais_alteradas_2t*.zip|csv  seções com mudança de local no 2º turno

Saídas (diretório --saida)
--------------------------
    Auditoria_Seções_2026.xlsx   planilha com as 8 abas exigidas
    Auditoria_TSE_2026.pdf       relatório
    manifesto_fontes.json        proveniência de cada arquivo (URL, data, SHA-256)
    secoes_consolidadas.csv.gz   tabela consolidada completa
    inconsistencias.csv.gz       todos os testes que falharam (formato longo)
    auditoria.log                log de execução

Códigos de saída: 0 = auditoria nacional completa; 1 = parcial; 2 = não executada
(fonte obrigatória indisponível); 3 = erro inesperado.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import logging
import platform
import re
import sys
import unicodedata
import warnings
import zipfile
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Callable, Iterator
from urllib.parse import urlparse

import numpy as np
import pandas as pd

VERSAO_SCRIPT = "1.0.0"
ANO = 2026
CD_CARGO_PRESIDENTE = 1
UFS_BRASIL = (
    "AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA", "MG", "MS", "MT", "PA",
    "PB", "PE", "PI", "PR", "RJ", "RN", "RO", "RR", "RS", "SC", "SE", "SP", "TO",
)
UF_EXTERIOR = "ZZ"
KEY = ["SG_UF", "CD_MUNICIPIO", "NR_ZONA", "NR_SECAO"]
# Códigos que o LEIAME do TSE usa para "#NULO#" (-1) e "#NE#" (-3) em campos numéricos.
SENTINELAS = (-1.0, -3.0)
NA_TSE = ["#NULO#", "#NULO", "#NE#", "#NE", ""]

CKAN_API = "https://dadosabertos.tse.jus.br/api/3/action/package_show"
CKAN_DATASETS = ("resultados-2026", "eleitorado-2026")
_CDN = "https://cdn.tse.jus.br/estatistica/sead/odsele"
# Usadas apenas se o recurso não aparecer na API CKAN. São o padrão de nomes das
# eleições anteriores; o manifesto registra a origem como "URL inferida".
URL_INFERIDAS = {
    "detalhe_votacao_secao": _CDN + "/detalhe_votacao_secao/detalhe_votacao_secao_2026.zip",
    "votacao_secao": _CDN + "/votacao_secao/votacao_secao_2026_{uf}.zip",
    "eleitorado_local_votacao": _CDN + "/eleitorado_locais_votacao/eleitorado_local_votacao_2026.zip",
}

PADROES = {
    "detalhe_votacao_secao": re.compile(
        r"^detalhe_votacao_secao_2026(?:_(?P<uf>[A-Z]{2}|BRASIL))?\.(?:zip|csv)$", re.I),
    "votacao_secao": re.compile(r"^votacao_secao_2026_(?P<uf>[A-Z]{2})\.(?:zip|csv)$", re.I),
    "bweb": re.compile(
        r"^bweb_(?P<turno>[12])t_(?P<uf>[A-Z]{2})(?:_(?P<versao>\d+))?\.(?:zip|csv)$", re.I),
    "eleitorado_local_votacao": re.compile(
        r"^eleitorado_local_votacao_2026(?:_(?P<uf>[A-Z]{2}|BRASIL))?\.(?:zip|csv)$", re.I),
    "secoes_alteradas_2t": re.compile(r"^secoes_eleitorais_alteradas_2t.*\.(?:zip|csv)$", re.I),
}

SITUACOES_COMPARAVEIS = ("COMPARAVEL", "COMPARAVEL_COM_RESSALVA")
CLASSES = {
    "C1": "Consistente",
    "C2": "Variação estatística atípica",
    "C3": "Divergência explicada",
    "C4": "Inconsistência documental",
    "C5": "Verificação pendente",
}

LOG = logging.getLogger("auditoria_tse_2026")


class ErroFonte(Exception):
    """Arquivo ilegível, corrompido ou fora do esquema esperado."""


# =============================================================================
# Configuração
# =============================================================================
@dataclass(frozen=True)
class Parametros:
    limiar_pct: float = 15.0      # filtro exploratório: crescimento % do comparecimento
    limiar_abs: float = 30.0      # filtro exploratório: crescimento absoluto (eleitores)
    z_limite: float = 3.5         # z-score robusto (Iglewicz & Hoaglin, 1993)
    iqr_k: float = 1.5            # cerca de Tukey: Q3 + k * IQR
    min_pares: int = 10           # mínimo de seções no município para usá-lo como grupo de referência
    n_faixas_aptos: int = 5       # faixas de tamanho (quantis nacionais) para o grupo alternativo
    tol_aptos_abs: float = 5.0    # tolerância de variação de aptos entre turnos (eleitores)
    tol_aptos_rel: float = 0.02   # tolerância relativa de variação de aptos (fração)
    chunksize: int = 500_000


@dataclass
class Fonte:
    tipo: str
    uf: str | None = None
    turno: int | None = None
    versao_nome: str | None = None
    url: str | None = None
    origem_url: str | None = None          # "API CKAN", "URL inferida", "arquivo local"
    caminho: str | None = None
    data_acesso_utc: str | None = None
    http_status: int | None = None
    http_last_modified: str | None = None
    http_etag: str | None = None
    ckan_resource_id: str | None = None
    ckan_last_modified: str | None = None
    tamanho_bytes: int | None = None
    sha256: str | None = None
    codificacao: str | None = None
    delimitador: str | None = None
    membros_lidos: str = ""
    linhas_lidas: int = 0
    linhas_filtradas: int = 0
    status: str = "PENDENTE"
    erro: str | None = None


def agora_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def configurar_log(saida: Path, verboso: bool) -> None:
    saida.mkdir(parents=True, exist_ok=True)
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    LOG.setLevel(logging.DEBUG if verboso else logging.INFO)
    for h in LOG.handlers:
        h.close()
    LOG.handlers.clear()
    for h in (logging.StreamHandler(sys.stderr),
              logging.FileHandler(saida / "auditoria.log", mode="w", encoding="utf-8")):
        h.setFormatter(fmt)
        LOG.addHandler(h)


def sem_acento(s: str) -> str:
    return unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower().strip()


def sha256_arquivo(caminho: Path) -> str:
    h = hashlib.sha256()
    with open(caminho, "rb") as f:
        for bloco in iter(lambda: f.read(1 << 20), b""):
            h.update(bloco)
    return h.hexdigest()


# =============================================================================
# Etapa A — Descoberta e coleta
# =============================================================================
def identificar_arquivo(nome: str) -> dict | None:
    base = Path(urlparse(nome).path).name
    for tipo, rx in PADROES.items():
        m = rx.match(base)
        if not m:
            continue
        g = m.groupdict()
        uf = (g.get("uf") or "").upper() or None
        if uf == "BRASIL":
            uf = None
        turno = int(g["turno"]) if g.get("turno") else None
        return {"tipo": tipo, "uf": uf, "turno": turno, "versao": g.get("versao"), "nome": base}
    return None


def _versao_ordenavel(v: str | None) -> str:
    """bweb usa sufixo DDMMAAAAHHMM; converte para AAAAMMDDHHMM para ordenar."""
    if v and len(v) == 12 and v.isdigit():
        return v[4:8] + v[2:4] + v[0:2] + v[8:12]
    return v or ""


def _sessao_http():
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry

    s = requests.Session()
    retry = Retry(total=5, backoff_factor=2, status_forcelist=(429, 500, 502, 503, 504),
                  allowed_methods=("GET", "HEAD"))
    s.mount("https://", HTTPAdapter(max_retries=retry))
    s.headers["User-Agent"] = f"Auditoria_TSE_2026/{VERSAO_SCRIPT}"
    return s


def descobrir_ckan(sessao, timeout: int, falhas: list[dict], hosts_inacessiveis: set[str]) -> list[dict]:
    import requests

    candidatos = []
    host = urlparse(CKAN_API).hostname
    for ds in CKAN_DATASETS:
        acesso = agora_iso()
        if host in hosts_inacessiveis:
            falhas.append({"etapa": "descoberta CKAN", "dataset": ds, "url": f"{CKAN_API}?id={ds}",
                           "data_acesso_utc": acesso, "erro": f"não tentado: host {host} inacessível"})
            continue
        try:
            r = sessao.get(CKAN_API, params={"id": ds}, timeout=timeout)
            r.raise_for_status()
            pacote = r.json()["result"]
        except Exception as e:  # noqa: BLE001 — qualquer falha de rede/JSON vira registro
            if isinstance(e, requests.exceptions.ConnectionError):
                hosts_inacessiveis.add(host)
            falhas.append({"etapa": "descoberta CKAN", "dataset": ds, "url": f"{CKAN_API}?id={ds}",
                           "data_acesso_utc": acesso, "erro": f"{type(e).__name__}: {e}"})
            LOG.error("Falha ao consultar CKAN %s: %s", ds, e)
            continue
        LOG.info("CKAN %s: %d recursos listados", ds, len(pacote.get("resources", [])))
        for rec in pacote.get("resources", []):
            url = rec.get("url") or ""
            info = identificar_arquivo(url)
            if info:
                info.update(url=url, origem="API CKAN", ckan_id=rec.get("id"),
                            ckan_lm=rec.get("last_modified") or rec.get("metadata_modified"))
                candidatos.append(info)
    return candidatos


def descobrir_local(diretorio: Path) -> list[dict]:
    candidatos = []
    for p in sorted(diretorio.rglob("*")):
        if p.is_file():
            info = identificar_arquivo(p.name)
            if info:
                info.update(caminho=str(p), origem="arquivo local")
                candidatos.append(info)
    return candidatos


def planejar_fontes(candidatos: list[dict], ufs: list[str], opc: argparse.Namespace,
                    permitir_inferidas: bool) -> list[Fonte]:
    """Escolhe um arquivo por (tipo, UF, turno). Nunca soma arquivo nacional e por UF."""
    def para_fonte(c: dict) -> Fonte:
        return Fonte(tipo=c["tipo"], uf=c["uf"], turno=c["turno"], versao_nome=c.get("versao"),
                     url=c.get("url"), origem_url=c["origem"], caminho=c.get("caminho"),
                     ckan_resource_id=c.get("ckan_id"), ckan_last_modified=c.get("ckan_lm"))

    def por_tipo(t):
        return [c for c in candidatos if c["tipo"] == t]

    fontes: list[Fonte] = []

    # detalhe_votacao_secao / eleitorado_local_votacao: por UF se houver, senão o nacional.
    for tipo, desligado in (("detalhe_votacao_secao", False),
                            ("eleitorado_local_votacao", opc.sem_eleitorado)):
        if desligado:
            continue
        cs = por_tipo(tipo)
        por_uf = {c["uf"]: c for c in cs if c["uf"]}
        nacional = [c for c in cs if not c["uf"]]
        if por_uf and all(u in por_uf for u in ufs):
            fontes += [para_fonte(por_uf[u]) for u in ufs]
        elif nacional:
            fontes.append(para_fonte(nacional[0]))
        elif por_uf:
            fontes += [para_fonte(por_uf[u]) for u in ufs if u in por_uf]
            fontes += [Fonte(tipo=tipo, uf=u, status="NAO_ENCONTRADA",
                             erro="arquivo não localizado") for u in ufs if u not in por_uf]
        elif permitir_inferidas:
            fontes.append(Fonte(tipo=tipo, url=URL_INFERIDAS[tipo],
                                origem_url="URL inferida (padrão de eleições anteriores)"))
        else:
            fontes.append(Fonte(tipo=tipo, status="NAO_ENCONTRADA", erro="arquivo não localizado"))

    if not opc.sem_votacao_secao:
        cs = {c["uf"]: c for c in por_tipo("votacao_secao")}
        for u in ufs:
            if u in cs:
                fontes.append(para_fonte(cs[u]))
            elif permitir_inferidas:
                fontes.append(Fonte(tipo="votacao_secao", uf=u,
                                    url=URL_INFERIDAS["votacao_secao"].format(uf=u),
                                    origem_url="URL inferida (padrão de eleições anteriores)"))
            else:
                fontes.append(Fonte(tipo="votacao_secao", uf=u, status="NAO_ENCONTRADA",
                                    erro="arquivo não localizado"))

    if not opc.sem_bweb:
        # Nomes de boletins de urna têm carimbo de data; sem URL inferida possível.
        for u in ufs:
            for t in (1, 2):
                cs = [c for c in por_tipo("bweb") if c["uf"] == u and c["turno"] == t]
                if cs:
                    fontes.append(para_fonte(max(cs, key=lambda c: _versao_ordenavel(c["versao"]))))
                else:
                    fontes.append(Fonte(tipo="bweb", uf=u, turno=t, status="NAO_ENCONTRADA",
                                        erro="boletim de urna não listado na fonte"))

    alt = por_tipo("secoes_alteradas_2t")
    if alt:
        fontes.append(para_fonte(alt[0]))
    else:
        fontes.append(Fonte(tipo="secoes_alteradas_2t", status="NAO_ENCONTRADA",
                            erro="lista oficial de seções alteradas no 2º turno não localizada "
                                 "(publicada fora do CKAN; forneça via --entrada)"))
    return fontes


def baixar(fonte: Fonte, dir_dados: Path, sessao, timeout: int, reusar: bool,
           hosts_inacessiveis: set[str]) -> None:
    import requests

    destino = dir_dados / fonte.tipo / Path(urlparse(fonte.url).path).name
    destino.parent.mkdir(parents=True, exist_ok=True)
    fonte.data_acesso_utc = agora_iso()
    host = urlparse(fonte.url).hostname
    if host in hosts_inacessiveis:  # evita repetir minutos de retentativas contra host já recusado
        fonte.status = "FALHA_DOWNLOAD"
        fonte.erro = f"não tentado: host {host} inacessível nesta execução (ver falha anterior)"
        return
    try:
        with sessao.get(fonte.url, stream=True, timeout=timeout) as r:
            fonte.http_status = r.status_code
            fonte.http_last_modified = r.headers.get("Last-Modified")
            fonte.http_etag = r.headers.get("ETag")
            r.raise_for_status()
            esperado = int(r.headers.get("Content-Length") or 0)
            if reusar and destino.exists() and esperado and destino.stat().st_size == esperado:
                LOG.info("Reutilizando %s (mesmo tamanho do servidor)", destino.name)
            else:
                LOG.info("Baixando %s", fonte.url)
                tmp = destino.with_name(destino.name + ".part")
                with open(tmp, "wb") as f:
                    for bloco in r.iter_content(1 << 20):
                        f.write(bloco)
                if esperado and tmp.stat().st_size != esperado:
                    raise IOError(f"download truncado: {tmp.stat().st_size} de {esperado} bytes")
                tmp.replace(destino)
        fonte.caminho = str(destino)
        fonte.tamanho_bytes = destino.stat().st_size
        fonte.sha256 = sha256_arquivo(destino)
        fonte.status = "BAIXADO"
    except Exception as e:  # noqa: BLE001
        if isinstance(e, requests.exceptions.ConnectionError):
            hosts_inacessiveis.add(host)
        fonte.status = "FALHA_DOWNLOAD"
        fonte.erro = f"{type(e).__name__}: {e}"
        LOG.error("Falha no download de %s: %s", fonte.url, fonte.erro)


def registrar_local(fonte: Fonte) -> None:
    p = Path(fonte.caminho)
    fonte.data_acesso_utc = agora_iso()
    fonte.tamanho_bytes = p.stat().st_size
    fonte.sha256 = sha256_arquivo(p)
    fonte.status = "LOCAL"


# =============================================================================
# Leitura e validação de formato
# =============================================================================
def membros_csv(caminho: Path) -> Iterator[tuple[str, Callable]]:
    """Itera os CSVs de um .zip (ou o próprio .csv). Ignora o consolidado _BRASIL
    quando há arquivos por UF, para não contar seções duas vezes."""
    if caminho.suffix.lower() == ".csv":
        yield caminho.name, lambda: open(caminho, "rb")
        return
    if not zipfile.is_zipfile(caminho):
        raise ErroFonte(f"{caminho.name}: não é um arquivo ZIP válido")
    with zipfile.ZipFile(caminho) as zf:
        nomes = [n for n in zf.namelist() if n.lower().endswith(".csv")]
        if not nomes:
            raise ErroFonte(f"{caminho.name}: ZIP sem arquivos CSV")
        por_uf = [n for n in nomes if not re.search(r"_BRASIL\.csv$", n, re.I)]
        for n in (por_uf or nomes):
            yield n, (lambda n=n: zf.open(n))


def detectar_formato(abrir: Callable) -> tuple[str, str]:
    with abrir() as fh:
        amostra = fh.read(1 << 20)
    if not amostra:
        raise ErroFonte("arquivo vazio")
    if amostra.startswith(b"\xef\xbb\xbf"):
        enc = "utf-8-sig"
    else:
        enc = "latin-1"  # padrão dos arquivos do TSE
        if any(b > 127 for b in amostra):
            try:
                amostra.decode("utf-8")
                enc = "utf-8"
            except UnicodeDecodeError as e:
                if e.start >= len(amostra) - 4:  # corte no meio de um caractere multibyte
                    enc = "utf-8"
    primeira = amostra.split(b"\n", 1)[0].decode(enc, errors="replace")
    sep = max((";", ",", "\t", "|"), key=primeira.count)
    if primeira.count(sep) == 0:
        raise ErroFonte("delimitador não identificado no cabeçalho")
    return enc, sep


def ler_tabela(fonte: Fonte, requeridas: list[str], opcionais: list[str],
               filtro: Callable[[pd.DataFrame], pd.DataFrame] | None, chunksize: int,
               a_cada_arquivo: Callable[[pd.DataFrame], pd.DataFrame] | None = None) -> pd.DataFrame:
    """Lê os CSVs da fonte em blocos, valida o esquema e aplica o filtro por bloco.
    A integridade do ZIP (CRC) é verificada pelo zipfile ao final da leitura de cada membro."""
    desejadas = set(requeridas) | set(opcionais)
    partes, membros = [], []
    for nome, abrir in membros_csv(Path(fonte.caminho)):
        enc, sep = detectar_formato(abrir)
        fonte.codificacao, fonte.delimitador = enc, sep
        with abrir() as fh:
            cab = [c.strip().upper() for c in
                   pd.read_csv(fh, sep=sep, encoding=enc, nrows=0, encoding_errors="replace").columns]
        faltam = [c for c in requeridas if c not in cab]
        if faltam:
            raise ErroFonte(f"{nome}: colunas obrigatórias ausentes {faltam}; cabeçalho: {cab[:40]}")
        blocos = []
        try:
            with abrir() as fh:
                leitor = pd.read_csv(fh, sep=sep, encoding=enc, encoding_errors="replace", dtype=str,
                                     usecols=lambda c: c.strip().upper() in desejadas,
                                     chunksize=chunksize, keep_default_na=False, na_values=NA_TSE)
                for ch in leitor:
                    ch.columns = [c.strip().upper() for c in ch.columns]
                    fonte.linhas_lidas += len(ch)
                    if filtro is not None:
                        ch = filtro(ch)
                    fonte.linhas_filtradas += len(ch)
                    if len(ch):
                        blocos.append(ch)
        except zipfile.BadZipFile as e:
            raise ErroFonte(f"{nome}: falha de integridade (CRC) — {e}") from e
        membros.append(nome)
        if blocos:
            df = pd.concat(blocos, ignore_index=True)
            df["_ARQUIVO"] = f"{Path(fonte.caminho).name}:{nome}"
            partes.append(a_cada_arquivo(df) if a_cada_arquivo else df)
    fonte.membros_lidos = "; ".join(membros)
    LOG.info("%s: %s linhas lidas, %s mantidas após filtro", Path(fonte.caminho).name,
             f"{fonte.linhas_lidas:,}", f"{fonte.linhas_filtradas:,}")
    partes = [p for p in partes if len(p)]
    return pd.concat(partes, ignore_index=True) if partes else pd.DataFrame()


def filtro_cargo_uf(col_cargo: str | None, ufs: set[str]) -> Callable:
    def f(ch: pd.DataFrame) -> pd.DataFrame:
        m = ch["SG_UF"].str.strip().str.upper().isin(ufs)
        if col_cargo:
            m &= pd.to_numeric(ch[col_cargo], errors="coerce") == CD_CARGO_PRESIDENTE
        return ch.loc[m]
    return f


def normalizar_chave(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    df = df.copy()
    df["SG_UF"] = df["SG_UF"].astype(str).str.strip().str.upper()
    for c in KEY[1:]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    invalidas = df[KEY].isna().any(axis=1)
    df = df.loc[~invalidas].copy()
    for c in KEY[1:]:
        df[c] = df[c].astype("int64")
    return df, int(invalidas.sum())


def numeros(df: pd.DataFrame, cols: list[str]) -> None:
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").astype("float64")


def turno_de(df: pd.DataFrame, padrao: int | None) -> pd.Series:
    if "NR_TURNO" in df.columns:
        t = pd.to_numeric(df["NR_TURNO"], errors="coerce")
        if padrao is not None:
            t = t.fillna(padrao)
        return t
    return pd.Series(padrao if padrao is not None else np.nan, index=df.index, dtype="float64")


def lista_secoes(valor) -> str:
    """Normaliza uma lista de seções (ex.: DS_AGREGADAS) para '12,34'. Vazio = sem agregadas."""
    if valor is None or (isinstance(valor, float) and np.isnan(valor)) or valor is pd.NA:
        return ""
    nums = sorted({int(x) for x in re.findall(r"\d+", str(valor))})
    return ",".join(map(str, nums))


# =============================================================================
# Etapa B — Normalização por fonte
# =============================================================================
CAMPOS_DETALHE = {  # campo semântico -> nomes aceitos (primeiro presente é usado)
    "aptos": ["QT_APTOS"],
    "comparecimento": ["QT_COMPARECIMENTO"],
    "abstencoes": ["QT_ABSTENCOES"],
    "nominais": ["QT_VOTOS_NOMINAIS", "QT_VOTOS_NOMINAIS_VALIDOS"],
    "legenda": ["QT_VOTOS_LEGENDA", "QT_VOTOS_LEG_VALIDOS"],
    "brancos": ["QT_VOTOS_BRANCOS"],
    "nulos": ["QT_VOTOS_NULOS", "QT_TOTAL_VOTOS_NULOS"],
    "anulados_sep": ["QT_VOTOS_ANULADOS_APU_SEP", "QT_VOTOS_ANULADOS"],
}
CAMPOS_VALORES = list(CAMPOS_DETALHE)


def preparar_detalhe(df: pd.DataFrame, inconsist: list[pd.DataFrame]) -> tuple[dict, dict]:
    df, invalidas = normalizar_chave(df)
    if invalidas:
        LOG.warning("detalhe_votacao_secao: %d linhas com chave inválida descartadas", invalidas)
    df["turno"] = turno_de(df, None)
    df = df[df["turno"].isin([1, 2])].copy()
    df["turno"] = df["turno"].astype(int)
    mapa = {}
    for sem, opcoes in CAMPOS_DETALHE.items():
        col = next((c for c in opcoes if c in df.columns), None)
        mapa[sem] = col
        df[sem] = pd.to_numeric(df[col], errors="coerce").astype("float64") if col else np.nan
    if "NM_MUNICIPIO" not in df.columns:
        df["NM_MUNICIPIO"] = np.nan

    # Duplicidades: idênticas são removidas e registradas; divergentes são mantidas
    # (primeira ocorrência) e marcadas para classificação.
    chave_t = KEY + ["turno"]
    n0 = len(df)
    df = df.drop_duplicates(chave_t + CAMPOS_VALORES)
    if len(df) < n0:
        LOG.warning("detalhe_votacao_secao: %d duplicatas idênticas removidas", n0 - len(df))
        inconsist.append(pd.DataFrame([{
            "SG_UF": "*", "turno": None, "grupo_teste": "G1", "teste": "DUPLICIDADE_IDENTICA_REMOVIDA",
            "valor_observado": n0 - len(df), "fonte": "detalhe_votacao_secao",
            "observacao": "linhas idênticas por seção/turno/cargo; mantida uma ocorrência"}]))
    dup = df.duplicated(chave_t, keep=False)
    df["dup_divergente"] = dup
    if dup.any():
        d = df.loc[dup, KEY + ["turno", "comparecimento"]].copy()
        d["grupo_teste"], d["teste"] = "G1", "DUPLICIDADE_DIVERGENTE"
        d["valor_observado"] = d.pop("comparecimento")
        d["fonte"] = "detalhe_votacao_secao"
        d["observacao"] = "mesma seção/turno com valores diferentes no arquivo oficial"
        inconsist.append(d)
    df = df.drop_duplicates(chave_t, keep="first")
    cols = KEY + ["NM_MUNICIPIO"] + CAMPOS_VALORES + ["_ARQUIVO", "dup_divergente"]
    return {t: df.loc[df["turno"] == t, cols].reset_index(drop=True) for t in (1, 2)}, mapa


def agregar_bu(df: pd.DataFrame, turno_arquivo: int | None) -> pd.DataFrame:
    df, _ = normalizar_chave(df)
    df["turno"] = turno_de(df, turno_arquivo)
    numeros(df, ["QT_APTOS", "QT_COMPARECIMENTO", "QT_ABSTENCOES", "QT_VOTOS"])
    tipo = df["DS_TIPO_VOTAVEL"].map(sem_acento)
    df["tipo_voto"] = np.select(
        [tipo.str.startswith("nominal"), tipo.str.startswith("branco"), tipo.str.startswith("nulo"),
         tipo.str.startswith("legenda"), tipo.str.contains("anulad", na=False)],
        ["nominais", "brancos", "nulos", "legenda", "anulados_sep"], "outros")
    for c in ("DS_AGREGADAS", "DS_TIPO_URNA", "NR_URNA_EFETIVADA", "NR_LOCAL_VOTACAO"):
        if c not in df.columns:
            df[c] = np.nan
    g = df.groupby(KEY + ["turno"], sort=False)
    base = g.agg(bu_aptos=("QT_APTOS", "max"), bu_aptos_min=("QT_APTOS", "min"),
                 bu_comparecimento=("QT_COMPARECIMENTO", "max"),
                 bu_comparecimento_min=("QT_COMPARECIMENTO", "min"),
                 bu_abstencoes=("QT_ABSTENCOES", "max"),
                 bu_n_urnas=("NR_URNA_EFETIVADA", "nunique"),
                 bu_nr_urna=("NR_URNA_EFETIVADA", "first"),
                 bu_agregadas=("DS_AGREGADAS", "first"),
                 bu_tipo_urna=("DS_TIPO_URNA", "first"),
                 bu_local=("NR_LOCAL_VOTACAO", "first"),
                 bu_arquivo=("_ARQUIVO", "first"))
    votos = df.pivot_table(index=KEY + ["turno"], columns="tipo_voto", values="QT_VOTOS",
                           aggfunc="sum", fill_value=0)
    for c in ("nominais", "brancos", "nulos", "legenda", "anulados_sep", "outros"):
        if c not in votos.columns:
            votos[c] = 0.0
    votos = votos.add_prefix("bu_votos_")
    out = base.join(votos, how="left").reset_index()
    out["bu_agregadas"] = out["bu_agregadas"].map(lista_secoes)
    out["bu_local"] = pd.to_numeric(out["bu_local"], errors="coerce")
    return out


def agregar_vs(df: pd.DataFrame) -> pd.DataFrame:
    df, _ = normalizar_chave(df)
    df["turno"] = turno_de(df, None)
    numeros(df, ["QT_VOTOS", "NR_VOTAVEL"])
    df["cat"] = np.select([df["NR_VOTAVEL"] == 95, df["NR_VOTAVEL"].isin([96, 97, 98])],
                          ["brancos", "nulos_anulados"], "validos")
    dup = df.duplicated(KEY + ["turno", "NR_VOTAVEL"], keep=False)
    p = df.pivot_table(index=KEY + ["turno"], columns="cat", values="QT_VOTOS",
                       aggfunc="sum", fill_value=0)
    for c in ("validos", "brancos", "nulos_anulados"):
        if c not in p.columns:
            p[c] = 0.0
    p = p.add_prefix("vs_")
    p["vs_total"] = p[["vs_validos", "vs_brancos", "vs_nulos_anulados"]].sum(axis=1)
    p["vs_votavel_duplicado"] = dup.groupby([df[k] for k in KEY + ["turno"]]).sum()
    return p.reset_index()


def preparar_eleitorado(df: pd.DataFrame) -> pd.DataFrame:
    df, _ = normalizar_chave(df)
    if "AA_ELEICAO" in df.columns:
        aa = pd.to_numeric(df["AA_ELEICAO"], errors="coerce")
        df = df[aa.isna() | (aa == ANO)]
    df["turno"] = turno_de(df, None)
    snapshot = df["turno"].isna().all()
    df["turno"] = df["turno"].fillna(0).astype(int)
    numeros(df, ["CD_TIPO_SECAO_AGREGADA", "NR_SECAO_PRINCIPAL", "QT_ELEITOR_SECAO", "NR_LOCAL_VOTACAO"])
    for c in ("CD_TIPO_SECAO_AGREGADA", "NR_SECAO_PRINCIPAL", "QT_ELEITOR_SECAO", "NR_LOCAL_VOTACAO"):
        if c not in df.columns:
            df[c] = np.nan
    texto = pd.Series("", index=df.index, dtype=object)
    for c in ("DS_TIPO_LOCAL", "NM_LOCAL_VOTACAO", "DS_TIPO_SECAO_AGREGADA"):
        if c in df.columns:
            texto = texto + " " + df[c].fillna("").map(sem_acento)
    df["elv_transito"] = texto.str.contains("transito", na=False)
    df = df.drop_duplicates(KEY + ["turno"])

    ag = df[(df["CD_TIPO_SECAO_AGREGADA"] == 2) & df["NR_SECAO_PRINCIPAL"].notna()].copy()
    ag["principal"] = ag["NR_SECAO_PRINCIPAL"].astype("int64")
    lst = (ag.groupby(["SG_UF", "CD_MUNICIPIO", "NR_ZONA", "principal", "turno"])
             .agg(elv_agregadas=("NR_SECAO", lambda s: ",".join(map(str, sorted(s)))),
                  elv_eleitores_agregadas=("QT_ELEITOR_SECAO", "sum"))
             .reset_index().rename(columns={"principal": "NR_SECAO"}))
    out = df[KEY + ["turno", "CD_TIPO_SECAO_AGREGADA", "NR_SECAO_PRINCIPAL", "QT_ELEITOR_SECAO",
                    "NR_LOCAL_VOTACAO", "elv_transito"]].rename(columns={
        "CD_TIPO_SECAO_AGREGADA": "elv_tipo_secao", "NR_SECAO_PRINCIPAL": "elv_secao_principal",
        "QT_ELEITOR_SECAO": "elv_eleitores_secao", "NR_LOCAL_VOTACAO": "elv_local"})
    out = out.merge(lst, on=KEY + ["turno"], how="left")
    out["elv_agregadas"] = out["elv_agregadas"].fillna("")
    out["elv_eleitores_unidade"] = out["elv_eleitores_secao"] + out["elv_eleitores_agregadas"].fillna(0)
    if snapshot:  # sem NR_TURNO: o mesmo cadastro vale para os dois turnos
        out = pd.concat([out.assign(turno=1), out.assign(turno=2)], ignore_index=True)
    out["elv_snapshot"] = snapshot
    return out


def preparar_alteradas(fonte: Fonte) -> pd.DataFrame:
    """Lista oficial de seções que mudaram de local no 2º turno (esquema flexível)."""
    caminho = Path(fonte.caminho)
    for nome, abrir in membros_csv(caminho):
        enc, sep = detectar_formato(abrir)
        with abrir() as fh:
            df = pd.read_csv(fh, sep=sep, encoding=enc, dtype=str, keep_default_na=False,
                             na_values=NA_TSE, encoding_errors="replace")
        fonte.linhas_lidas += len(df)
        cols = {c: sem_acento(c).upper() for c in df.columns}
        def achar(rx):
            return next((c for c, n in cols.items() if re.search(rx, n)), None)
        mapa = {"SG_UF": achar(r"(^|_)(SG_)?UF$"), "CD_MUNICIPIO": achar(r"(CD|COD).*MUN"),
                "NR_ZONA": achar(r"ZONA"), "NR_SECAO": achar(r"SECAO(?!.*PRINC)")}
        if any(v is None for v in mapa.values()):
            raise ErroFonte(f"{nome}: colunas UF/município/zona/seção não identificadas: {list(df.columns)}")
        df = df.rename(columns={v: k for k, v in mapa.items()})[KEY]
        df, _ = normalizar_chave(df)
        fonte.linhas_filtradas += len(df)
        fonte.membros_lidos = nome
        return df.drop_duplicates().assign(mudou_local_lista_oficial=True)
    return pd.DataFrame(columns=KEY + ["mudou_local_lista_oficial"])


# =============================================================================
# Etapas B a E — Consolidação, cálculos, testes, estatística e classificação
# =============================================================================
def sufixar(df: pd.DataFrame, sfx: str) -> pd.DataFrame:
    return df.rename(columns={c: f"{c}{sfx}" for c in df.columns if c not in KEY})


def _por_turno(df: pd.DataFrame | None, t: int, sfx: str) -> pd.DataFrame | None:
    if df is None or df.empty:
        return None
    return sufixar(df[df["turno"] == t].drop(columns="turno"), sfx)


def _diferente(a: pd.Series, b: pd.Series) -> pd.Series:
    return a.notna() & b.notna() & (a != b)


def consolidar(det: dict[int, pd.DataFrame], bu: pd.DataFrame | None, vs: pd.DataFrame | None,
               elv: pd.DataFrame | None, alt: pd.DataFrame | None,
               bu_carregado: set, vs_carregado: set, p: Parametros,
               inconsist: list[pd.DataFrame]) -> pd.DataFrame:
    colunas_det = ["NM_MUNICIPIO"] + CAMPOS_VALORES + ["_ARQUIVO", "dup_divergente"]
    vazio = pd.DataFrame(columns=KEY + colunas_det)
    w = sufixar(det.get(1, vazio), "_1t").merge(sufixar(det.get(2, vazio), "_2t"),
                                               on=KEY, how="outer", indicator=True)
    w["presente_1t"] = w["_merge"].astype(str).isin(["both", "left_only"])
    w["presente_2t"] = w["_merge"].astype(str).isin(["both", "right_only"])
    w = w.drop(columns="_merge")
    w["NM_MUNICIPIO"] = w["NM_MUNICIPIO_1t"].fillna(w["NM_MUNICIPIO_2t"])
    w = w.drop(columns=["NM_MUNICIPIO_1t", "NM_MUNICIPIO_2t"])
    w = w.rename(columns={"_ARQUIVO_1t": "arquivo_origem_1t", "_ARQUIVO_2t": "arquivo_origem_2t"})
    for c in ("dup_divergente_1t", "dup_divergente_2t"):
        w[c] = w[c].astype("boolean").fillna(False).astype(bool)

    for t in (1, 2):
        s = f"_{t}t"
        w[f"validos{s}"] = w[f"nominais{s}"] + w[f"legenda{s}"].fillna(0)
        w[f"nulos_anulados{s}"] = w[f"nulos{s}"] + w[f"anulados_sep{s}"].fillna(0)
        w[f"soma_votos{s}"] = w[f"validos{s}"] + w[f"brancos{s}"] + w[f"nulos_anulados{s}"]
        apt = w[f"aptos{s}"]
        w[f"taxa{s}"] = np.where(apt > 0, 100 * w[f"comparecimento{s}"] / apt, np.nan)
        for extra in (_por_turno(bu, t, s), _por_turno(vs, t, s), _por_turno(elv, t, s)):
            if extra is not None:
                w = w.merge(extra, on=KEY, how="left")

    # ---- Etapa C — cálculos ----------------------------------------------------
    c1, c2 = w["comparecimento_1t"], w["comparecimento_2t"]
    w["delta_comparecimento"] = c2 - c1
    w["comparecimento_1t_zero"] = c1 == 0
    w["variacao_pct"] = np.where(c1 > 0, 100 * (c2 - c1) / c1, np.nan)
    w["delta_taxa_pp"] = w["taxa_2t"] - w["taxa_1t"]
    w["delta_aptos"] = w["aptos_2t"] - w["aptos_1t"]
    w["delta_abstencoes"] = w["abstencoes_2t"] - w["abstencoes_1t"]

    # ---- Etapa D, Grupo 1 — consistência matemática ------------------------------
    def reg(mask, turno, grupo, teste, obs_val, esp_val, fonte, nota):
        mask = mask.fillna(False).astype(bool)
        if not mask.any():
            return
        d = w.loc[mask, KEY].copy()
        d["turno"], d["grupo_teste"], d["teste"] = turno, grupo, teste
        for nome, v in (("valor_observado", obs_val), ("valor_esperado", esp_val)):
            d[nome] = np.nan if v is None else (v if np.isscalar(v) else np.asarray(v, dtype="float64")[mask.values])
        d["diferenca"] = d["valor_observado"] - d["valor_esperado"]
        d["fonte"], d["observacao"] = fonte, nota
        inconsist.append(d)

    for t in (1, 2):
        s = f"_{t}t"
        pres = w[f"presente{s}"]
        apt, comp, abst = w[f"aptos{s}"], w[f"comparecimento{s}"], w[f"abstencoes{s}"]
        ausente = pd.Series(False, index=w.index)
        g1 = w[f"dup_divergente{s}"].copy()
        for campo in ("aptos", "comparecimento", "abstencoes", "nominais", "brancos", "nulos"):
            v = w[f"{campo}{s}"]
            m_aus = pres & (v.isna() | v.isin(SENTINELAS))
            if campo in ("aptos", "comparecimento", "abstencoes"):
                ausente |= m_aus
                reg(m_aus, t, "G1-definição", f"VALOR_AUSENTE_OU_SENTINELA_{campo.upper()}", v, None,
                    "detalhe_votacao_secao", "#NULO#/#NE# (-1/-3) ou vazio: não tratado como negativo")
            m_neg = pres & (v < 0) & ~v.isin(SENTINELAS)
            g1 |= m_neg
            reg(m_neg, t, "G1", f"VALOR_NEGATIVO_{campo.upper()}", v, 0, "detalhe_votacao_secao", "")
        m = pres & (comp > apt)
        g1 |= m
        reg(m, t, "G1", "COMPARECIMENTO_MAIOR_QUE_APTOS", comp, apt, "detalhe_votacao_secao", "")
        m = pres & _diferente(apt, comp + abst)
        g1 |= m
        reg(m, t, "G1", "IDENTIDADE_APTOS=COMPARECIMENTO+ABSTENCOES", comp + abst, apt,
            "detalhe_votacao_secao", "")
        m = pres & _diferente(comp, w[f"soma_votos{s}"])
        g1 |= m
        reg(m, t, "G1", "IDENTIDADE_COMPARECIMENTO=VALIDOS+BRANCOS+NULOS+ANULADOS", w[f"soma_votos{s}"],
            comp, "detalhe_votacao_secao", "mesmo cargo (Presidente); votos de outros cargos não somados")
        w[f"g1_falha{s}"] = g1.fillna(False).astype(bool)
        w[f"valor_ausente{s}"] = ausente.fillna(False).astype(bool)

        # ---- Conferência com boletim de urna (Etapa E) ----
        ufs_bu = {u for (u, tt) in bu_carregado if tt == t}
        if f"bu_aptos{s}" in w.columns:
            div = pd.Series(False, index=w.index)
            pares = (("aptos", "bu_aptos"), ("comparecimento", "bu_comparecimento"),
                     ("abstencoes", "bu_abstencoes"))
            for campo, col_bu in pares:
                m = pres & _diferente(w[f"{campo}{s}"], w[f"{col_bu}{s}"])
                div |= m
                reg(m, t, "Fontes", f"DETALHE_X_BU_{campo.upper()}", w[f"{campo}{s}"],
                    w[f"{col_bu}{s}"], "detalhe_votacao_secao x bweb", "")
            bu_validos = w[f"bu_votos_nominais{s}"] + w[f"bu_votos_legenda{s}"]
            bu_nul = w[f"bu_votos_nulos{s}"] + w[f"bu_votos_anulados_sep{s}"]
            for nome, det_v, bu_v in (("VALIDOS", w[f"validos{s}"], bu_validos),
                                      ("BRANCOS", w[f"brancos{s}"], w[f"bu_votos_brancos{s}"]),
                                      ("NULOS_ANULADOS", w[f"nulos_anulados{s}"], bu_nul)):
                m = pres & _diferente(det_v, bu_v)
                div |= m
                reg(m, t, "Fontes", f"DETALHE_X_BU_{nome}", det_v, bu_v, "detalhe_votacao_secao x bweb", "")
            bu_soma = bu_validos + w[f"bu_votos_brancos{s}"] + bu_nul + w[f"bu_votos_outros{s}"]
            m_int = pres & (_diferente(w[f"bu_comparecimento{s}"], bu_soma)
                            | _diferente(w[f"bu_aptos{s}"], w[f"bu_aptos_min{s}"])
                            | _diferente(w[f"bu_comparecimento{s}"], w[f"bu_comparecimento_min{s}"]))
            div |= m_int
            reg(m_int, t, "G1", "BU_INCOERENTE_INTERNAMENTE", w[f"bu_comparecimento{s}"], bu_soma, "bweb",
                "comparecimento do BU difere da soma de votos do cargo ou aptos/comparecimento variam no BU")
            multiplo = w[f"bu_n_urnas{s}"] > 1
            sem_bu = w[f"bu_aptos{s}"].isna()
        else:
            div = multiplo = pd.Series(False, index=w.index)
            sem_bu = pd.Series(True, index=w.index)
        carregado = w["SG_UF"].isin(ufs_bu)
        w[f"bu_status{s}"] = np.select(
            [~pres, ~carregado, sem_bu, multiplo, div],
            ["NAO_SE_APLICA", "BU_NAO_CARREGADO", "SECAO_SEM_BU", "BU_MULTIPLO", "DIVERGE"], "CONFERE")
        w[f"div_bu{s}"] = (w[f"bu_status{s}"] == "DIVERGE")
        reg(pres & carregado & sem_bu, t, "Fontes", "SECAO_SEM_BOLETIM_DE_URNA", None, None, "bweb",
            "seção com resultado no detalhe e sem BU no arquivo carregado")

        # ---- Conferência com votação por seção ----
        ufs_vs = {u for (u, tt) in vs_carregado if tt == t}
        div_vs = pd.Series(False, index=w.index)
        if f"vs_total{s}" in w.columns:
            for nome, det_v, vs_v in (("VALIDOS", w[f"validos{s}"], w[f"vs_validos{s}"]),
                                      ("BRANCOS", w[f"brancos{s}"], w[f"vs_brancos{s}"]),
                                      ("NULOS_ANULADOS", w[f"nulos_anulados{s}"], w[f"vs_nulos_anulados{s}"])):
                m = pres & _diferente(det_v, vs_v)
                div_vs |= m
                reg(m, t, "Fontes", f"DETALHE_X_VOTACAO_SECAO_{nome}", det_v, vs_v,
                    "detalhe_votacao_secao x votacao_secao", "")
            m = pres & (w[f"vs_votavel_duplicado{s}"] > 0)
            div_vs |= m
            reg(m, t, "G1", "VOTACAO_SECAO_VOTAVEL_DUPLICADO", w[f"vs_votavel_duplicado{s}"], 0,
                "votacao_secao", "mesmo votável repetido na seção")
            reg(pres & w["SG_UF"].isin(ufs_vs) & w[f"vs_total{s}"].isna(), t, "Fontes",
                "SECAO_AUSENTE_EM_VOTACAO_SECAO", None, None, "votacao_secao", "")
        w[f"div_vs{s}"] = div_vs.fillna(False).astype(bool)

    # Registros de BU sem correspondente no detalhe.
    if bu is not None and not bu.empty:
        for t in (1, 2):
            chaves = w.loc[w[f"presente_{t}t"], KEY]
            orf = bu[bu["turno"] == t][KEY].merge(chaves, on=KEY, how="left", indicator=True)
            orf = orf[orf["_merge"] == "left_only"].drop(columns="_merge")
            if len(orf):
                orf["turno"], orf["grupo_teste"], orf["teste"] = t, "Fontes", "BU_SEM_REGISTRO_NO_DETALHE"
                orf["fonte"], orf["observacao"] = "bweb x detalhe_votacao_secao", ""
                inconsist.append(orf)

    # ---- Correspondência entre turnos -------------------------------------------
    def col(nome):
        return w[nome] if nome in w.columns else pd.Series(np.nan, index=w.index, dtype="object")

    bu_ag1, bu_ag2 = col("bu_agregadas_1t"), col("bu_agregadas_2t")
    alt_bu = bu_ag1.notna() & bu_ag2.notna() & (bu_ag1 != bu_ag2)
    elv_por_turno = elv is not None and not elv.empty and not bool(elv["elv_snapshot"].iloc[0])
    el1, el2 = col("elv_agregadas_1t"), col("elv_agregadas_2t")
    alt_elv = (el1.notna() & el2.notna() & (el1 != el2)) if elv_por_turno else pd.Series(False, index=w.index)
    w["agregacao_alterada"] = (alt_bu | alt_elv).astype(bool)
    w["fonte_agregacao"] = np.select([alt_bu, alt_elv, bu_ag1.notna() | bu_ag2.notna(), el1.notna()],
                                     ["bweb", "eleitorado_local_votacao", "bweb", "eleitorado_local_votacao"],
                                     "indisponível")
    w["agregadas_1t"] = bu_ag1.where(bu_ag1.notna(), el1)
    w["agregadas_2t"] = bu_ag2.where(bu_ag2.notna(), el2)
    w["possui_agregadas"] = (w["agregadas_1t"].fillna("") != "") | (w["agregadas_2t"].fillna("") != "")

    # Seções agregadas em um turno (aparecem dentro da lista de outra seção).
    agregadas_em = {}
    for t in (1, 2):
        conj = set()
        for c in (f"bu_agregadas_{t}t", f"elv_agregadas_{t}t"):
            if c in w.columns:
                for (uf, mun, zona, lst) in w.loc[w[c].fillna("") != "", KEY[:3] + [c]].itertuples(index=False):
                    conj.update((uf, mun, zona, int(x)) for x in lst.split(","))
        if elv_por_turno:  # cadastro sem NR_TURNO não diz em qual turno a seção foi agregada
            e = elv[(elv["turno"] == t) & (elv["elv_tipo_secao"] == 2)]
            conj.update(map(tuple, e[KEY].itertuples(index=False, name=None)))
        agregadas_em[t] = conj
    chaves = list(w[KEY].itertuples(index=False, name=None))
    w["agregada_no_1t"] = [k in agregadas_em[1] for k in chaves]
    w["agregada_no_2t"] = [k in agregadas_em[2] for k in chaves]

    w["secao_transito"] = (col("elv_transito_1t").fillna(False).astype(bool)
                           | col("elv_transito_2t").fillna(False).astype(bool))
    loc1 = col("bu_local_1t").where(col("bu_local_1t").notna(), col("elv_local_1t"))
    loc2 = col("bu_local_2t").where(col("bu_local_2t").notna(), col("elv_local_2t"))
    w["mudou_local_2t"] = _diferente(pd.to_numeric(loc1, errors="coerce"), pd.to_numeric(loc2, errors="coerce"))
    if alt is not None and not alt.empty:
        w = w.merge(alt, on=KEY, how="left")
        w["mudou_local_2t"] |= w["mudou_local_lista_oficial"].fillna(False).astype(bool)
    else:
        w["mudou_local_lista_oficial"] = np.nan

    tol = np.maximum(p.tol_aptos_abs, p.tol_aptos_rel * w["aptos_1t"].fillna(0))
    w["situacao_correspondencia"] = np.select(
        [~w["presente_1t"], ~w["presente_2t"],
         w["dup_divergente_1t"] | w["dup_divergente_2t"],
         w["agregacao_alterada"],
         ~(w["aptos_1t"] > 0) | ~(w["aptos_2t"] > 0),
         w["comparecimento_1t"].isna() | w["comparecimento_2t"].isna()
         | w["valor_ausente_1t"] | w["valor_ausente_2t"],
         w["delta_aptos"].abs() > tol,
         w["comparecimento_1t_zero"],
         (w["delta_aptos"] != 0) | w["mudou_local_2t"] | w["secao_transito"]],
        ["SOMENTE_2T", "SOMENTE_1T", "DUPLICIDADE_DIVERGENTE", "ALTERACAO_AGREGACAO",
         "APTOS_ZERO_OU_AUSENTE", "VALOR_AUSENTE_OU_SENTINELA", "VARIACAO_APTOS_ACIMA_TOLERANCIA",
         "COMPARECIMENTO_1T_ZERO", "COMPARAVEL_COM_RESSALVA"], "COMPARAVEL")

    w = w.copy()  # desfragmenta após os merges
    estatistica_grupos(w, p)
    classificar(w)
    return w


def _z_robusto(x: pd.Series, grupo: pd.Series) -> tuple[pd.Series, ...]:
    g = x.groupby(grupo)
    med = g.transform("median")
    absdev = (x - med).abs()
    mad = absdev.groupby(grupo).transform("median")
    meanad = absdev.groupby(grupo).transform("mean")
    z = pd.Series(np.nan, index=x.index)
    ok = mad > 0
    z[ok] = 0.6745 * (x[ok] - med[ok]) / mad[ok]
    alt = ~ok & (meanad > 0)  # MAD = 0: usa desvio absoluto médio (IBM SPSS / Iglewicz-Hoaglin)
    z[alt] = (x[alt] - med[alt]) / (1.253314 * meanad[alt])
    q = g.quantile([0.25, 0.75]).unstack()
    q1 = grupo.map(q[0.25]) if len(q) else pd.Series(np.nan, index=x.index)
    q3 = grupo.map(q[0.75]) if len(q) else pd.Series(np.nan, index=x.index)
    n = g.transform("size")
    return med, mad, z, q1, q3, n


def estatistica_grupos(w: pd.DataFrame, p: Parametros) -> None:
    """Etapa D, Grupo 2. Referência: seções comparáveis e sem falha G1 do mesmo município;
    se o município tiver menos de `min_pares` seções, a mesma UF e faixa de tamanho."""
    pares = w["situacao_correspondencia"].isin(SITUACOES_COMPARAVEIS) & ~w["g1_falha_1t"] & ~w["g1_falha_2t"]
    w["incluida_estatistica"] = pares
    cols = ["faixa_aptos", "grupo_referencia", "n_grupo", "mediana_grupo_pp", "mad_grupo_pp",
            "desvio_mediana_grupo_pp", "z_robusto_grupo", "limite_iqr_grupo_pp",
            "z_robusto_nacional", "S1_filtro_exploratorio", "S2_iqr_grupo", "S3_z_grupo", "atipica"]
    for c in cols:
        w[c] = np.nan
    w["grupo_referencia"] = pd.Series(None, index=w.index, dtype=object)
    for c in ("S1_filtro_exploratorio", "S2_iqr_grupo", "S3_z_grupo", "atipica"):
        w[c] = False
    if pares.sum() == 0:
        return
    x = w.loc[pares, "delta_taxa_pp"]
    faixa = pd.qcut(w.loc[pares, "aptos_1t"], p.n_faixas_aptos, labels=False, duplicates="drop") + 1
    w.loc[pares, "faixa_aptos"] = faixa
    mun = w.loc[pares, "SG_UF"] + "-" + w.loc[pares, "CD_MUNICIPIO"].astype(str)
    n_mun = mun.map(mun.value_counts())
    grupo = np.where(n_mun >= p.min_pares, "MUN:" + mun,
                     "UF_FAIXA:" + w.loc[pares, "SG_UF"] + "-F" + faixa.astype(int).astype(str))
    grupo = pd.Series(grupo, index=x.index)
    med, mad, z, q1, q3, n = _z_robusto(x, grupo)
    _, _, zn, _, _, _ = _z_robusto(x, pd.Series("BR", index=x.index))
    w.loc[pares, "grupo_referencia"] = grupo
    w.loc[pares, "n_grupo"] = n
    w.loc[pares, "mediana_grupo_pp"] = med
    w.loc[pares, "mad_grupo_pp"] = mad
    w.loc[pares, "desvio_mediana_grupo_pp"] = x - med
    w.loc[pares, "z_robusto_grupo"] = z
    w.loc[pares, "limite_iqr_grupo_pp"] = q3 + p.iqr_k * (q3 - q1)
    w.loc[pares, "z_robusto_nacional"] = zn
    s1 = pares & (w["variacao_pct"] > p.limiar_pct) & (w["delta_comparecimento"] > p.limiar_abs)
    s2 = pares & (w["delta_taxa_pp"] > w["limite_iqr_grupo_pp"])
    s3 = pares & (w["z_robusto_grupo"] > p.z_limite)
    w["S1_filtro_exploratorio"], w["S2_iqr_grupo"], w["S3_z_grupo"] = s1, s2, s3
    # Nenhum indicador isolado basta: exige magnitude (S1) e desvio frente aos pares (S2 ou S3).
    w["atipica"] = s1 & (s2 | s3)


def classificar(w: pd.DataFrame) -> None:
    bu_ok = {t: w[f"bu_status_{t}t"].isin(["CONFERE", "DIVERGE"]) for t in (1, 2)}
    div_bu = w["div_bu_1t"] | w["div_bu_2t"]
    div_vs = w["div_vs_1t"] | w["div_vs_2t"]
    dup = w["dup_divergente_1t"] | w["dup_divergente_2t"]
    g1_conf = (w["g1_falha_1t"] & bu_ok[1]) | (w["g1_falha_2t"] & bu_ok[2])
    g1_nao_conf = (w["g1_falha_1t"] & ~bu_ok[1]) | (w["g1_falha_2t"] & ~bu_ok[2])
    sit = w["situacao_correspondencia"]
    comparavel = sit.isin(SITUACOES_COMPARAVEIS)
    explic_agreg = (sit == "ALTERACAO_AGREGACAO") \
        | ((sit == "SOMENTE_1T") & w["agregada_no_2t"]) | ((sit == "SOMENTE_2T") & w["agregada_no_1t"])
    explic_transito = (sit == "VARIACAO_APTOS_ACIMA_TOLERANCIA") & w["secao_transito"]
    bu_conferido = (w["bu_status_1t"] == "CONFERE") & (w["bu_status_2t"] == "CONFERE")
    sem_bu_secao = (w["bu_status_1t"].isin(["SECAO_SEM_BU", "BU_MULTIPLO"])
                    | w["bu_status_2t"].isin(["SECAO_SEM_BU", "BU_MULTIPLO"]))
    ausente = w["valor_ausente_1t"] | w["valor_ausente_2t"]

    c4 = div_bu | div_vs | dup | g1_conf
    c3 = ~c4 & (explic_agreg | explic_transito)
    c5 = ~c4 & ~c3 & (~comparavel | g1_nao_conf | ausente | sem_bu_secao | (w["atipica"] & ~bu_conferido))
    c2 = ~c4 & ~c3 & ~c5 & w["atipica"]
    w["classificacao"] = np.select([c4, c3, c5, c2], ["C4", "C3", "C5", "C2"], "C1")
    w["classificacao_descricao"] = w["classificacao"].map(CLASSES)

    motivos = [
        (div_bu, "divergência detalhe x boletim de urna"),
        (div_vs, "divergência detalhe x votação por seção"),
        (dup, "duplicidade divergente no arquivo oficial"),
        (g1_conf, "identidade matemática falha no registro oficial (BU disponível)"),
        (explic_agreg & ~c4, "variação explicada por alteração/agregação de seções (registro oficial)"),
        (explic_transito & ~c4, "variação de aptos em seção de voto em trânsito (registro oficial)"),
        (~comparavel & ~explic_agreg & ~explic_transito, "não comparável: " + sit.astype(str)),
        (g1_nao_conf, "falha matemática sem BU para confirmar"),
        (ausente, "valor ausente ou código #NULO#/#NE#"),
        (sem_bu_secao, "seção sem BU único no arquivo carregado"),
        (w["atipica"] & ~bu_conferido, "aumento atípico sem conferência completa no BU"),
        (w["atipica"] & bu_conferido, "aumento atípico; BU confere com o detalhe"),
    ]
    txt = pd.Series("", index=w.index, dtype=object)
    for m, frase in motivos:
        m = m.fillna(False).astype(bool)
        novo = frase[m] if isinstance(frase, pd.Series) else frase
        txt[m] = np.where(txt[m] == "", novo, txt[m] + "; " + novo)
    vazio = txt == ""
    txt[vazio] = np.where(bu_conferido[vazio], "sem divergências; BU confere",
                          "sem divergências nas fontes carregadas (BU não conferido)")
    w["motivo_classificacao"] = txt
    w["bu_conferido"] = bu_conferido
    w["conclusao_validacao"] = w["classificacao"].map({
        "C1": "Conferida sem divergência", "C2": "Conferida — variação atípica sem inconsistência",
        "C3": "Diferença explicada", "C4": "Inconsistência documental confirmada",
        "C5": "Inconclusiva / pendente"})


# =============================================================================
# Resumos
# =============================================================================
def avaliar_escopo(det: dict, bu_carregado: set, vs_carregado: set, ufs: list[str]) -> dict:
    ufs_det = {t: set(det[t]["SG_UF"].unique()) if t in det else set() for t in (1, 2)}
    lacunas = []
    for u in UFS_BRASIL:
        faltas = []
        if u not in ufs:
            faltas.append("fora do escopo solicitado")
        else:
            for t in (1, 2):
                if u not in ufs_det[t]:
                    faltas.append(f"detalhe {t}T")
                if (u, t) not in bu_carregado:
                    faltas.append(f"BU {t}T")
                if (u, t) not in vs_carregado:
                    faltas.append(f"votacao_secao {t}T")
        if faltas:
            lacunas.append({"UF": u, "faltando": ", ".join(faltas)})
    criticas = [l for l in lacunas if re.search(r"detalhe|BU|fora", l["faltando"])]
    if not ufs_det[1] and not ufs_det[2]:
        status = "NÃO EXECUTADA"
    elif not ufs_det[1] or not ufs_det[2]:
        status = "NÃO EXECUTADA (um dos turnos ausente)"
    elif criticas:
        status = "PARCIAL"
    else:
        status = "COMPLETA"
    return {"status": status, "lacunas": lacunas, "ufs_detalhe_1t": sorted(ufs_det[1]),
            "ufs_detalhe_2t": sorted(ufs_det[2])}


def _pct(a, b):
    return 100 * a / b if b else np.nan


def distribuicao(x: pd.Series) -> dict:
    x = x.dropna()
    if x.empty:
        return {}
    q = x.quantile([0.001, 0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99, 0.999])
    return {"n": len(x), "média": x.mean(), "desvio padrão": x.std(), "mínimo": x.min(),
            "p0,1": q[0.001], "p1": q[0.01], "p5": q[0.05], "p25": q[0.25], "mediana": q[0.5],
            "p75": q[0.75], "p95": q[0.95], "p99": q[0.99], "p99,9": q[0.999], "máximo": x.max(),
            "% com aumento": 100 * (x > 0).mean()}


def resumo_nacional(w: pd.DataFrame, inc: pd.DataFrame, escopo: dict, p: Parametros) -> pd.DataFrame:
    linhas = [("Status do escopo", escopo["status"], "COMPLETA exige detalhe e BU dos 2 turnos nas 27 UFs")]
    if w.empty:
        return pd.DataFrame(linhas, columns=["Indicador", "Valor", "Observação"])
    comp = w["situacao_correspondencia"].isin(SITUACOES_COMPARAVEIS)
    est = w["incluida_estatistica"].astype(bool)
    linhas += [
        ("UFs com detalhe 1º turno", len(escopo["ufs_detalhe_1t"]), ", ".join(escopo["ufs_detalhe_1t"])),
        ("UFs com detalhe 2º turno", len(escopo["ufs_detalhe_2t"]), ", ".join(escopo["ufs_detalhe_2t"])),
        ("Seções com registro no 1º turno", int(w["presente_1t"].sum()), "detalhe_votacao_secao, cargo Presidente"),
        ("Seções com registro no 2º turno", int(w["presente_2t"].sum()), ""),
        ("Seções presentes nos dois turnos", int((w["presente_1t"] & w["presente_2t"]).sum()), "chave UF+município+zona+seção"),
        ("Seções comparáveis", int(comp.sum()), "COMPARAVEL + COMPARAVEL_COM_RESSALVA"),
        ("  das quais com ressalva", int((w["situacao_correspondencia"] == "COMPARAVEL_COM_RESSALVA").sum()),
         "variação de aptos dentro da tolerância, mudança de local ou seção de trânsito"),
        ("Seções usadas na estatística (comparáveis sem falha G1)", int(est.sum()), ""),
        ("Seções não comparáveis", int((~comp).sum()), "ver aba Seções Não Comparáveis"),
    ]
    for sit, n in w.loc[~comp, "situacao_correspondencia"].value_counts().items():
        linhas.append((f"  não comparável — {sit}", int(n), ""))
    for t in (1, 2):
        s = f"_{t}t"
        m = w[f"presente{s}"]
        linhas.append((f"Aptos {t}º turno (soma)", float(w.loc[m, f"aptos{s}"].sum()), ""))
        linhas.append((f"Comparecimento {t}º turno (soma)", float(w.loc[m, f"comparecimento{s}"].sum()), ""))
        linhas.append((f"Taxa de comparecimento {t}º turno (%)",
                       _pct(w.loc[m, f"comparecimento{s}"].sum(), w.loc[m, f"aptos{s}"].sum()), "todas as seções do turno"))
    linhas.append(("Taxa 1º turno nas seções comparáveis (%)",
                   _pct(w.loc[comp, "comparecimento_1t"].sum(), w.loc[comp, "aptos_1t"].sum()), ""))
    linhas.append(("Taxa 2º turno nas seções comparáveis (%)",
                   _pct(w.loc[comp, "comparecimento_2t"].sum(), w.loc[comp, "aptos_2t"].sum()), ""))
    for k, v in distribuicao(w.loc[est, "delta_taxa_pp"]).items():
        linhas.append((f"Δ taxa (p.p.) — {k}", v, "seções usadas na estatística"))
    linhas += [
        (f"S1: variação > {p.limiar_pct:g}% e Δ > {p.limiar_abs:g} eleitores", int(w["S1_filtro_exploratorio"].sum()), "filtro exploratório"),
        (f"S2: Δ taxa acima de Q3 + {p.iqr_k:g}·IQR do grupo", int(w["S2_iqr_grupo"].sum()), ""),
        (f"S3: z robusto do grupo > {p.z_limite:g}", int(w["S3_z_grupo"].sum()), ""),
        ("Aumentos atípicos (S1 e (S2 ou S3))", int(w["atipica"].sum()), "critério combinado"),
        ("Comparecimento 1º turno = 0 (sinalizado à parte)", int(w["comparecimento_1t_zero"].sum()), ""),
        ("Falha G1 (consistência matemática) em algum turno", int((w["g1_falha_1t"] | w["g1_falha_2t"]).sum()), ""),
        ("Divergência detalhe x BU", int((w["div_bu_1t"] | w["div_bu_2t"]).sum()), ""),
        ("Divergência detalhe x votação por seção", int((w["div_vs_1t"] | w["div_vs_2t"]).sum()), ""),
        ("Seções com BU conferido nos 2 turnos", int(w["bu_conferido"].sum()), ""),
    ]
    for c, desc in CLASSES.items():
        linhas.append((f"{c} — {desc}", int((w["classificacao"] == c).sum()), ""))
    if not inc.empty:
        for (g, t), n in inc.groupby(["grupo_teste", "teste"]).size().items():
            linhas.append((f"Teste falho [{g}] {t}", int(n), "linhas na aba Inconsistências"))
    return pd.DataFrame(linhas, columns=["Indicador", "Valor", "Observação"])


def resumo_uf(w: pd.DataFrame) -> pd.DataFrame:
    if w.empty:
        return pd.DataFrame()
    linhas = []
    for uf, g in w.groupby("SG_UF"):
        comp = g["situacao_correspondencia"].isin(SITUACOES_COMPARAVEIS)
        est = g["incluida_estatistica"].astype(bool)
        d = distribuicao(g.loc[est, "delta_taxa_pp"])
        linha = {
            "UF": uf, "seções 1T": int(g["presente_1t"].sum()), "seções 2T": int(g["presente_2t"].sum()),
            "comparáveis": int(comp.sum()), "não comparáveis": int((~comp).sum()),
            "aptos 1T": g["aptos_1t"].sum(), "aptos 2T": g["aptos_2t"].sum(),
            "comparecimento 1T": g["comparecimento_1t"].sum(), "comparecimento 2T": g["comparecimento_2t"].sum(),
            "taxa 1T (%)": _pct(g["comparecimento_1t"].sum(), g["aptos_1t"].sum()),
            "taxa 2T (%)": _pct(g["comparecimento_2t"].sum(), g["aptos_2t"].sum()),
            "Δ taxa mediana (p.p.)": d.get("mediana"), "Δ taxa p1": d.get("p1"), "Δ taxa p5": d.get("p5"),
            "Δ taxa p95": d.get("p95"), "Δ taxa p99": d.get("p99"),
            "IQR Δ taxa": (d.get("p75") - d.get("p25")) if d else np.nan,
            "S1": int(g["S1_filtro_exploratorio"].sum()), "atípicas": int(g["atipica"].sum()),
            "% atípicas (comparáveis)": _pct(g["atipica"].sum(), est.sum()),
            "falha G1": int((g["g1_falha_1t"] | g["g1_falha_2t"]).sum()),
            "div. BU": int((g["div_bu_1t"] | g["div_bu_2t"]).sum()),
            "BU conferido": int(g["bu_conferido"].sum()),
        }
        for c in CLASSES:
            linha[c] = int((g["classificacao"] == c).sum())
        linhas.append(linha)
    return pd.DataFrame(linhas)


COLS_SECAO = [
    *KEY, "NM_MUNICIPIO", "situacao_correspondencia", "classificacao", "classificacao_descricao",
    "motivo_classificacao", "aptos_1t", "aptos_2t", "delta_aptos", "comparecimento_1t", "comparecimento_2t",
    "delta_comparecimento", "variacao_pct", "taxa_1t", "taxa_2t", "delta_taxa_pp", "abstencoes_1t",
    "abstencoes_2t", "delta_abstencoes", "validos_1t", "brancos_1t", "nulos_1t", "anulados_sep_1t",
    "validos_2t", "brancos_2t", "nulos_2t", "anulados_sep_2t", "faixa_aptos", "grupo_referencia", "n_grupo",
    "mediana_grupo_pp", "mad_grupo_pp", "desvio_mediana_grupo_pp", "z_robusto_grupo", "limite_iqr_grupo_pp",
    "z_robusto_nacional", "S1_filtro_exploratorio", "S2_iqr_grupo", "S3_z_grupo", "atipica",
    "comparecimento_1t_zero", "possui_agregadas", "agregadas_1t", "agregadas_2t", "agregacao_alterada",
    "fonte_agregacao", "mudou_local_2t", "secao_transito", "g1_falha_1t", "g1_falha_2t",
    "bu_status_1t", "bu_status_2t", "bu_conferido", "arquivo_origem_1t", "arquivo_origem_2t",
]

COLS_VALIDACAO = [
    *KEY, "NM_MUNICIPIO", "classificacao", "conclusao_validacao", "motivo_classificacao", "atipica",
    "aptos_1t", "bu_aptos_1t", "comparecimento_1t", "bu_comparecimento_1t", "abstencoes_1t", "bu_abstencoes_1t",
    "validos_1t", "bu_votos_nominais_1t", "brancos_1t", "bu_votos_brancos_1t", "nulos_anulados_1t",
    "bu_votos_nulos_1t", "bu_status_1t", "bu_agregadas_1t", "bu_tipo_urna_1t", "bu_nr_urna_1t", "bu_arquivo_1t",
    "aptos_2t", "bu_aptos_2t", "comparecimento_2t", "bu_comparecimento_2t", "abstencoes_2t", "bu_abstencoes_2t",
    "validos_2t", "bu_votos_nominais_2t", "brancos_2t", "bu_votos_brancos_2t", "nulos_anulados_2t",
    "bu_votos_nulos_2t", "bu_status_2t", "bu_agregadas_2t", "bu_tipo_urna_2t", "bu_nr_urna_2t", "bu_arquivo_2t",
    "agregacao_alterada", "delta_aptos", "secao_transito", "mudou_local_2t",
]


def selecionar(w: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    return w[[c for c in cols if c in w.columns]]


def texto_metodologia(p: Parametros, mapa_campos: dict) -> list[tuple[str, str]]:
    return [
        ("Unidade de análise", "Seção eleitoral; chave UF + código do município (TSE) + zona + seção."),
        ("Cargo", "Presidente da República (CD_CARGO = 1 / CD_CARGO_PERGUNTA = 1). Nenhum voto de outro cargo é somado."),
        ("Comparecimento", "QT_COMPARECIMENTO do arquivo detalhe_votacao_secao. Nunca derivado de votos de candidatos."),
        ("Mapeamento de colunas (detalhe)", "; ".join(f"{k} <- {v or 'AUSENTE'}" for k, v in mapa_campos.items())),
        ("Códigos #NULO#/#NE#", "Tratados como ausentes (-1/-3 conforme LEIAME do TSE), não como negativos."),
        ("Delta", "Comparecimento_2T − Comparecimento_1T."),
        ("Variação %", "100 × Delta / Comparecimento_1T; não calculada quando Comparecimento_1T = 0 (sinalizado)."),
        ("Taxa", "100 × Comparecimento / Aptos, por turno; Δ taxa em pontos percentuais."),
        ("Correspondência entre turnos",
         "SOMENTE_1T/2T; DUPLICIDADE_DIVERGENTE; ALTERACAO_AGREGACAO (DS_AGREGADAS do BU ou eleitorado_local_votacao "
         "por turno); APTOS_ZERO_OU_AUSENTE; VALOR_AUSENTE_OU_SENTINELA; VARIACAO_APTOS_ACIMA_TOLERANCIA "
         f"(|Δ aptos| > máx({p.tol_aptos_abs:g}; {100 * p.tol_aptos_rel:g}% dos aptos 1T)); COMPARECIMENTO_1T_ZERO; "
         "COMPARAVEL_COM_RESSALVA (Δ aptos dentro da tolerância, mudança de local ou seção de trânsito); COMPARAVEL."),
        ("Grupo 1 — consistência", "Valores negativos; comparecimento > aptos; aptos ≠ comparecimento + abstenções; "
         "comparecimento ≠ válidos + brancos + nulos + anulados em separado; duplicidades; conferência com BU e "
         "com votacao_secao (válidos, brancos, nulos+anulados). As identidades seguem o LEIAME de eleições "
         "anteriores e devem ser confirmadas no LEIAME 2026."),
        ("Grupo 2 — estatística", f"Métrica principal: Δ taxa (p.p.). Grupo de referência: mesmo município se tiver "
         f"≥ {p.min_pares} seções elegíveis; senão mesma UF e faixa de tamanho (quantis nacionais de aptos 1T, "
         f"{p.n_faixas_aptos} faixas). S1: variação > {p.limiar_pct:g}% e Δ > {p.limiar_abs:g} eleitores (filtro "
         f"exploratório, não é parâmetro legal). S2: Δ taxa > Q3 + {p.iqr_k:g}·IQR do grupo. S3: z robusto "
         f"0,6745·(x − mediana)/MAD > {p.z_limite:g} (MAD = 0: desvio absoluto médio × 1,2533)."),
        ("Aumento atípico", "S1 E (S2 OU S3): exige magnitude e desvio frente aos pares; nenhum indicador isolado basta."),
        ("C1 — Consistente", "Comparável, sem falhas G1, sem divergência entre fontes e não atípica. Coluna bu_conferido "
         "indica se o BU foi efetivamente conferido."),
        ("C2 — Variação atípica", "Atípica, sem inconsistência e com BU conferido nos dois turnos."),
        ("C3 — Divergência explicada", "Alteração de agregação ou seção agregada em um turno (registro oficial), ou "
         "variação de aptos em seção de voto em trânsito identificada no cadastro oficial."),
        ("C4 — Inconsistência documental", "Divergência detalhe x BU ou detalhe x votacao_secao; duplicidade divergente; "
         "falha de identidade matemática em turno cujo BU foi carregado; BU internamente incoerente."),
        ("C5 — Verificação pendente", "Não comparável sem explicação documental, valores ausentes, falha G1 sem BU, "
         "seção sem BU único, ou atípica sem BU conferido."),
        ("Precedência", "C4 > C3 > C5 > C2 > C1."),
        ("Interpretação", "Desvio estatístico não é evidência de fraude nem de causa intencional. Correlação ≠ causalidade."),
    ]


# =============================================================================
# Saída — XLSX
# =============================================================================
LIMITE_LINHAS_XLSX = 1_048_575


def _valor_xlsx(v):
    if v is None or v is pd.NA or v is pd.NaT:
        return None
    if isinstance(v, (float, np.floating)):
        return None if not np.isfinite(v) else float(v)
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.bool_, bool)):
        return bool(v)
    return v


def escrever_xlsx(caminho: Path, abas: list[tuple[str, pd.DataFrame]]) -> None:
    import xlsxwriter

    wb = xlsxwriter.Workbook(str(caminho), {"constant_memory": True, "strings_to_urls": False,
                                            "nan_inf_to_errors": False})
    cab = wb.add_format({"bold": True, "bg_color": "#DDE4EE", "text_wrap": True, "valign": "top", "border": 1})
    dec = wb.add_format({"num_format": "0.00"})
    for nome, df in abas:
        partes = [df.iloc[i:i + LIMITE_LINHAS_XLSX] for i in range(0, max(len(df), 1), LIMITE_LINHAS_XLSX)]
        for k, parte in enumerate(partes):
            ws = wb.add_worksheet(nome if k == 0 else f"{nome[:26]} ({k + 1})")
            cols = list(parte.columns)
            for j, c in enumerate(cols):
                largura = min(max(len(str(c)) + 2, 10), 60)
                fmt = dec if parte[c].dtype.kind == "f" else None
                ws.set_column(j, j, largura, fmt)
            ws.write_row(0, 0, cols, cab)
            for i, linha in enumerate(parte.itertuples(index=False, name=None), start=1):
                ws.write_row(i, 0, [_valor_xlsx(v) for v in linha])
            if cols:
                ws.autofilter(0, 0, max(len(parte), 1), len(cols) - 1)
            ws.freeze_panes(1, 0)
    wb.close()


# =============================================================================
# Saída — PDF
# =============================================================================
def fmt_n(v, casas=0) -> str:
    if v is None or (isinstance(v, float) and not np.isfinite(v)):
        return "—"
    s = f"{v:,.{casas}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def escrever_pdf(caminho: Path, w: pd.DataFrame, inc: pd.DataFrame, fontes: list[Fonte], falhas: list[dict],
                 escopo: dict, ruf: pd.DataFrame, p: Parametros, execucao: dict) -> None:
    from reportlab.graphics.charts.barcharts import VerticalBarChart
    from reportlab.graphics.shapes import Drawing, String
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import cm
    from reportlab.platypus import (KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table,
                                    TableStyle)

    est = getSampleStyleSheet()
    corpo = ParagraphStyle("corpo", parent=est["BodyText"], fontSize=9, leading=12)
    peq = ParagraphStyle("peq", parent=corpo, fontSize=7, leading=9)
    alerta = ParagraphStyle("alerta", parent=corpo, backColor=colors.HexColor("#FDECEA"),
                            borderColor=colors.HexColor("#C62828"), borderWidth=1, borderPadding=6,
                            textColor=colors.HexColor("#7F1D1D"))
    h1, h2 = est["Heading1"], est["Heading2"]

    def glifos(txt) -> str:  # fontes base do PDF (WinAnsi) não têm Δ nem ≥
        return str(txt).replace("Δ", "Delta ").replace("≥", ">=")

    def tabela(dados, larguras=None, fonte=7):
        t = Table([[Paragraph(glifos(c), peq) for c in linha] for linha in dados], colWidths=larguras, repeatRows=1)
        t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#DDE4EE")),
                               ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                               ("FONTSIZE", (0, 0), (-1, -1), fonte), ("VALIGN", (0, 0), (-1, -1), "TOP")]))
        return t

    def barras(rotulos, valores, titulo, largura=17 * cm, altura=6 * cm):
        d = Drawing(largura, altura)
        bc = VerticalBarChart()
        bc.x, bc.y, bc.width, bc.height = 40, 35, largura - 60, altura - 60
        bc.data = [list(valores)]
        bc.categoryAxis.categoryNames = [glifos(r) for r in rotulos]
        bc.categoryAxis.labels.fontSize = 5
        bc.categoryAxis.labels.angle = 90
        bc.categoryAxis.labels.dy = -8
        bc.valueAxis.labels.fontSize = 6
        bc.valueAxis.valueMin = 0
        bc.bars[0].fillColor = colors.HexColor("#2A6FB0")
        bc.bars[0].strokeColor = None
        d.add(bc)
        d.add(String(largura / 2, altura - 12, glifos(titulo), fontSize=8, textAnchor="middle"))
        return d

    doc = SimpleDocTemplate(str(caminho), pagesize=A4, leftMargin=1.6 * cm, rightMargin=1.6 * cm,
                            topMargin=1.5 * cm, bottomMargin=1.5 * cm, title="Auditoria TSE 2026",
                            author=f"Auditoria_TSE_2026.py v{VERSAO_SCRIPT}")
    s = [Paragraph("Auditoria estatística do comparecimento por seção — Presidente, Eleições 2026 (1º x 2º turno)", h1),
         Paragraph(f"Gerado em {execucao['inicio_utc']} (UTC) por Auditoria_TSE_2026.py v{VERSAO_SCRIPT}. "
                   f"Status do escopo: <b>{escopo['status']}</b>.", corpo), Spacer(1, 6)]

    tem_dados = not w.empty
    if escopo["status"] != "COMPLETA":
        s.append(Paragraph(
            f"<b>Auditoria {escopo['status']}.</b> Os resultados abaixo cobrem apenas as fontes efetivamente "
            "processadas e não podem ser lidos como auditoria nacional concluída. Lacunas: " +
            ("; ".join(f"{l['UF']}: {l['faltando']}" for l in escopo["lacunas"][:40]) or "—") +
            (" …" if len(escopo["lacunas"]) > 40 else ""), alerta))
        s.append(Spacer(1, 8))

    # 1. Resumo executivo
    s.append(Paragraph("1. Resumo executivo", h2))
    if not tem_dados:
        s.append(Paragraph("Nenhum resultado foi calculado: a fonte obrigatória (detalhe_votacao_secao) dos dois "
                           "turnos não pôde ser obtida ou lida. As seções seguintes registram as tentativas de coleta "
                           "e as falhas; não há números eleitorais neste relatório.", corpo))
    else:
        comp = w["situacao_correspondencia"].isin(SITUACOES_COMPARAVEIS)
        e = w["incluida_estatistica"].astype(bool)
        d = distribuicao(w.loc[e, "delta_taxa_pp"])
        cls = w["classificacao"].value_counts()
        s.append(Paragraph(
            f"Foram lidas {fmt_n(w['presente_1t'].sum())} seções no 1º turno e {fmt_n(w['presente_2t'].sum())} no "
            f"2º turno (cargo Presidente). {fmt_n(comp.sum())} seções são comparáveis entre turnos e "
            f"{fmt_n(e.sum())} entraram na análise estatística. A taxa de comparecimento agregada das seções "
            f"comparáveis passou de {fmt_n(_pct(w.loc[comp, 'comparecimento_1t'].sum(), w.loc[comp, 'aptos_1t'].sum()), 2)}% "
            f"para {fmt_n(_pct(w.loc[comp, 'comparecimento_2t'].sum(), w.loc[comp, 'aptos_2t'].sum()), 2)}%; a mediana "
            f"da variação por seção foi {fmt_n(d.get('mediana'), 2)} p.p. (p1 = {fmt_n(d.get('p1'), 2)}; "
            f"p99 = {fmt_n(d.get('p99'), 2)}).", corpo))
        s.append(Paragraph(
            f"{fmt_n(w['atipica'].sum())} seções atenderam ao critério combinado de aumento atípico "
            f"(S1 e (S2 ou S3)). Classificação: " +
            "; ".join(f"{c} {CLASSES[c]}: {fmt_n(cls.get(c, 0))}" for c in CLASSES) + ".", corpo))
        s.append(Paragraph(
            "Variações estatísticas atípicas indicam necessidade de verificação, não irregularidade. Nenhuma "
            "conclusão sobre intenção, causa ou fraude é sustentada por desvio estatístico isolado.", corpo))

    # 2. Fontes
    s.append(Paragraph("2. Fontes utilizadas e tentativas de coleta", h2))
    linhas = [["Tipo", "UF", "T", "Status", "Origem / URL", "Acesso (UTC)", "SHA-256 (início)", "Linhas lidas/mantidas"]]
    for f in fontes:
        linhas.append([f.tipo, f.uf or "—", f.turno or "—", f.status + (f" — {f.erro}" if f.erro else ""),
                       f"{f.origem_url or '—'}: {f.url or f.caminho or '—'}", f.data_acesso_utc or "—",
                       (f.sha256 or "—")[:16], f"{fmt_n(f.linhas_lidas)} / {fmt_n(f.linhas_filtradas)}"])
    for fl in falhas:
        linhas.append([fl.get("etapa"), "—", "—", "FALHA — " + fl.get("erro", ""), fl.get("url"),
                       fl.get("data_acesso_utc"), "—", "—"])
    s.append(tabela(linhas, [2.2 * cm, 0.8 * cm, 0.6 * cm, 3.6 * cm, 4.6 * cm, 2.2 * cm, 1.6 * cm, 1.8 * cm], 6))
    s.append(Paragraph("Hashes completos, cabeçalhos HTTP (Last-Modified/ETag) e versão CKAN estão no manifesto "
                       "(manifesto_fontes.json) e na aba Fontes e Metodologia.", peq))

    if tem_dados:
        comp = w["situacao_correspondencia"].isin(SITUACOES_COMPARAVEIS)
        e = w["incluida_estatistica"].astype(bool)
        # 3. Quantidades
        s.append(Paragraph("3. Seções analisadas, comparáveis, excluídas e pendentes", h2))
        q = [["Indicador", "Quantidade"],
             ["Seções no 1º turno", fmt_n(w["presente_1t"].sum())], ["Seções no 2º turno", fmt_n(w["presente_2t"].sum())],
             ["Comparáveis", fmt_n(comp.sum())], ["Usadas na estatística", fmt_n(e.sum())],
             ["Não comparáveis", fmt_n((~comp).sum())]]
        q += [[f"  {k}", fmt_n(v)] for k, v in w.loc[~comp, "situacao_correspondencia"].value_counts().items()]
        q += [["Pendentes (C5)", fmt_n((w["classificacao"] == "C5").sum())]]
        s.append(tabela(q, [9 * cm, 4 * cm], 8))

        # 4. Distribuição nacional
        s.append(Paragraph("4. Distribuição nacional da variação da taxa de comparecimento", h2))
        x = w.loc[e, "delta_taxa_pp"].dropna()
        if len(x):
            bordas = np.arange(-20, 21, 1.0)
            cont = np.histogram(x.clip(-20.5, 20.5), bins=np.concatenate(([-np.inf], bordas, [np.inf])))[0]
            rot = ["<-20"] + [f"{a:g}" for a in bordas[:-1]] + ["≥20"]
            cont = list(cont[:len(bordas)]) + [int(cont[len(bordas):].sum())]
            s.append(barras(rot, cont, "Seções por faixa de Δ taxa (p.p., faixas de 1 p.p.)"))
            d = distribuicao(x)
            s.append(tabela([["Estatística", "Δ taxa (p.p.)"]] +
                            [[k, fmt_n(v, 3 if k not in ("n",) else 0)] for k, v in d.items()], [6 * cm, 4 * cm], 7))

        # 5. Por UF
        s.append(PageBreak())
        s.append(Paragraph("5. Distribuição por UF", h2))
        if not ruf.empty:
            cols = ["UF", "comparáveis", "taxa 1T (%)", "taxa 2T (%)", "Δ taxa mediana (p.p.)", "Δ taxa p99",
                    "atípicas", "% atípicas (comparáveis)", "falha G1", "div. BU", "C4", "C5"]
            dados = [cols] + [[r["UF"]] + [fmt_n(r[c], 2 if "taxa" in c or "%" in c or "Δ" in c else 0)
                                           for c in cols[1:]] for _, r in ruf.iterrows()]
            s.append(tabela(dados, None, 6))
            s.append(barras(ruf["UF"], ruf["atípicas"].fillna(0), "Seções com aumento atípico por UF", altura=5 * cm))

        # 6. Padrões
        s.append(Paragraph("6. Principais padrões estatísticos", h2))
        at = w[w["atipica"]]
        if at.empty:
            s.append(Paragraph("Nenhuma seção atendeu ao critério combinado de aumento atípico.", corpo))
        else:
            s.append(Paragraph(
                f"Das {fmt_n(len(at))} seções atípicas: {fmt_n(at['mudou_local_2t'].sum())} mudaram de local no 2º turno, "
                f"{fmt_n(at['possui_agregadas'].sum())} possuem seções agregadas, "
                f"{fmt_n((at['situacao_correspondencia'] == 'COMPARAVEL_COM_RESSALVA').sum())} são comparáveis com ressalva. "
                "Coocorrências são descritivas e não implicam causa.", corpo))
            top_mun = (at.groupby(["SG_UF", "NM_MUNICIPIO"]).size().rename("atípicas").reset_index()
                         .sort_values("atípicas", ascending=False).head(15))
            s.append(tabela([["UF", "Município", "Seções atípicas"]] +
                            top_mun.astype(str).values.tolist(), [1.5 * cm, 7 * cm, 3 * cm], 7))
            s.append(Spacer(1, 6))
            top = at.sort_values("z_robusto_grupo", ascending=False).head(30)
            cols = ["SG_UF", "NM_MUNICIPIO", "NR_ZONA", "NR_SECAO", "comparecimento_1t", "comparecimento_2t",
                    "variacao_pct", "delta_taxa_pp", "z_robusto_grupo", "classificacao"]
            s.append(Paragraph("Maiores desvios (z robusto do grupo) — até 30 seções:", corpo))
            s.append(tabela([["UF", "Município", "Zona", "Seção", "Comp. 1T", "Comp. 2T", "Var. %", "Δ p.p.", "z", "Classe"]] +
                            [[r[c] if c in ("SG_UF", "NM_MUNICIPIO", "classificacao") else
                              fmt_n(r[c], 2 if c in ("variacao_pct", "delta_taxa_pp", "z_robusto_grupo") else 0)
                              for c in cols] for _, r in top.iterrows()], None, 6))

        # 7. Inconsistências
        s.append(Paragraph("7. Inconsistências documentais verificadas", h2))
        if inc.empty:
            s.append(Paragraph("Nenhum teste de consistência falhou nas fontes carregadas.", corpo))
        else:
            cont = inc.groupby(["grupo_teste", "teste", "turno"], dropna=False).size().reset_index(name="n")
            s.append(tabela([["Grupo", "Teste", "Turno", "Ocorrências"]] +
                            [[a, b, "—" if pd.isna(c) else int(c), fmt_n(n)] for a, b, c, n in cont.values.tolist()],
                            [2 * cm, 9 * cm, 1.5 * cm, 2.5 * cm], 7))
        s.append(Paragraph(f"Seções em C4 (inconsistência documental): {fmt_n((w['classificacao'] == 'C4').sum())}. "
                           "Detalhes por seção nas abas Inconsistências Matemáticas e Validações dos Boletins.", corpo))

    # 8. Limitações
    s.append(Paragraph("8. Limitações", h2))
    lim = [
        "As identidades contábeis (aptos = comparecimento + abstenções; comparecimento = soma de votos do cargo) e o "
        "mapeamento de códigos de votáveis (95 branco; 96–98 nulo/anulado) seguem o LEIAME de eleições anteriores e "
        "devem ser confirmados no LEIAME 2026 antes de qualquer conclusão sobre os casos C4.",
        "Variação de aptos entre turnos pode decorrer de voto em trânsito, decisões judiciais e ajustes de cadastro; "
        "sem registro oficial que explique a variação, a seção é mantida como C5.",
        "A lista oficial de seções com mudança de local no 2º turno é publicada fora do CKAN; sem ela, mudanças de "
        "local só são detectadas pelo NR_LOCAL_VOTACAO do BU ou do cadastro.",
        "Os limiares de 15% e 30 eleitores são filtros exploratórios, não parâmetros legais.",
        "O grupo de referência municipal assume homogeneidade dentro do município; municípios pequenos usam UF e faixa "
        "de tamanho, o que reduz a comparabilidade.",
        "Correlação não implica causalidade; desvio estatístico não é evidência de fraude.",
    ]
    if escopo["status"] != "COMPLETA":
        lim.insert(0, f"Escopo {escopo['status']}: ver lacunas no início do relatório.")
    for l in lim:
        s.append(Paragraph("• " + l, corpo))

    # 9. Conclusões
    s.append(Paragraph("9. Conclusões sustentadas pelos dados", h2))
    if not tem_dados:
        s.append(Paragraph("Não há conclusões: nenhum dado oficial foi processado nesta execução.", corpo))
    else:
        cls = w["classificacao"].value_counts()
        conc = [
            f"{fmt_n(cls.get('C1', 0))} seções não apresentaram divergência nas fontes carregadas "
            f"({fmt_n(w['bu_conferido'].sum())} com BU conferido nos dois turnos).",
            f"{fmt_n(cls.get('C2', 0))} seções têm aumento atípico de comparecimento sem inconsistência matemática "
            "e com BU conferido; recomenda-se verificação administrativa (cadernos, atas, transferências).",
            f"{fmt_n(cls.get('C3', 0))} diferenças foram explicadas por registros administrativos oficiais.",
            f"{fmt_n(cls.get('C4', 0))} seções apresentam inconsistência documental entre fontes oficiais ou dentro "
            "do registro oficial; exigem conferência no LEIAME 2026 e junto ao TSE.",
            f"{fmt_n(cls.get('C5', 0))} seções permanecem pendentes por falta de dados ou de correspondência entre turnos.",
            "Nenhum destes resultados, isoladamente, demonstra fraude ou intenção.",
        ]
        for c in conc:
            s.append(Paragraph("• " + c, corpo))
    s.append(Spacer(1, 8))
    s.append(Paragraph("Parâmetros: " + ", ".join(f"{k}={v}" for k, v in asdict(p).items()), peq))
    doc.build(s)


# =============================================================================
# Orquestração
# =============================================================================
def processar_fonte(fonte: Fonte, fn: Callable[[Fonte], pd.DataFrame | None]) -> pd.DataFrame | None:
    if fonte.status not in ("BAIXADO", "LOCAL"):
        return None
    try:
        r = fn(fonte)
        fonte.status = "PROCESSADO"
        return r
    except (ErroFonte, zipfile.BadZipFile, UnicodeDecodeError, pd.errors.ParserError, ValueError, KeyError) as e:
        fonte.status = "FALHA_LEITURA"
        fonte.erro = f"{type(e).__name__}: {e}"
        LOG.error("Falha ao ler %s: %s", fonte.caminho, fonte.erro)
        return None


def executar(opc: argparse.Namespace) -> int:
    saida = Path(opc.saida).resolve()
    configurar_log(saida, opc.verboso)
    execucao = {"inicio_utc": agora_iso(), "versao_script": VERSAO_SCRIPT, "python": sys.version.split()[0],
                "pandas": pd.__version__, "numpy": np.__version__, "plataforma": platform.platform(),
                "comando": " ".join(sys.argv)}
    p = Parametros(limiar_pct=opc.limiar_pct, limiar_abs=opc.limiar_abs, z_limite=opc.z_limite,
                   iqr_k=opc.iqr_k, min_pares=opc.min_pares, tol_aptos_abs=opc.tol_aptos_abs,
                   tol_aptos_rel=opc.tol_aptos_rel, chunksize=opc.chunksize)
    ufs = [u.strip().upper() for u in opc.ufs.split(",")] if opc.ufs else list(UFS_BRASIL)
    if opc.incluir_exterior and UF_EXTERIOR not in ufs:
        ufs.append(UF_EXTERIOR)
    invalidas = [u for u in ufs if u not in UFS_BRASIL + (UF_EXTERIOR,)]
    if invalidas:
        LOG.error("UFs inválidas: %s", invalidas)
        return 3
    conj_ufs = set(ufs)
    LOG.info("Auditoria TSE 2026 v%s — UFs: %s", VERSAO_SCRIPT, ",".join(ufs))

    # ---------------- Etapa A: coleta ----------------
    falhas: list[dict] = []
    if opc.entrada:
        fontes = planejar_fontes(descobrir_local(Path(opc.entrada)), ufs, opc, permitir_inferidas=False)
        for f in fontes:
            if f.caminho and f.status == "PENDENTE":
                registrar_local(f)
    else:
        sessao = _sessao_http()
        hosts_inacessiveis: set[str] = set()
        candidatos = descobrir_ckan(sessao, opc.timeout, falhas, hosts_inacessiveis)
        fontes = planejar_fontes(candidatos, ufs, opc, permitir_inferidas=True)
        dir_dados = Path(opc.dados).resolve() if opc.dados else saida / "dados_tse"
        for f in fontes:
            if f.url and f.status == "PENDENTE":
                baixar(f, dir_dados, sessao, opc.timeout, opc.reusar, hosts_inacessiveis)

    # ---------------- Etapa B: leitura/normalização ----------------
    inconsist: list[pd.DataFrame] = []
    det_partes = []
    for f in [f for f in fontes if f.tipo == "detalhe_votacao_secao"]:
        r = processar_fonte(f, lambda f: ler_tabela(
            f, ["NR_TURNO", *KEY, "CD_CARGO", "QT_APTOS", "QT_COMPARECIMENTO", "QT_ABSTENCOES"],
            ["NM_MUNICIPIO"] + [c for v in CAMPOS_DETALHE.values() for c in v],
            filtro_cargo_uf("CD_CARGO", conj_ufs), p.chunksize))
        if r is not None and len(r):
            det_partes.append(r)
    det, mapa_campos = ({}, {})
    if det_partes:
        det, mapa_campos = preparar_detalhe(pd.concat(det_partes, ignore_index=True), inconsist)
    for t in (1, 2):
        LOG.info("detalhe: %d seções no %dº turno", len(det.get(t, [])), t)

    bu_partes, bu_carregado = [], set()
    for f in [f for f in fontes if f.tipo == "bweb"]:
        r = processar_fonte(f, lambda f: ler_tabela(
            f, [*KEY, "CD_CARGO_PERGUNTA", "QT_APTOS", "QT_COMPARECIMENTO", "QT_ABSTENCOES",
                "DS_TIPO_VOTAVEL", "QT_VOTOS"],
            ["NR_TURNO", "DS_AGREGADAS", "DS_TIPO_URNA", "NR_URNA_EFETIVADA", "NR_LOCAL_VOTACAO", "NR_VOTAVEL"],
            filtro_cargo_uf("CD_CARGO_PERGUNTA", conj_ufs), p.chunksize,
            a_cada_arquivo=lambda df, t=f.turno: agregar_bu(df, t)))
        if f.status == "PROCESSADO":
            bu_carregado.add((f.uf, f.turno))
            if r is not None and len(r):
                bu_partes.append(r)
        apagar_se_pedido(f, opc)
    bu = pd.concat(bu_partes, ignore_index=True) if bu_partes else None
    if bu is not None:
        n0 = len(bu)
        bu = bu.drop_duplicates(KEY + ["turno"])
        if len(bu) < n0:
            LOG.warning("bweb: %d seções repetidas entre arquivos descartadas", n0 - len(bu))

    vs_partes, vs_carregado = [], set()
    for f in [f for f in fontes if f.tipo == "votacao_secao"]:
        r = processar_fonte(f, lambda f: ler_tabela(
            f, ["NR_TURNO", *KEY, "CD_CARGO", "NR_VOTAVEL", "QT_VOTOS"], [],
            filtro_cargo_uf("CD_CARGO", conj_ufs), p.chunksize, a_cada_arquivo=agregar_vs))
        if f.status == "PROCESSADO" and r is not None and len(r):
            vs_partes.append(r)
            vs_carregado |= {(f.uf, int(t)) for t in r["turno"].dropna().unique()}
        apagar_se_pedido(f, opc)
    vs = pd.concat(vs_partes, ignore_index=True) if vs_partes else None

    elv_partes = []
    for f in [f for f in fontes if f.tipo == "eleitorado_local_votacao"]:
        r = processar_fonte(f, lambda f: ler_tabela(
            f, KEY, ["NR_TURNO", "AA_ELEICAO", "CD_TIPO_SECAO_AGREGADA", "DS_TIPO_SECAO_AGREGADA",
                     "NR_SECAO_PRINCIPAL", "QT_ELEITOR_SECAO", "NR_LOCAL_VOTACAO", "DS_TIPO_LOCAL",
                     "NM_LOCAL_VOTACAO"], filtro_cargo_uf(None, conj_ufs), p.chunksize))
        if r is not None and len(r):
            elv_partes.append(r)
    elv = preparar_eleitorado(pd.concat(elv_partes, ignore_index=True)) if elv_partes else None

    alt = None
    for f in [f for f in fontes if f.tipo == "secoes_alteradas_2t"]:
        alt = processar_fonte(f, preparar_alteradas)

    # ---------------- Etapas C–E ----------------
    escopo = avaliar_escopo(det, bu_carregado, vs_carregado, ufs)
    w = pd.DataFrame()
    if det and len(det.get(1, [])) and len(det.get(2, [])):
        w = consolidar(det, bu, vs, elv, alt, bu_carregado, vs_carregado, p, inconsist)
    inc = pd.concat([i for i in inconsist if len(i)], ignore_index=True) if any(len(i) for i in inconsist) \
        else pd.DataFrame(columns=KEY + ["turno", "grupo_teste", "teste", "valor_observado", "valor_esperado",
                                         "diferenca", "fonte", "observacao"])
    LOG.info("Status do escopo: %s", escopo["status"])

    # ---------------- Saídas ----------------
    ruf = resumo_uf(w)
    manifesto = {"execucao": execucao, "parametros": asdict(p), "escopo": escopo,
                 "fontes": [asdict(f) for f in fontes], "falhas_descoberta": falhas}
    (saida / "manifesto_fontes.json").write_text(json.dumps(manifesto, ensure_ascii=False, indent=2, default=str),
                                                 encoding="utf-8")
    vazio = pd.DataFrame({"Situação": ["Sem dados processados nesta execução — ver aba Fontes e Metodologia."]})
    if not w.empty:
        comp = w["situacao_correspondencia"].isin(SITUACOES_COMPARAVEIS)
        todas = selecionar(w[comp], COLS_SECAO)
        atip = selecionar(w[w["atipica"]].sort_values("z_robusto_grupo", ascending=False), COLS_SECAO)
        sinal = (w["atipica"] | w["g1_falha_1t"] | w["g1_falha_2t"] | w["div_bu_1t"] | w["div_bu_2t"]
                 | w["div_vs_1t"] | w["div_vs_2t"] | w["comparecimento_1t_zero"]
                 | ~comp | w["classificacao"].isin(["C2", "C3", "C4"]))
        valid = selecionar(w[sinal], COLS_VALIDACAO)
        nao_comp = selecionar(w[~comp | ~w["incluida_estatistica"].astype(bool)], COLS_SECAO)
        w.to_csv(saida / "secoes_consolidadas.csv.gz", index=False, sep=";", encoding="utf-8")
    else:
        todas = atip = valid = nao_comp = vazio
    inc.to_csv(saida / "inconsistencias.csv.gz", index=False, sep=";", encoding="utf-8")
    inc_mat = inc[inc["grupo_teste"].astype(str).str.startswith("G1") | inc["grupo_teste"].eq("Fontes")] \
        if not inc.empty else vazio
    df_fontes = pd.DataFrame([asdict(f) for f in fontes])
    met = pd.DataFrame(texto_metodologia(p, mapa_campos), columns=["Item", "Definição"])
    extra = pd.DataFrame([("Execução", f"{k}: {v}") for k, v in execucao.items()] +
                         [("Falha de descoberta", json.dumps(fl, ensure_ascii=False)) for fl in falhas] +
                         [("Lacuna de escopo", f"{l['UF']}: {l['faltando']}") for l in escopo["lacunas"]],
                         columns=["Item", "Definição"])
    df_fontes.insert(0, "Definição", df_fontes["tipo"] + " " + df_fontes["uf"].fillna("BR")
                     + df_fontes["turno"].map(lambda t: f" {int(t)}T" if pd.notna(t) else ""))
    df_fontes.insert(0, "Item", "Fonte de dados")
    fontes_met = pd.concat([df_fontes.astype(object), met.astype(object), extra.astype(object)], ignore_index=True)
    abas = [("Resumo Nacional", resumo_nacional(w, inc, escopo, p)),
            ("Resumo por UF", ruf if not ruf.empty else vazio),
            ("Todas as Seções Comparáveis", todas), ("Aumentos Atípicos", atip if len(atip) else vazio),
            ("Inconsistências Matemáticas", inc_mat if len(inc_mat) else vazio),
            ("Validações dos Boletins", valid if len(valid) else vazio),
            ("Seções Não Comparáveis", nao_comp if len(nao_comp) else vazio),
            ("Fontes e Metodologia", fontes_met)]
    escrever_xlsx(saida / "Auditoria_Seções_2026.xlsx", abas)
    escrever_pdf(saida / "Auditoria_TSE_2026.pdf", w, inc, fontes, falhas, escopo, ruf, p, execucao)
    LOG.info("Saídas gravadas em %s", saida)
    if escopo["status"] == "COMPLETA":
        return 0
    return 1 if escopo["status"] == "PARCIAL" else 2


def apagar_se_pedido(f: Fonte, opc: argparse.Namespace) -> None:
    if opc.apagar_apos_processar and f.status == "PROCESSADO" and f.origem_url != "arquivo local" and f.caminho:
        Path(f.caminho).unlink(missing_ok=True)


def argumentos(argv: list[str] | None = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--saida", default="./saida_auditoria", help="diretório de saída")
    ap.add_argument("--entrada", help="diretório com arquivos do TSE já baixados (desativa o download)")
    ap.add_argument("--dados", help="diretório para os downloads (padrão: <saida>/dados_tse)")
    ap.add_argument("--ufs", help="lista de UFs separadas por vírgula (padrão: 26 UFs + DF)")
    ap.add_argument("--incluir-exterior", action="store_true", help="inclui UF ZZ (votos no exterior)")
    ap.add_argument("--sem-votacao-secao", action="store_true", help="não usa votacao_secao (arquivos grandes)")
    ap.add_argument("--sem-bweb", action="store_true", help="não usa boletins de urna (impede C1/C2 validados)")
    ap.add_argument("--sem-eleitorado", action="store_true", help="não usa eleitorado_local_votacao")
    ap.add_argument("--reusar", action="store_true", help="reaproveita downloads com mesmo tamanho do servidor")
    ap.add_argument("--apagar-apos-processar", action="store_true", help="apaga bweb/votacao_secao baixados após leitura")
    ap.add_argument("--timeout", type=int, default=120)
    ap.add_argument("--chunksize", type=int, default=500_000)
    ap.add_argument("--limiar-pct", type=float, default=15.0)
    ap.add_argument("--limiar-abs", type=float, default=30.0)
    ap.add_argument("--z-limite", type=float, default=3.5)
    ap.add_argument("--iqr-k", type=float, default=1.5)
    ap.add_argument("--min-pares", type=int, default=10)
    ap.add_argument("--tol-aptos-abs", type=float, default=5.0)
    ap.add_argument("--tol-aptos-rel", type=float, default=0.02)
    ap.add_argument("--verboso", action="store_true")
    return ap.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    opc = argumentos(argv)
    warnings.simplefilter("ignore", pd.errors.PerformanceWarning)
    try:
        return executar(opc)
    except Exception:  # noqa: BLE001
        LOG.exception("Erro inesperado")
        return 3


if __name__ == "__main__":
    sys.exit(main())
