"""Valida takes de vídeo gerados externamente contra a decupagem da Cena 01.

Checa: decodificação íntegra, resolução 1920x1080, 24 fps, duração >= duração da tomada.
Saída: relatórios/validacao_tomadas_<data>.md. Código de saída 1 se algum take reprovar.
A checagem de fidelidade visual do personagem continua sendo manual (critérios no storyboard).
"""
from __future__ import annotations

import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path

EP = Path(__file__).resolve().parent.parent
VIDEOS, REPORTS = EP / "videos", EP / "relatorios"
SHOT_DUR = {"C01-P01": 8, "C01-P02": 6, "C01-P03": 6, "C01-P04": 7, "C01-P05": 7, "C01-P06": 6}
NAME_RE = re.compile(r"^(C\d{2}-P\d{2})_take(\d{2})\.(mp4|mov)$", re.I)


def probe(path: Path) -> dict:
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=width,height,r_frame_rate:format=duration", "-of", "json", str(path)],
                         capture_output=True, text=True)
    if out.returncode != 0:
        raise RuntimeError(out.stderr.strip() or "ffprobe falhou")
    data = json.loads(out.stdout)
    s = data["streams"][0]
    num, den = map(int, s["r_frame_rate"].split("/"))
    return {"w": s["width"], "h": s["height"], "fps": num / den, "dur": float(data["format"]["duration"])}


def decodes(path: Path) -> bool:
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-f", "null", "-"], capture_output=True, text=True)
    return r.returncode == 0 and not r.stderr.strip()


def main() -> int:
    rows, failed = [], False
    for f in sorted(VIDEOS.iterdir()):
        if f.name.startswith("cena01_animatic") or f.is_dir():
            continue
        m = NAME_RE.match(f.name)
        if not m or m.group(1).upper() not in SHOT_DUR:
            rows.append((f.name, "—", "REPROVADO: nome fora do padrão ou tomada inexistente"))
            failed = True
            continue
        try:
            info = probe(f)
        except Exception as exc:  # arquivo corrompido ou não-vídeo
            rows.append((f.name, "—", f"REPROVADO: {exc}"))
            failed = True
            continue
        issues, warns = [], []
        if info["dur"] + 1e-3 < SHOT_DUR[m.group(1).upper()]:
            issues.append(f"duração {info['dur']:.2f}s < {SHOT_DUR[m.group(1).upper()]}s")
        if not decodes(f):
            issues.append("erros de decodificação")
        if (info["w"], info["h"]) != (1920, 1080):
            (issues if info["w"] * 9 != info["h"] * 16 else warns).append(f"resolução {info['w']}x{info['h']}")
        if abs(info["fps"] - 24) > 0.01:
            warns.append(f"{info['fps']:.3f} fps (será convertido para 24)")
        status = "REPROVADO: " + "; ".join(issues) if issues else ("OK com ressalvas: " + "; ".join(warns) if warns else "OK")
        failed |= bool(issues)
        rows.append((f.name, f"{info['w']}x{info['h']} · {info['fps']:.2f} fps · {info['dur']:.2f}s", status))

    REPORTS.mkdir(exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y-%m-%d_%H%M")
    report = REPORTS / f"validacao_tomadas_{stamp}.md"
    lines = [f"# Validação técnica de takes — {stamp}", "", "| Arquivo | Técnico | Resultado |", "|---|---|---|"]
    lines += [f"| {a} | {b} | {c} |" for a, b, c in rows] or ["| — | — | Nenhum take encontrado |"]
    lines += ["", "Fidelidade visual: checagem manual pendente para cada take aprovado tecnicamente."]
    report.write_text("\n".join(lines) + "\n")
    print(report.read_text())
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
