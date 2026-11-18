# Entrada de materiais gerados externamente — Ep. 01

## Vídeo (pasta `videos/`)
- Nome: `C01-P01_take01.mp4` (cena, tomada, número do take). Nunca sobrescrever takes: incrementar o número.
- Gerar sempre com a **ficha horizontal** como imagem de referência e o prompt da tomada (`storyboard/cena01_storyboard.md`).
- Especificação: 16:9; ideal 1920×1080 a 24 fps. Se a ferramenta só exportar 720p ou 30 fps, enviar mesmo assim: o validador sinaliza e a conversão é feita na montagem, com perda de qualidade registrada.
- Duração: igual ou **maior** que a da tomada (sobra é cortada; falta não é recuperável).
- Boca neutra nas tomadas com fala (lip sync na pós).

## Áudio (pasta `audio/`)
- Vozes: `voz_pingo_C01_pt_BR_take01.wav` / `..._en_US_...`; WAV 48 kHz, 24 bits, mono, sem música nem efeitos, cerca de 0,5 s de silêncio no início e no fim.
- Trilha e efeitos: `trilha_*.wav`, `sfx_*.wav`, com **comprovante de licença** comercial em `audio/licencas/`.

## Validação
`python3 projetos/validar_tomadas.py` — confere resolução, fps, duração mínima e integridade de cada take e grava o relatório em `relatorios/`.
