#!/usr/bin/env python3
"""Dados do Capítulo 1 — Estudo do Evangelho de João"""

NAVY   = "#1a2744"
GOLD   = "#c9a84c"
CREAM  = "#f5f0e8"
GREEN  = "#2d6a4f"
PURPLE = "#6b3d8f"
ORANGE = "#e07b39"
GRAY   = "#8b8680"

CAP1 = {
    "numero": 1,
    "titulo": "O Verbo se Fez Carne",
    "subtitulo": "João 1:1-51",
    "serie": "Estudo do Evangelho de João",
    "tema_geral": "Conhecendo Jesus, o Filho de Deus",

    "versiculo_chave": {
        "texto": "E o Verbo se fez carne e habitou entre nós, e vimos a sua glória, como a glória do Unigênito do Pai, cheio de graça e de verdade.",
        "ref": "João 1:14"
    },

    "panorama": {
        "texto": (
            "João inicia seu evangelho apresentando Jesus como o Verbo eterno, que existia com Deus "
            "desde o princípio e por meio de quem todas as coisas foram feitas. Em seguida, João Batista "
            "testemunha sobre Jesus, o Cordeiro de Deus, e vemos os primeiros discípulos sendo chamados "
            "para segui-lo. O prólogo (v.1–18) é um dos textos mais profundos da Bíblia, identificando "
            "Jesus como o Logos — a Razão divina que permeia o universo — que assumiu a natureza humana "
            "para habitar entre nós."
        ),
        "temas": [
            "O Verbo Eterno e a Criação",
            "Luz e Trevas",
            "Encarnação do Filho de Deus",
            "Testemunho de João Batista",
            "O Chamado dos Primeiros Discípulos",
        ],
        "estrutura": [
            {"ref": "1:1–18",  "titulo": "O Prólogo — O Verbo Eterno"},
            {"ref": "1:19–28", "titulo": "O Testemunho de João Batista"},
            {"ref": "1:29–34", "titulo": "O Cordeiro de Deus"},
            {"ref": "1:35–42", "titulo": "Os Dois Primeiros Discípulos"},
            {"ref": "1:43–51", "titulo": "Filipe e Natanael"},
        ],
    },

    "personagens": [
        {
            "nome": "Jesus — O Verbo",
            "titulo": "O Filho Unigênito",
            "descricao": (
                "João apresenta Jesus como o Logos eterno, coexistente com Deus antes da criação. "
                "Ele é a Luz verdadeira que ilumina todo ser humano, o Filho Unigênito cheio de "
                "graça e verdade. João Batista proclama: 'Eis o Cordeiro de Deus que tira o "
                "pecado do mundo!'"
            ),
            "versiculo": "No princípio era o Verbo, e o Verbo estava com Deus. (1:1)",
            "cor": NAVY,
            "inicial": "J",
        },
        {
            "nome": "João Batista",
            "titulo": "O Profeta Precursor",
            "descricao": (
                "Enviado por Deus como testemunha da Luz, João Batista recusou ser chamado de "
                "Messias, Elias ou O Profeta. Ele se identificou apenas como 'a voz que clama "
                "no deserto'. Sua missão era preparar o caminho e apontar para Cristo."
            ),
            "versiculo": "Ele veio como testemunha, para testificar da Luz. (1:7)",
            "cor": GREEN,
            "inicial": "B",
        },
        {
            "nome": "André e Pedro",
            "titulo": "Os Primeiros Chamados",
            "descricao": (
                "André, discípulo de João Batista, foi o primeiro a seguir Jesus. Imediatamente "
                "buscou seu irmão Simão Pedro. Jesus o renomeou: 'Tu serás chamado Cefas' — "
                "revelando o destino do impulsivo pescador antes mesmo de ele demonstrá-lo."
            ),
            "versiculo": "Trouxe-o a Jesus. (1:42)",
            "cor": ORANGE,
            "inicial": "A",
        },
        {
            "nome": "Filipe e Natanael",
            "titulo": "Vinde e Vede",
            "descricao": (
                "Jesus chamou Filipe diretamente: 'Segue-me.' Filipe encontrou Natanael e o "
                "anunciou como cumprimento das profecias. Natanael, cético ('Pode vir algo bom "
                "de Nazaré?'), ficou atônito quando Jesus revelou conhecê-lo sob a figueira."
            ),
            "versiculo": "Filipe lhe disse: Vem e vê. (1:46)",
            "cor": PURPLE,
            "inicial": "N",
        },
    ],

    "contexto": {
        "titulo": "Contexto Histórico",
        "periodo": "85–95 d.C. — Éfeso, Ásia Menor",
        "texto": (
            "O Evangelho de João foi escrito por volta de 85–95 d.C., provavelmente na cidade "
            "de Éfeso. Naquele tempo, o povo judeu estava sob domínio romano. Muitos esperavam "
            "um Messias, mas Jesus veio de forma diferente do que imaginavam. João escreve para "
            "que todos creiam que Jesus é o Cristo, o Filho de Deus, e tenham vida em seu nome "
            "(João 20:31). O autor usa a palavra grega Logos — 'Verbo' — conceito familiar tanto "
            "ao judaísmo quanto à filosofia grega, para apresentar Jesus a todo o mundo."
        ),
        "marcos": [
            {"ano": "63 a.C.", "evento": "Roma conquista Jerusalém (Pompeu)"},
            {"ano": "37 a.C.", "evento": "Herodes, o Grande, torna-se rei"},
            {"ano": "~4 a.C.", "evento": "Nascimento de Jesus em Belém"},
            {"ano": "26–30 d.C.", "evento": "Ministério público de Jesus"},
            {"ano": "30/33 d.C.", "evento": "Crucificação e Ressurreição"},
            {"ano": "70 d.C.", "evento": "Destruição do Templo pelos romanos"},
            {"ano": "85–95 d.C.", "evento": "João escreve o Evangelho em Éfeso"},
        ],
        "local": "Os acontecimentos ocorreram principalmente na Judeia e na Galileia.",
        "mapa": {
            "regioes": ["GALILEIA", "SAMARIA", "JUDEIA"],
            "locais": ["Jerusalém", "Betânia além do Jordão", "Caná"],
            "mares": ["Mar Mediterrâneo", "Mar da Galileia"],
            "rios": ["Rio Jordão"],
        },
    },

    "blocos": [
        {
            "num": 1,
            "ref": "João 1:1-5",
            "titulo": "O Verbo Eterno",
            "cor": NAVY,
            "icone": "✦",
            "texto": (
                "No princípio era o Verbo, e o Verbo estava com Deus, e o Verbo era Deus. "
                "Ele estava no princípio com Deus. Todas as coisas foram feitas por ele, e "
                "sem ele nada do que foi feito se fez. Nele estava a vida, e a vida era a "
                "luz dos homens. E a luz resplandece nas trevas, e as trevas não a compreenderam."
            ),
            "aprendizado_titulo": "Jesus não foi criado",
            "aprendizado": (
                "Jesus é eterno e divino. Ele existia desde o princípio, estava com Deus "
                "e era Deus. Tudo foi criado por meio dele, e nele havia vida, que é a luz "
                "dos homens. Três afirmações sobre o Verbo: (1) preexistência eterna, "
                "(2) comunhão pessoal com o Pai, (3) divindade plena."
            ),
            "imagem_prompt": "cosmic creation, light emanating from center, stars being formed, blue and gold tones, biblical scene, photorealistic",
        },
        {
            "num": 2,
            "ref": "João 1:6-13",
            "titulo": "O Testemunho de João Batista",
            "cor": GREEN,
            "icone": "☀",
            "texto": (
                "Houve um homem enviado por Deus, cujo nome era João. Este veio como "
                "testemunha, para que testificasse da Luz, para que todos cressem por "
                "meio dele. Ele não era a Luz, mas veio para que testificasse da Luz. "
                "Havia a Luz verdadeira que, vindo ao mundo, ilumina todo o homem... "
                "Mas a todos quantos o receberam, deu-lhes o poder de serem feitos filhos de Deus."
            ),
            "aprendizado_titulo": "Nossa missão: apontar para Cristo",
            "aprendizado": (
                "João Batista é introduzido como testemunha — não a Luz, mas aquele que "
                "aponta para Ela. Como ele, nossa função não é sermos o centro, mas "
                "direcionar outros a Jesus. Para os que O recebem e creem, há uma "
                "transformação radical: tornam-se filhos de Deus."
            ),
            "imagem_prompt": "John the Baptist in the wilderness pointing to a bright light in the distance, desert landscape, Jordan river, dramatic sky, photorealistic biblical scene",
        },
        {
            "num": 3,
            "ref": "João 1:14-18",
            "titulo": "Deus Habitou entre Nós",
            "cor": GOLD,
            "icone": "◈",
            "texto": (
                "E o Verbo se fez carne e habitou entre nós (e vimos a sua glória, como a "
                "glória do Unigênito do Pai), cheio de graça e de verdade... Porque a lei "
                "foi dada por Moisés; a graça e a verdade vieram por Jesus Cristo. Ninguém "
                "jamais viu a Deus; o Filho Unigênito, que está no seio do Pai, esse o has revelado."
            ),
            "aprendizado_titulo": "Jesus veio para revelar Deus",
            "aprendizado": (
                "O Verbo eterno assumiu permanentemente a humanidade. 'Habitou entre nós' "
                "no grego significa literalmente 'armou sua tenda' — evocando o tabernáculo "
                "no deserto. Moisés deu a Lei; Jesus trouxe a realidade que a Lei prefigurava: "
                "graça e verdade em pessoa."
            ),
            "imagem_prompt": "Jesus Christ walking among people in ancient Galilee, warm golden light surrounding him, disciples following, photorealistic, cinematic",
        },
        {
            "num": 4,
            "ref": "João 1:19-34",
            "titulo": "O Cordeiro de Deus",
            "cor": PURPLE,
            "icone": "◎",
            "texto": (
                "E este é o testemunho de João... Eu sou a voz do que clama no deserto: "
                "Endireitai o caminho do Senhor... No dia seguinte, viu João a Jesus, que "
                "vinha ter com ele, e disse: Eis o Cordeiro de Deus, que tira o pecado do "
                "mundo! Este é aquele de quem eu disse: Depois de mim vem um homem que é "
                "antes de mim; porque era primeiro do que eu."
            ),
            "aprendizado_titulo": "Jesus é o sacrifício perfeito",
            "aprendizado": (
                "João Batista se define como 'voz' — não uma identidade autônoma, mas o "
                "canal por onde passa a mensagem. A proclamação 'Cordeiro de Deus' conecta "
                "Jesus ao sistema sacrificial do AT, mas transcende-o: este Cordeiro tira "
                "o pecado do mundo — não apenas de Israel."
            ),
            "imagem_prompt": "white lamb in a green peaceful meadow, soft morning light, symbolic and serene, photorealistic",
        },
        {
            "num": 5,
            "ref": "João 1:35-51",
            "titulo": "Os Primeiros Discípulos",
            "cor": ORANGE,
            "icone": "⟡",
            "texto": (
                "No dia seguinte, estava João, e dois dos seus discípulos. E, olhando para "
                "Jesus que passava, disse: Eis o Cordeiro de Deus! E os dois discípulos "
                "ouviram-no falar, e seguiram a Jesus... Filipe disse-lhe: Vem e vê. "
                "Jesus disse-lhe: Porque te disse que te vi debaixo da figueira, crês? "
                "Coisas maiores do que estas verás."
            ),
            "aprendizado_titulo": "Quem encontra Jesus compartilha com outros",
            "aprendizado": (
                "O padrão do discipulado em João: encontro com Jesus → transformação pessoal "
                "→ convite aos outros. André encontra Pedro. Filipe encontra Natanael. "
                "A evangelização não é argumento, é convite à experiência: 'Vem e vê' "
                "é a estratégia apostólica mais simples e eficaz."
            ),
            "imagem_prompt": "group of fishermen by the Sea of Galilee following Jesus, sunset, fishing nets, photorealistic biblical scene",
        },
    ],

    "aprendemos_sobre_jesus": [
        "Ele é eterno e divino.",
        "Ele é o Criador de todas as coisas.",
        "Ele é a Luz que ilumina o mundo.",
        "Ele se fez homem e viveu entre nós.",
        "Ele é o Cordeiro de Deus que tira o pecado do mundo.",
        "Ele chama pessoas comuns para segui-lo.",
    ],

    "sintese": {
        "titulo": "Síntese Teológica",
        "temas": [
            {
                "titulo": "Cristologia Alta",
                "texto": "João apresenta a cristologia mais elevada dos Evangelhos: Jesus não apenas nasce de virgem — Ele existia antes da criação como Deus eterno.",
                "icone": "✦",
                "cor": NAVY,
            },
            {
                "titulo": "Luz vs. Trevas",
                "texto": "O dualismo luz/trevas percorre todo o Evangelho. As trevas não compreenderam nem extinguiram a Luz — indicando rejeição e impotência das trevas.",
                "icone": "◑",
                "cor": GOLD,
            },
            {
                "titulo": "Fé e Adoção",
                "texto": "Receber Jesus é o ato de fé que gera novo nascimento e adoção divina — o Evangelho em miniatura já está no capítulo 1 (v.12).",
                "icone": "♡",
                "cor": GREEN,
            },
            {
                "titulo": "Graça sobre Graça",
                "texto": "'Graça sobre graça' (v.16): a plenitude de Cristo é inesgotável — cada graça recebida abre caminho para mais graça, nunca para lei ou mérito.",
                "icone": "∞",
                "cor": PURPLE,
            },
        ],
    },

    "curiosidades": [
        {
            "titulo": "O Logos Grego",
            "texto": (
                "O termo 'Verbo' (Logos) era conhecido no mundo grego como 'a razão' ou 'a "
                "palavra que dá sentido'. Para Heráclito (500 a.C.), era o princípio racional "
                "que governa o cosmos. João mostra que essa Palavra é Jesus!"
            ),
            "icone": "🏛",
        },
        {
            "titulo": "Dez Testemunhas",
            "texto": (
                "Na cultura judaica, dez testemunhas eram necessárias para confirmar algo "
                "(Deuteronômio 19:15). João Batista 'testemunha' sobre Jesus três vezes "
                "neste capítulo — estabelecendo credibilidade legal máxima."
            ),
            "icone": "⚖",
        },
        {
            "titulo": "A Figueira de Natanael",
            "texto": (
                "Natanael morava em Caná da Galileia, a mesma cidade onde Jesus realizou "
                "seu primeiro milagre (João 2:1). Sentar sob a figueira era postura típica "
                "de rabino em meditação — o que Natanael fazia ali permanece misterioso."
            ),
            "icone": "🌿",
        },
        {
            "titulo": "Cefas — Profecia em Nome",
            "texto": (
                "Jesus chama Simão de 'Cefas' (aramaico) = 'Pedro' (grego) = 'Rocha'. "
                "Este renomeio no primeiro encontro é declaração profética — não do que "
                "Simão era (impulsivo), mas do que a graça faria dele."
            ),
            "icone": "🪨",
        },
    ],

    "aplicacao": {
        "titulo": "Aplicação Prática",
        "pontos": [
            {
                "num": "1",
                "titulo": "Creia que Jesus é Deus e Salvador",
                "texto": "Receba a Luz ativamente. Receber Jesus muda nossa identidade — de filhos do mundo para filhos de Deus.",
                "icone": "✝",
            },
            {
                "num": "2",
                "titulo": "Permita que Ele seja a luz",
                "texto": "Deixe que a Luz de Cristo guie suas escolhas diárias — em relacionamentos, trabalho, família.",
                "icone": "☀",
            },
            {
                "num": "3",
                "titulo": "Fale de Jesus com outras pessoas",
                "texto": "Como André e Filipe, compartilhe o que encontrou. O convite 'Vem e vê' é a evangelização mais simples.",
                "icone": "◎",
            },
            {
                "num": "4",
                "titulo": "Esteja disposto a segui-lo diariamente",
                "texto": "Ser discípulo não é um evento, é um caminho. 'Segue-me' (v.43) é um convite contínuo.",
                "icone": "⟡",
            },
        ],
    },

    "desafio": {
        "titulo": "Desafio da Semana",
        "descricao": "Separe um tempo todos os dias para ler o Evangelho de João e orar pedindo que Deus aumente sua fé e amor por Jesus. Compartilhe com alguém o que você aprendeu.",
        "tarefas": [
            "Leia João 1 inteiro em uma sentada (~10 min). Observe como Jesus é descrito.",
            "Escolha um versículo que te impactou e medite nele 5 min por dia.",
            "Convide uma pessoa para 'vir e ver' — culto, grupo bíblico ou ler João 1 juntos.",
            "Memorize João 1:1 até o final da semana.",
        ],
    },

    "reflexao": {
        "titulo": "Perguntas para Reflexão",
        "perguntas": [
            "O que significa dizer que Jesus é o Verbo eterno?",
            "Por que João Batista afirmou que não era o Cristo?",
            "O que o fato de Jesus se fazer carne revela sobre o amor de Deus?",
            "Por que os primeiros discípulos decidiram seguir Jesus?",
            "Como você pode ser uma 'luz' que aponta outros para Jesus?",
            "Qual parte deste capítulo mais falou ao seu coração?",
        ],
    },

    "memoria": {
        "texto": "No princípio era o Verbo e o Verbo estava com Deus e o Verbo era Deus",
        "ref": "João 1:1",
        "blanks_idx": [2, 5, 8, 11],
    },

    "oracao": {
        "titulo": "Oração Final",
        "texto": (
            "Senhor Jesus, obrigado por vires ao mundo para nos revelar o amor de Deus. "
            "Ajuda-me a te conhecer mais a cada dia, a confiar em ti e a compartilhar "
            "contigo com outras pessoas. Que eu seja uma testemunha da Tua Luz, apontando "
            "outros para Ti como João Batista. Que a Tua graça sobre graça transborde em "
            "minha vida hoje e sempre. Em Teu nome, Amém."
        ),
    },
}
