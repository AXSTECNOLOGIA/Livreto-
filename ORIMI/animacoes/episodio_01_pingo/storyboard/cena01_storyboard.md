# Cena 01 — "Bom dia, floresta!" — Storyboard e decupagem (v01, ASTRA)

**Duração:** 40 s = 960 quadros @ 24 fps · **Tomadas:** 6 (todas ≤ 8 s, para facilitar geração e correção)
**Painéis:** `paineis/C01-P0X_v01.png` · **Folha de contato:** `cena01_folha_contato_v01.png`
**Animatic de timing:** `../videos/cena01_animatic_v01.mp4` (sem áudio; trilha silenciosa) — **não é arte final**.
**Gerador:** `../projetos/animatic_cena01.py` (reproduzível).

| Tomada | Tempo | Quadros | Plano | Câmera | Ação | Áudio previsto |
|---|---|---|---|---|---|---|
| C01-P01 | 0:00–0:08 | 0–191 | Aéreo geral | Travelling aéreo lento, descendo | Névoa sobre a mata ciliar, rio serpenteando, sol nascendo | Trilha entra suave; pássaros distantes |
| C01-P02 | 0:08–0:14 | 192–335 | Grua pelo dossel | Grua vertical, raios de luz | Orvalho pingando; revela árvore de raízes tabulares com abrigo | Gotas, folhas, aves mais próximas |
| C01-P03 | 0:14–0:20 | 336–479 | Médio fechado | Estática, push-in leve | Pingo dormindo enrolado; raio de sol no rosto; orelha tremelica | Respiração suave |
| C01-P04 | 0:20–0:27 | 480–647 | Close → médio | Push-in no bocejo, recua no espreguiçar | Abre os olhos, boceja, espreguiça em "reverência" | Bocejo (vocal Pingo) |
| C01-P05 | 0:27–0:34 | 648–815 | Médio frontal | Altura dos olhos, estática | Senta, sacode o pelo, fala | **Fala Pingo** 0:28,5–0:32,5 |
| C01-P06 | 0:34–0:40 | 816–959 | Geral 3/4 traseiro | Baixa, acompanha e para | Trota para a luz; borboleta azul cruza no último segundo | Passos em folhas; motivo musical do "curioso" |

## Continuidade
- **Eixo:** Pingo sai do abrigo para a **direita do quadro** (P06). A Cena 02 deve começar com ele entrando pela esquerda, seguindo a borboleta para a direita.
- **Luz:** chave quente vinda da direita-alto (sol nascente) em P02–P06; temperatura sobe gradualmente (amanhecer → manhã).
- **Abrigo:** mesma árvore e mesmo leito de folhas reaparecem na Cena 06 (retorno).
- **Borboleta azul:** asa azul-metálica com borda escura (*Morpho*); mesmo design na Cena 02.

## Prompts para SOL (geração de vídeo image-to-video — usar a ficha como imagem de referência)
Prefixo comum (todas as tomadas):
> Cinematic 3D children's animation, soft natural lighting, Brazilian Amazon riverside forest, gentle and warm mood, 24 fps, 16:9. Character: PINGO, a jaguar cub exactly as in the reference sheet — golden fur, cream muzzle/chest/belly, dark brown spots with the same head pattern, round ears with dark brown rims and pink interior, large amber-brown eyes, long spotted tail with dark brown tip. Do not change proportions, colors or markings.

Negativo comum:
> no other animals in focus, no toucans, no macaws, no humans, no text, no logos, no realistic predatory behavior, no bared fangs, no extra limbs, no color shift of the fur, no style change between shots.

| Tomada | Prompt específico |
|---|---|
| P01 | Aerial drone shot at dawn, slow forward glide over misty rainforest canopy, a calm river winding through, sun rising behind the trees, golden light breaking through the mist. No character visible. |
| P02 | Vertical crane shot descending through the canopy, dew drops falling from leaves, volumetric sun rays, revealing a giant tree with buttress roots and a cozy hollow between the roots lined with dry leaves. |
| P03 | Medium close shot, static with slight push-in: PINGO sleeping curled up on dry leaves inside the root hollow, tail over his nose, a sunbeam slowly touches his face, one ear twitches. |
| P04 | Close-up: PINGO opens his eyes, gives a big cute yawn showing tiny milk teeth, then camera pulls back as he does a feline play-bow stretch, front paws extended, hips up. |
| P05 | Medium frontal shot at the cub's eye level, static: PINGO sits up, shakes his fur, looks around the forest with joyful curiosity and speaks enthusiastically (mouth neutral if lip sync is done in post). |
| P06 | Low wide 3/4 rear shot: PINGO trots out of the hollow toward the sunlight, camera follows then stops; in the last second a blue morpho butterfly flutters across the frame. |

## Critérios de validação da tomada (antes de entrar na montagem)
1. Padrão de manchas da cabeça idêntico à referência; cor da pelagem dentro da paleta.
2. Ponta da cauda marrom-escura; orelhas com borda escura.
3. Sem deformação de patas/rosto entre quadros; sem "morphing" de manchas.
4. Duração exata (quadros) e direção de saída coerente com o eixo.
5. Nenhum animal de fundo parecido com personagens ORIMI.
