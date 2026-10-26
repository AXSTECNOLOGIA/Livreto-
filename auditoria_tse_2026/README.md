# Auditoria estatística TSE 2026 — comparecimento por seção (Presidente, 1º x 2º turno)

Pipeline reproduzível: coleta → validação → normalização → cálculos → testes de consistência →
estatística robusta → validação com boletins de urna → classificação C1–C5 → XLSX + PDF.

## Execução

```bash
pip install -r requirements.txt
python Auditoria_TSE_2026.py --saida ./saida                         # coleta via API CKAN do TSE
python Auditoria_TSE_2026.py --entrada ./dados_tse --saida ./saida   # arquivos já baixados
python Auditoria_TSE_2026.py --ufs DF,AC --saida ./saida             # subconjunto (PARCIAL)
python -m unittest discover -s tests -v                              # testes (fixture sintético)
```

Para rodar com download manual, salve em `./dados_tse` os arquivos com o nome publicado pelo TSE:
`detalhe_votacao_secao_2026.zip`, `votacao_secao_2026_<UF>.zip`, `bweb_1t_<UF>_*.zip`,
`bweb_2t_<UF>_*.zip`, `eleitorado_local_votacao_2026.zip` e, se disponível,
`secoes_eleitorais_alteradas_2t*.csv`.

Códigos de saída: `0` completa · `1` parcial · `2` não executada · `3` erro inesperado.

## Execução registrada em 2026-10-26

`execucao_2026-10-26/` contém a tentativa feita no ambiente em nuvem. Todos os hosts do TSE
(`dadosabertos.tse.jus.br`, `cdn.tse.jus.br`) foram recusados pela política de rede
(`Tunnel connection failed: 403 Forbidden`). **Nenhum dado eleitoral foi processado.** Os
arquivos dessa pasta documentam apenas as falhas de coleta e não contêm números eleitorais.

## Testes

`tests/test_auditoria.py` gera em diretório temporário um fixture **sintético** que imita só
o layout dos arquivos do TSE. Os números são inventados e servem apenas para exercitar cada regra
(C1–C5, agregação, BU divergente, comparecimento 1T zero, consolidado `_BRASIL` ignorado,
filtro de cargo, escolha da versão mais recente do BU, SHA-256 do manifesto).
