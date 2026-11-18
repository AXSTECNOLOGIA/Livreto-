"""Extrai recortes da ficha de referência do Pingo para uso exclusivo em storyboard/animatic.
Recortes NÃO são arte final; servem apenas como indicação de pose/expressão."""
import sys
from pathlib import Path
from PIL import Image

REF = Path(__file__).resolve().parents[3] / "referencias" / "PINGO_FICHA_TURNAROUND_HORIZONTAL_ENVIADA_2026-11-18.png"
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent / "recortes"

CROPS = {  # (x0, y0, x1, y1) na imagem 1536x1024
    "hero": (0, 0, 510, 535),
    "frente": (490, 235, 655, 470), "tres_quartos_dir": (655, 235, 825, 470),
    "perfil_dir": (825, 235, 1005, 470), "costas": (1005, 235, 1185, 470),
    "perfil_esq": (1185, 235, 1355, 470), "tres_quartos_esq": (1355, 235, 1525, 470),
    "exp_alegre": (30, 585, 245, 757), "exp_curioso": (245, 585, 458, 757),
    "exp_surpreso": (458, 585, 668, 757), "exp_pensativo": (668, 585, 880, 757),
    "exp_animado": (880, 585, 1090, 757), "exp_confiante": (1090, 585, 1300, 757),
    "exp_carinhoso": (1300, 585, 1515, 757),
}

def main() -> None:
    if not REF.exists():
        sys.exit(f"Referência não encontrada: {REF}")
    OUT.mkdir(parents=True, exist_ok=True)
    img = Image.open(REF).convert("RGB")
    for name, box in CROPS.items():
        img.crop(box).save(OUT / f"{name}.png")
    print(f"{len(CROPS)} recortes gravados em {OUT}")

if __name__ == "__main__":
    main()
