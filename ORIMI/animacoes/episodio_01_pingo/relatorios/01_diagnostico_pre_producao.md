# Diagnóstico de pré-produção — Episódio 01 "Pingo e a Primeira Aventura"

**Data:** 18/11/2026 · **Fase:** 1 (pré-produção) · **Estado:** aguardando aprovação do storyboard da Cena 01

## 1. Materiais oficiais localizados

| Fonte | Material | Situação |
|---|---|---|
| Google Drive | Registro mestre de aprovações v1.2 | Lido. Fonte de verdade das decisões |
| Google Drive | Fichas 9:16 aprovadas dos 9 personagens (Pingo, Capi, Tuca, Luma, Guri, Tatu, Tami, Nino, Kiko) | Localizadas. Texto da ficha do Pingo extraído; imagem da Capi não pôde ser extraída pelo conector |
| Google Drive | Capa do Vol. 01, contracapa (prova) e miolos PT/EN de 24 p. (prova) | Localizados. Texto do miolo PT lido |
| Chat (18/11) | Ficha horizontal do Pingo (6 vistas, 7 expressões, detalhes, paleta) | Copiada para `ORIMI/referencias/` |
| Chat (18/11) | Ficha horizontal da Capi (6 vistas, 8 expressões, lenço verde) | Copiada para `ORIMI/referencias/` |
| Repositório Git | Sem material ORIMI antes desta sessão. O repositório tem outro projeto (livro interativo do Evangelho de João) | Estrutura `ORIMI/` criada em paralelo, sem tocar nos arquivos existentes |

## 2. Referências ausentes ou divergentes

| ID | Item | Impacto |
|---|---|---|
| P-01 | **Fichas horizontais (turnaround) não estão registradas como aprovadas** no registro mestre. Lá constam só as fichas 9:16 | Alto. Definir qual ficha é a referência canônica da animação |
| P-02 | As expressões divergem. A ficha 9:16 do Pingo tem 6 (com "Determinado"); a horizontal tem 7 ("Animado" e "Confiante", sem "Determinado"). A da Capi tem 8 | Médio. Aprovar o conjunto de expressões da animação |
| P-03 | A ficha 9:16 do Pingo escreve **"Capti"** na historinha. É erro de geração | Baixo para a animação. Corrigir na revisão editorial do livro |
| P-04 | Não há logotipo ORIMI em vetor ou alta resolução, nem vinheta de abertura e encerramento | Alto para a Cena 06 e a entrega. É necessário o arquivo oficial da marca |
| P-05 | O bioma não está definido no material oficial (o livro diz só "floresta") | Médio. Proposta: Amazônia de várzea/mata ciliar, onde onça, capivara e *Morpho* coexistem |
| P-06 | Não há referência de cenário (abrigo, rio, trilha) nem bíblia de cores de ambiente | Médio. Criar na Fase 2, antes de gerar o piloto |
| P-07 | Não há HEX verificados para a Capi. Os HEX do Pingo vieram da arte gerada e ainda não foram conferidos (registro mestre, item 11.2) | Baixo. Medir na arte aprovada antes do color grading |

## 3. Ferramentas realmente disponíveis nesta sessão

| Papel no prompt | Capacidade necessária | Disponível? | Observação |
|---|---|---|---|
| **ASTRA** (planejamento) | Análise de roteiro, decupagem, storyboard | **Sim**. Feito pelo Claude | Storyboard da Cena 01 entregue |
| **LUA** (revisão/localização) | Revisão de texto, inglês, legendas | **Sim**. Feito pelo Claude | Roteiros PT/EN e SRT entregues |
| **TERRA** (engenharia) | Scripts, FFmpeg, validação técnica | **Sim**. FFmpeg (libx264/AAC), Python + Pillow, ImageMagick | Pipeline validado com o animatic |
| **SOL** (vídeo 3D) | Geração de vídeo a partir de imagem de referência | **Não** | Weave (Figma) existe, mas a conta não está vinculada. Adobe e Canva exigem autorização |
| SOL (imagem) | Geração de imagem | Parcial | Figma `generate_image` só aceita texto, **sem imagem de referência**, e consome créditos pagos. Não serve para manter a fidelidade dos personagens |
| Áudio: vozes | TTS ou dublagem | **Não** | O pacote Piper instala, mas os modelos de voz (Hugging Face) estão bloqueados pela rede. TTS sintético também não tem qualidade para animação infantil |
| Áudio: trilha e efeitos | Música original e foley | **Não** | Nenhum gerador ou banco licenciado disponível. Só daria para fazer síntese procedural básica |

