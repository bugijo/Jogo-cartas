# Integração de campanhas — estado atual

Fontes oficiais do capítulo inicial: `../RULES.md`, `../CAMPAIGN.md` e `../content/catalog.json`. O motor de `edicao-integral/` não substitui esses arquivos. A primeira caixa ainda pode ser jogada com seus PDFs existentes. `cistern02.py` porta preparação, porções, relógio, filtro, privação, acolhimento e cercos/intenções em um estado separado.

Em 24/10/2026 foi concluído e reproduzido um replay legal H2 da Cisterna, seed 22. Ele parte de preparação normal (`IntegratedCampaign.new`), escolhe dois fundadores, sorteia vínculos pelo baralho embaralhado, executa expedições públicas ao Mercado, Oficina e Estação, transporta e entrega Conexões, Bomba e Membrana, processa os cinco eventos, refeições, os cercos dos dias 3 e 5, conclui as etapas A/B/C e recebe `verified_victory` do validador do motor. O replay e o verificador estão em `replays/cisterna_h2_seed22.json` e `verify_campaign_player02.py`.

Esta evidência comprova uma trajetória H2 específica, não a campanha sob todas as sementes, uma taxa de vitória ou equilíbrio. Nenhum resgate foi necessário na rota escolhida; nenhuma promessa foi assumida. Isso satisfaz a condição oficial “sem pessoa abandonada por promessa” porque `CAMPAIGN.md` condiciona a promessa à escolha explícita do grupo e não exige um resgate para vencer. A rota processou dois cercos (missão no dia 3 e Pressão no dia 5), ambos com recibo; o cerco final causou perda de comida e dano ao portão, mas o grupo continuou abastecido naquela refeição.

Diferenças materiais que impedem ligar os arcos por uma flag sem perder regras:

| Aspecto | Capítulo 0.2 | Motor experimental |
| --- | --- | --- |
| Elenco | 24 fichas, 12 iniciais, vínculos sorteados | dez protagonistas fixos e 15 NPCs de outro catálogo |
| Economia | cartas de quatro porções; C inclui cães; validade e lotes locais | contadores food/water por herói/NPC, sem cães ou abertura de carta |
| Abrigo | Moral, Saúde, Pressão, cercos, acolhimento temporário | estruturas, crises e estoque, sem aqueles três indicadores |
| Tempo | dez segmentos compartilhados por viagem e combate | segmentos regionais, rodadas táticas independentes |
| Objetivo | filtro em etapas A/B/C até dia 5, peças Conexões/Bomba/Membrana | flag `cistern_complete`, sem ficha de projeto ou peças |
| Lugares | seis destinos e quatro módulos impressos por destino | seis locais regionais diferentes, oito plantas funcionais, incluindo as seis geometrias canônicas; Posto e Condomínio ainda sem destino regional |

`Arc2.decode_radio()` exige um `cistern_record` com `verified_victory`; agora o certificado pode ser produzido por uma Cisterna válida, mas ainda não existe uma migração canônica completa que preserve roster, vínculos, moradores, ferimentos, equipamentos e economia. Não se deve fabricar `cistern_record` ou pular a fronteira dos arcos. A próxima tarefa P1 é projetar e testar essa migração a partir do save certificado.

A defesa final já é executável no fluxo contínuo após a transição, mas as ondas e o mapa linear são conteúdo experimental; o ensaio `ENSAIO_DEFESA_20261023.json` ainda injeta requisitos e equipamento e, portanto, não é evidência de equilíbrio.
