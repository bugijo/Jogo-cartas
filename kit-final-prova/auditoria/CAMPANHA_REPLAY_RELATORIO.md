# Revisão reproduzível da campanha — cinco dias

Regras e catálogo da edição 0.2 preservados. Quinze ensaios de **fases** (H=2–6, três sementes cada) registram preparação, carga prevista, provisões, confrontos amostrados, resgates, fila de cerco, trabalhos e filtro ao longo dos cinco dias. São ensaios determinísticos para achar lacunas, **não partidas táticas completas nem evidência de equilíbrio**. Perfil favorável recusa resgates opcionais e prioriza abastecimento; difícil acolhe Jana e recebe `ZC-VIA-0007` (+1 Pressão) no dia 2; limite seleciona vínculos de maior consumo e tenta os três resgates. Os dados e cercos continuam determinados pela semente, por isso um perfil favorável também pode encontrar uma rolagem ruim.

## Preparação

| Pessoas | Heróis | Vínculos examinados | Vagas | Consumidores possíveis | Resultado |
|---:|---:|---:|---:|---:|---|
| 1 | 2 | 66 | 8 | 2–5 | cabem |
| 2 | 2 | 66 | 8 | 2–5 | cabem |
| 3 | 3 | 220 | 8 | 3–7 | cabem |
| 4 | 4 | 495 | 8 | 4–9 | cabem |
| 5 | 5 | 792 | 10 | 6–11 | cabem |
| 6 | 6 | 924 | 12 | 8–13 | cabem |

Solo controla dois heróis. Os 12 vínculos foram usados sem reposição; H5/H6 acrescentam uma/duas barracas iniciais.

## Ensaios com sementes

| H | Perfil | Semente | C inicial | Resgates aceitos | Filtro | Noite 5 | Resultado / causa |
|---:|---|---:|---:|---:|---|---|---|
| 2 | favoravel | 2101 | 3 | 0 | ativo | comida 1, água 6, Saúde 5, Moral 4 | plano possível |
| 2 | dificil | 2202 | 4 | 1 | ativo | comida 0, água 2, Saúde 3, Moral 5 | derrota/bloqueio: falta de porções |
| 2 | limite | 2303 | 5 | 3 | ativo | comida 0, água 2, Saúde 3, Moral 4 | derrota/bloqueio: falta de porções |
| 3 | favoravel | 3101 | 5 | 0 | ativo | comida 11, água 20, Saúde 5, Moral 5 | plano possível |
| 3 | dificil | 3202 | 4 | 1 | ativo | comida 0, água 2, Saúde 3, Moral 4 | derrota/bloqueio: herói incapacitado na amostra, falta de porções |
| 3 | limite | 3303 | 7 | 3 | ativo | comida 0, água 4, Saúde 2, Moral 3 | derrota/bloqueio: falta de porções |
| 4 | favoravel | 4101 | 9 | 0 | ativo | comida 7, água 28, Saúde 5, Moral 5 | plano possível |
| 4 | dificil | 4202 | 5 | 1 | ativo | comida 0, água 10, Saúde 4, Moral 5 | derrota/bloqueio: herói incapacitado na amostra, falta de porções |
| 4 | limite | 4303 | 9 | 1 | ativo | comida 1, água 18, Saúde 2, Moral 2 | plano possível |
| 5 | favoravel | 5101 | 7 | 0 | ativo | comida 5, água 18, Saúde 5, Moral 5 | derrota/bloqueio: herói incapacitado na amostra |
| 5 | dificil | 5202 | 9 | 1 | ativo | comida 1, água 18, Saúde 5, Moral 5 | plano possível |
| 5 | limite | 5303 | 11 | 1 | ativo | comida 0, água 16, Saúde 1, Moral 2 | derrota/bloqueio: falta de porções |
| 6 | favoravel | 6101 | 11 | 0 | ativo | comida 5, água 26, Saúde 5, Moral 5 | plano possível |
| 6 | dificil | 6202 | 11 | 1 | ativo | comida 0, água 16, Saúde 4, Moral 5 | derrota/bloqueio: falta de porções |
| 6 | limite | 6303 | 13 | 1 | ativo | comida 1, água 26, Saúde 2, Moral 2 | plano possível |

Cada registro completo, com dados, cargas, estoque antes/depois, cerco e resgate, está em [CAMPANHA_SEMENTES.json](CAMPANHA_SEMENTES.json). As sementes são fixas; repetir o script gera o mesmo resultado. Um plano possível só demonstra que esses saldos de fases não se contradizem; o movimento e os efeitos de todas as cartas não foram resolvidos.

## Replay tático herdado

| H | Resultado | Evidência |
|---:|---|---|
| 2 | PASS | roteiro Lia/Ivo terminou cinco dias |
| 3 | BLOCKED | ('Mercado', 4, 'Lia', 'PA', 0, 1) |
| 4 | BLOCKED | ('Mercado', 4, 'Lia', 'PA', 0, 1) |
| 5 | BLOCKED | ('Mercado', 4, 'Lia', 'PA', 0, 1) |
| 6 | BLOCKED | ('Mercado', 4, 'Lia', 'PA', 0, 1) |

