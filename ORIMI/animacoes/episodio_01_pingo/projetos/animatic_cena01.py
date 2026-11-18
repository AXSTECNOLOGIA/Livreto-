"""Animatic de timing da Cena 01 — "Bom dia, floresta!".

Gera painéis 1920x1080 (storyboard) e um MP4 de 40 s / 24 fps com movimentos de câmera
indicativos (zoompan). NÃO é arte final: usa recortes da ficha de referência apenas
para indicar pose/expressão e valida o pipeline de montagem (FFmpeg).

Uso:
    python3 animatic_cena01.py            # gera painéis + MP4 + folha de contato
Dependências: Pillow, FFmpeg/FFprobe no PATH.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
EP = HERE.parent
REF = EP.parents[1] / "referencias" / "PINGO_FICHA_TURNAROUND_HORIZONTAL_ENVIADA_2026-11-18.png"
PANELS = EP / "storyboard" / "paineis"
VIDEO_OUT = EP / "videos" / "cena01_animatic_v01.mp4"
SHEET_OUT = EP / "storyboard" / "cena01_folha_contato_v01.png"

W, H, FPS = 1920, 1080, 24
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

CROPS = {
    "hero": (0, 0, 510, 535), "frente": (490, 235, 655, 470),
    "costas": (1005, 235, 1185, 470), "tres_quartos_esq": (1355, 235, 1525, 470),
    "exp_alegre": (30, 585, 245, 757), "exp_carinhoso": (1300, 585, 1515, 757),
    "exp_animado": (880, 585, 1090, 757), "exp_curioso": (245, 585, 458, 757),
}


@dataclass(frozen=True)
class Shot:
    code: str
    start: float
    dur: float
    plan: str
    camera: str
    action: str
    sky: tuple[tuple[int, int, int], tuple[int, int, int]]
    pose: str | None
    zoom: tuple[float, float]  # zoom inicial/final do movimento indicativo
    dialogue: str = ""


SHOTS = [
    Shot("C01-P01", 0, 8, "Plano aéreo geral (drone)",
         "Travelling aéreo lento para frente sobre o dossel, descendo levemente",
         "Amanhecer: névoa sobre a mata ciliar, rio serpenteando, sol nascendo atrás das copas.",
         ((40, 52, 96), (247, 176, 96)), None, (1.00, 1.12)),
    Shot("C01-P02", 8, 6, "Grua descendo pelo dossel",
         "Grua vertical atravessando as copas, raios de luz volumétrica",
         "Folhas gotejando orvalho; revela grande árvore de raízes tabulares com um abrigo entre as raízes.",
         ((96, 120, 90), (250, 214, 150)), None, (1.10, 1.25)),
    Shot("C01-P03", 14, 6, "Plano médio fechado — Pingo dormindo",
         "Câmera estática, leve push-in",
         "Pingo enrolado sobre folhas secas, cauda sobre o focinho. Raio de sol toca o rosto; orelha tremelica.",
         ((70, 90, 60), (226, 196, 130)), "exp_carinhoso", (1.00, 1.08)),
    Shot("C01-P04", 20, 7, "Close-up → plano médio",
         "Push-in curto no bocejo, recua no espreguiçar",
         "Abre os olhos, boceja (dentes de leite, sem agressividade), espreguiça em 'reverência' felina.",
         ((80, 100, 66), (240, 206, 140)), "exp_animado", (1.15, 1.00)),
    Shot("C01-P05", 27, 7, "Plano médio frontal — fala",
         "Câmera na altura dos olhos de Pingo, estática",
         "Senta, sacode o pelo, olha para a floresta e fala com entusiasmo.",
         ((96, 132, 80), (250, 222, 160)), "frente", (1.00, 1.04),
         "Pingo: \"Bom dia, floresta! O que será que vamos descobrir hoje?\""),
    Shot("C01-P06", 34, 6, "Plano geral 3/4 traseiro",
         "Câmera baixa acompanha Pingo saindo do abrigo; para no final",
         "Pingo trota para a luz. No último segundo, uma borboleta azul cruza o quadro (gancho da Cena 02).",
         ((110, 150, 90), (252, 230, 170)), "costas", (1.00, 1.06)),
]


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


def crop_pose(name: str) -> Image.Image:
    return Image.open(REF).convert("RGB").crop(CROPS[name])


def gradient(top: tuple[int, int, int], bottom: tuple[int, int, int]) -> Image.Image:
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    for y in range(H):
        t = y / (H - 1)
        d.line([(0, y), (W, y)], fill=tuple(int(a + (b - a) * t) for a, b in zip(top, bottom)))
    return img


def forest_silhouette(img: Image.Image, shot: Shot) -> None:
    """Esboço esquemático do cenário (apenas para leitura espacial)."""
    d = ImageDraw.Draw(img, "RGBA")
    if shot.code == "C01-P01":
        d.ellipse([1300, 260, 1500, 460], fill=(255, 230, 160, 200))  # sol
        for i in range(26):
            x = i * 80 - 20
            d.ellipse([x, 560 - (i % 3) * 30, x + 190, 760], fill=(34, 70, 40, 235))
        d.polygon([(0, 900), (500, 820), (900, 880), (1300, 800), (1920, 860), (1920, 940),
                   (1300, 870), (900, 950), (500, 890), (0, 970)], fill=(150, 190, 210, 220))  # rio
        d.rectangle([0, 760, W, 820], fill=(255, 255, 255, 60))  # névoa
    else:
        for x, w in ((60, 140), (1650, 180), (380, 70), (1400, 60)):
            d.rectangle([x, 0, x + w, H], fill=(48, 36, 24, 200))
        for i in range(0, W, 120):
            d.ellipse([i - 60, -120, i + 180, 220], fill=(40, 80, 44, 220))
        d.rectangle([0, 900, W, H], fill=(92, 70, 40, 230))
        for i in range(5):
            x = 300 + i * 300
            d.polygon([(x, 0), (x + 120, 0), (x + 420, 900), (x + 260, 900)], fill=(255, 240, 190, 40))


def wrap(text: str, f: ImageFont.FreeTypeFont, width: int, draw: ImageDraw.ImageDraw) -> list[str]:
    words, lines, cur = text.split(), [], ""
    for w in words:
        test = f"{cur} {w}".strip()
        if draw.textlength(test, font=f) <= width:
            cur = test
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def panel(shot: Shot) -> Image.Image:
    img = gradient(*shot.sky)
    forest_silhouette(img, shot)
    if shot.pose:
        pose = crop_pose(shot.pose)
        scale = 640 / pose.height
        pose = pose.resize((int(pose.width * scale), 640), Image.LANCZOS)
        card = Image.new("RGB", (pose.width + 24, pose.height + 24), (255, 255, 255))
        card.paste(pose, (12, 12))
        shadow = Image.new("RGBA", (card.width + 40, card.height + 40), (0, 0, 0, 0))
        ImageDraw.Draw(shadow).rounded_rectangle([20, 20, card.width + 20, card.height + 20], 24, fill=(0, 0, 0, 120))
        shadow = shadow.filter(ImageFilter.GaussianBlur(14))
        x, y = (W - card.width) // 2, 140
        img.paste(shadow, (x - 10, y - 4), shadow)
        img.paste(card, (x, y))
    d = ImageDraw.Draw(img, "RGBA")
    # Área segura de título (90%) e marca de animatic
    d.rectangle([96, 54, W - 96, H - 54], outline=(255, 255, 255, 90), width=2)
    d.rounded_rectangle([40, 30, 760, 100], 18, fill=(20, 60, 30, 210))
    d.text((60, 44), f"{shot.code}  |  {shot.start:05.1f}s – {shot.start + shot.dur:05.1f}s ({shot.dur:.0f}s)",
           font=font(FONT_B, 30), fill="white")
    d.text((W - 640, 44), "ANIMATIC — NÃO É ARTE FINAL", font=font(FONT_B, 30), fill=(255, 235, 120))
    # Bloco inferior com descrição
    d.rounded_rectangle([40, 800, W - 40, H - 24], 22, fill=(0, 0, 0, 175))
    d.text((70, 815), shot.plan, font=font(FONT_B, 32), fill=(255, 210, 90))
    d.text((70, 858), f"Câmera: {shot.camera}", font=font(FONT_R, 26), fill="white")
    y = 896
    for line in wrap(f"Ação: {shot.action}", font(FONT_R, 26), W - 140, d)[:2]:
        d.text((70, y), line, font=font(FONT_R, 26), fill=(230, 230, 230))
        y += 34
    if shot.dialogue:
        d.rounded_rectangle([300, 690, W - 300, 780], 20, fill=(255, 255, 255, 235))
        tf = font(FONT_B, 32)
        tw = d.textlength(shot.dialogue, font=tf)
        d.text(((W - tw) / 2, 718), shot.dialogue, font=tf, fill=(30, 60, 30))
    return img


def run(cmd: list[str]) -> None:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        sys.exit(f"Falha ao executar {' '.join(cmd[:3])}...\n{proc.stderr[-2000:]}")


def render_video(paths: list[Path]) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        clips = []
        for shot, p in zip(SHOTS, paths):
            frames = int(shot.dur * FPS)
            z0, z1 = shot.zoom
            zexpr = f"{z0}+({z1}-{z0})*on/{frames - 1}"
            clip = Path(tmp) / f"{shot.code}.mp4"
            run(["ffmpeg", "-y", "-loop", "1", "-i", str(p), "-vf",
                 f"scale=3840:2160,zoompan=z='{zexpr}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
                 f":d={frames}:s={W}x{H}:fps={FPS},format=yuv420p",
                 "-frames:v", str(frames), "-c:v", "libx264", "-preset", "medium", "-crf", "20", str(clip)])
            clips.append(clip)
        lst = Path(tmp) / "lista.txt"
        lst.write_text("".join(f"file '{c}'\n" for c in clips))
        VIDEO_OUT.parent.mkdir(parents=True, exist_ok=True)
        # Trilha silenciosa para manter compatibilidade de players/plataformas
        run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
             "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-shortest",
             "-c:v", "copy", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(VIDEO_OUT)])


def validate() -> dict:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                          "stream=codec_type,width,height,r_frame_rate:format=duration",
                          "-of", "json", str(VIDEO_OUT)], capture_output=True, text=True, check=True)
    info = json.loads(out.stdout)
    v = next(s for s in info["streams"] if s["codec_type"] == "video")
    dur = float(info["format"]["duration"])
    report = {"arquivo": str(VIDEO_OUT.relative_to(EP)), "resolucao": f"{v['width']}x{v['height']}",
              "fps": v["r_frame_rate"], "duracao_s": round(dur, 3),
              "ok": v["width"] == W and v["height"] == H and v["r_frame_rate"] == f"{FPS}/1" and abs(dur - 40) < 0.1}
    return report


def contact_sheet(paths: list[Path]) -> None:
    tw, th, pad = 640, 360, 16
    sheet = Image.new("RGB", (tw * 3 + pad * 4, th * 2 + pad * 3 + 70), (245, 242, 230))
    d = ImageDraw.Draw(sheet)
    d.text((pad, 18), "ORIMI — Ep. 01 — Cena 01 'Bom dia, floresta!' — Storyboard v01 (animatic, não é arte final)",
           font=font(FONT_B, 26), fill=(20, 70, 30))
    for i, p in enumerate(paths):
        im = Image.open(p).resize((tw, th), Image.LANCZOS)
        sheet.paste(im, (pad + (i % 3) * (tw + pad), 70 + pad + (i // 3) * (th + pad)))
    sheet.save(SHEET_OUT)


def main() -> None:
    for tool in ("ffmpeg", "ffprobe"):
        if not shutil.which(tool):
            sys.exit(f"Ferramenta ausente: {tool}")
    if not REF.exists():
        sys.exit(f"Referência não encontrada: {REF}")
    assert abs(sum(s.dur for s in SHOTS) - 40) < 1e-6, "Soma das tomadas deve ser 40 s"
    PANELS.mkdir(parents=True, exist_ok=True)
    paths = []
    for s in SHOTS:
        p = PANELS / f"{s.code}_v01.png"
        panel(s).save(p)
        paths.append(p)
    contact_sheet(paths)
    render_video(paths)
    print(json.dumps(validate(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
