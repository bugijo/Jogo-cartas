# Fronteira entre A Cisterna 0.2 e Última Transmissão experimental

Fontes oficiais do capítulo inicial: `../RULES.md`, `../CAMPAIGN.md` e `../content/catalog.json`. O motor de `edicao-integral/` não substitui esses arquivos. A primeira caixa ainda pode ser jogada com seus PDFs existentes. `cistern02.py` porta preparação, porções, relógio, filtro, privação, acolhimento e parte dos cercos/intenções em um estado separado; ainda não há fluxo completo nem importação para `World`.

Diferenças materiais que impedem ligar os arcos por uma flag sem perder regras:

| Aspecto | Capítulo 0.2 | Motor experimental |
| --- | --- | --- |
| Elenco | 24 fichas, 12 iniciais, vínculos sorteados | dez protagonistas fixos e 15 NPCs de outro catálogo |
| Economia | cartas de quatro porções; C inclui cães; validade e lotes locais | contadores food/water por herói/NPC, sem cães ou abertura de carta |
| Abrigo | Moral, Saúde, Pressão, cercos, acolhimento temporário | estruturas, crises e estoque, sem aqueles três indicadores |
| Tempo | dez segmentos compartilhados por viagem e combate | segmentos regionais, rodadas táticas independentes |
| Objetivo | filtro em etapas A/B/C até dia 5, peças Conexões/Bomba/Membrana | flag `cistern_complete`, sem ficha de projeto ou peças |
| Lugares | seis destinos e quatro módulos impressos por destino | seis locais regionais diferentes, oito plantas funcionais, incluindo as seis geometrias canônicas; Posto e Condomínio ainda sem destino regional |

`Arc2.decode_radio()` ainda aceita `cistern_complete` como dado externo. Essa interface **não prova** vitória no capítulo 0.2. Uma integração fiel precisa portar identidade/vínculos, relógio, estoque de porções, resgates, filtro e cerco, com testes cruzados contra os replays existentes, antes de aceitar a transição automaticamente. Não foi aplicada conversão silenciosa nem alteração aos textos oficiais.

A defesa final já é executável de modo isolado, mas as ondas e o mapa linear são conteúdo experimental; o ensaio `ENSAIO_DEFESA_20261023.json` injeta requisitos e equipamento, portanto não é uma campanha de vários dias.