Esse é o **roteiro herdado**, preservado para explicar a lacuna encontrada. Ao aplicar `ceil(H/2)`, Lia fica sem 1 PA no Mercado/rodada 4 para H3–6. O roteiro novo abaixo usa Caio como expedicionário adicional e resolve essa lacuna sem mudar regra ou atributo.

## Trajetórias táticas novas — cinco dias

| H | Estado | C inicial | Resgate | Busca | Relógios M/O/E | Estoque final comida/água |
|---:|---|---:|---|---|---|---|
| 2 | vitória na trajetória fixa | 5 | Bia | nenhuma | 7/8/9 | 7/16 |
| 3 | vitória na trajetória fixa | 5 | Bia | Mercado B1 | 8/8/9 | 7/16 |
| 4 | vitória na trajetória fixa | 5 | Bia | Mercado B1 | 8/8/9 | 7/16 |
| 5 | vitória na trajetória fixa | 6 | Bia | Mercado B1 | 8/8/9 | 2/13 |
| 6 | vitória na trajetória fixa | 8 | nenhum | Mercado B1 | 8/8/9 | 0/15 |

As cinco trajetórias passaram com dados de ataque 3, ordem de Horda registrada e cartas de Viagem distintas de efeito nulo/recusado (Ponte foi descoberta). O retorno da Estação ocorre no segmento 9: cada expedicionário recebe 1 fadiga; a Viagem extra `ZC-VIA-0002` retira 1 porção de água levada, e o descanso alimentado remove a fadiga no amanhecer do dia 4. Todas as portas, saídas, PA, cargas, IA, ferimentos e o limite de dez segmentos foram conferidos nas três expedições. A intenção Solidário de Bia foi revelada após duas noites para H2–5; H6 optou por não acolher. O cerco de missão Força 4 e o cerco de Pressão por `ZC-CER-0001` foram resolvidos antes dos trabalhos, com dados de vigia anotados. Os trabalhos A/B/C do filtro ocorreram nos dias 4–5. Heróis expedicionários recebem 2 XP por retorno com objetivo (6 XP em três visitas); as escolhas das marcas 3 e 6 XP ficam registradas por pessoa, sem transferir ferimentos. H6 termina com estoque de comida zero **após** alimentar todos os consumidores da quinta noite; é um caso de margem nula, não falta de refeição. Os estados por rodada estão em [ROTEIROS_TATICOS_H2_H6.json](ROTEIROS_TATICOS_H2_H6.json).

## Esgotamentos observados

- food: estoque zerou em 7/15 ensaios de fases.
- water: estoque zerou em 4/15 ensaios de fases.
- materials: estoque zerou em 15/15 ensaios de fases.
- ammo: estoque zerou em 9/15 ensaios de fases.
- Faltou pelo menos uma porção em 7/15 ensaios; estoque zero **após** uma refeição completa não é privação.
- Os três Materiais iniciais saem do estoque ao reservar A/B/C; o projeto mantém esses custos. Munição zero retira somente o bônus de cerco. Sem carta física de recurso suficiente, o manual manda usar ficha numerada anotada de mesmo valor; isso não repõe porções gastas.
- Nenhum ensaio exigiu o 25º inimigo simultâneo. Se ocorrer, a regra determina expedição perdida e retirada de emergência; não há limite aumentado nesta revisão.

Isto demonstra **uma vitória alcançável por tamanho de grupo** nas escolhas indicadas. As 15 sementes acima cobrem outras condições em nível de fases, incluindo perdas. Não há replay tático para cada semente nem para todos os efeitos do baralho; as trajetórias não estimam a chance de vencer. Nenhuma dificuldade foi ajustada nesta rodada.

## Componentes e limites

- [COMPONENTES_POR_GRUPO.json](COMPONENTES_POR_GRUPO.json) confere os 114 IDs, fichas e peões, 24 marcadores de inimigos, seis Pés de cabra e substituições de fórmula. Não houve esgotamento de carga nem de 24 marcadores nos ensaios de fases; isso não cobre picos posicionais do mapa.
- Regras §6: ao surgir o 25º inimigo simultâneo, a expedição é perdida e oferece retirada de emergência. Antes disso, falta de token físico usa token numerado e registro. Regras §7: falta de carta física de recurso usa ficha numerada de igual valor; cartas vazias retornam à reserva. Esses procedimentos foram conferidos no texto, não exercitados fisicamente.
- O registro impresso usa L/I como exemplos. O guia de impressão agora explicita que H3–H6 escrevem ID ou nome do herói no campo Local; T08/T09 recebem barracas iniciais para H5/H6. É esclarecimento de preenchimento, sem mudança de mecânica.
- Os ensaios com sementes simplificam posições, PA táticos, cansaço, ferimentos individuais ao longo de dias, efeitos completos de Viagem/Busca, intenções verificadas e transporte de resgatados. A trajetória tática fixa usa apenas uma seleção legal desses efeitos.
- Impressão física, duplex real, montagem e playtest humano não ocorreram.

**Estado:** cinco trajetórias fixas de cinco dias concluídas, uma por H=2–6. A campanha continua sem validação ampla de equilíbrio, efeitos alternativos, impressão física e playtest humano. Os 15 ensaios de fases estão completos e orientam os próximos casos táticos.