**Conclusão:** esta sessão cobre a pré-produção, a localização, as legendas, a montagem e a validação técnica. **A geração de vídeo 3D e de áudio precisa de ferramentas externas.** Opções:
1. Vincular a conta Figma ao Weave (app.weavy.ai → perfil → vincular Figma). Depois, verificar se há um modelo de vídeo com imagem de referência e qual o custo.
2. Autorizar o conector Adobe nas configurações de conectores do claude.ai e verificar se ele expõe geração de vídeo.
3. Gerar os clipes fora daqui com os prompts do storyboard, salvar em `videos/` com a nomenclatura `C01-P0X_take0Y.mp4`, e eu monto e valido.

## 4. Riscos

| ID | Risco | Mitigação |
|---|---|---|
| R-01 | **A IA de vídeo muda o personagem** entre tomadas (manchas, cor, proporção). É o maior risco do projeto | Tomadas ≤ 8 s, sempre com imagem de referência, critérios de validação por tomada (ver storyboard) e rejeição explícita de takes fora do padrão |
| R-02 | Semelhança com personagens comerciais (já citada no registro mestre, item 4.7) | Revisão humana de originalidade antes de publicar ou monetizar |
| R-03 | **Lip sync bilíngue.** Boca animada em PT não casa com o áudio EN | Gerar as falas com boca neutra e fazer lip sync na pós, por idioma. Alternativa mais barata: enquadrar as falas EN com menos destaque para a boca. Decidir antes do piloto |
| R-04 | Direitos de trilha e vozes geradas por IA | Usar só trilha original ou com licença comercial documentada. Para vozes humanas, contrato de cessão |
| R-05 | Erros de fauna | Checagem feita: onça nada, capivara é semiaquática e herbívora, *Morpho* existe na Amazônia. Tucano e arara proibidos no fundo para não parecerem Tuca e Luma |
| R-06 | Repositório misturado (Evangelho de João + ORIMI) | Funciona, mas o ideal é um repositório próprio para o ORIMI. Vídeos finais pesados devem ir para Drive ou Git LFS, não para o Git comum |

## 5. Entregas desta fase (verificadas em disco)

| Arquivo | Verificação |
|---|---|
| `roteiro/roteiro_ep01_pt_BR.md` | Criado |
| `roteiro/script_ep01_en_US.md` | Criado |
| `storyboard/cena01_storyboard.md` | Criado: 6 tomadas, decupagem, continuidade, prompts para SOL |
| `storyboard/paineis/C01-P01..P06_v01.png` | 6 PNG de 1920×1080 |
| `storyboard/cena01_folha_contato_v01.png` | Inspecionada visualmente |
| `videos/cena01_animatic_v01.mp4` | ffprobe: 1920×1080, 24/1 fps, 40,000 s, H.264 + AAC (silencioso) |
| `legendas/cena01_pt_BR.srt`, `cena01_en_US.srt` | Criados |
| `ORIMI/personagens/PINGO_ficha_animacao.md`, `CAPI_ficha_animacao.md` | Criados (propostas) |

## 6. Decisões necessárias para avançar à Fase 2 (piloto)
1. Aprovar o storyboard e o timing da Cena 01, ou pedir ajustes.
2. Definir a ficha canônica (P-01) e o conjunto de expressões (P-02).
3. Aprovar o bioma (P-05).
4. Escolher a ferramenta de geração de vídeo e de vozes (seção 3).
5. Escolher a estratégia de lip sync bilíngue (R-03).
6. Fornecer o logotipo oficial em alta resolução (P-04).
