# Revisão reproduzível da campanha — cinco dias

Regras e catálogo da edição 0.2 preservados. Quinze ensaios de **fases** (H=2–6, três sementes cada) registram preparação, carga prevista, provisões, confrontos amostrados, resgates, fila de cerco, trabalhos e filtro ao longo dos cinco dias. São ensaios determinísticos para achar lacunas, **não partidas táticas completas nem evidência de equilíbrio**. Perfil favorável recusa resgates opcionais e prioriza abastecimento; difícil acolhe Jana; limite seleciona vínculos de maior consumo e tenta os três resgates. Os dados e cercos continuam determinados pela semente, por isso um perfil favorável também pode encontrar uma rolagem ruim.

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
| 2 | favoravel | 2101 | 3 | 0 | ativo | comida 1, água 7, Saúde 5, Moral 4 | plano possível |
| 2 | dificil | 2202 | 4 | 1 | ativo | comida 0, água 2, Saúde 3, Moral 5 | derrota/bloqueio: falta de porções |
| 2 | limite | 2303 | 5 | 3 | ativo | comida 0, água 3, Saúde 3, Moral 4 | derrota/bloqueio: falta de porções |
| 3 | favoravel | 3101 | 5 | 0 | ativo | comida 11, água 21, Saúde 5, Moral 5 | plano possível |
| 3 | dificil | 3202 | 4 | 1 | ativo | comida 0, água 2, Saúde 3, Moral 4 | derrota/bloqueio: herói incapacitado na amostra, falta de porções |
| 3 | limite | 3303 | 7 | 3 | ativo | comida 0, água 5, Saúde 2, Moral 3 | derrota/bloqueio: falta de porções |
| 4 | favoravel | 4101 | 9 | 0 | ativo | comida 7, água 29, Saúde 5, Moral 5 | plano possível |
| 4 | dificil | 4202 | 5 | 1 | ativo | comida 0, água 11, Saúde 4, Moral 5 | derrota/bloqueio: herói incapacitado na amostra, falta de porções |
| 4 | limite | 4303 | 9 | 1 | ativo | comida 1, água 19, Saúde 2, Moral 2 | plano possível |
| 5 | favoravel | 5101 | 7 | 0 | ativo | comida 5, água 19, Saúde 5, Moral 5 | derrota/bloqueio: herói incapacitado na amostra |
| 5 | dificil | 5202 | 9 | 1 | ativo | comida 1, água 19, Saúde 5, Moral 5 | plano possível |
| 5 | limite | 5303 | 11 | 1 | ativo | comida 0, água 17, Saúde 1, Moral 2 | derrota/bloqueio: falta de porções |
| 6 | favoravel | 6101 | 11 | 0 | ativo | comida 5, água 27, Saúde 5, Moral 5 | plano possível |
| 6 | dificil | 6202 | 11 | 1 | ativo | comida 0, água 17, Saúde 4, Moral 5 | derrota/bloqueio: falta de porções |
| 6 | limite | 6303 | 13 | 1 | ativo | comida 1, água 27, Saúde 2, Moral 2 | plano possível |

Cada registro completo, com dados, cargas, estoque antes/depois, cerco e resgate, está em [CAMPANHA_SEMENTES.json](CAMPANHA_SEMENTES.json). As sementes são fixas; repetir o script gera o mesmo resultado. Um plano possível só demonstra que esses saldos de fases não se contradizem; o movimento e os efeitos de todas as cartas não foram resolvidos.

## Replay tático herdado

| H | Resultado | Evidência |
|---:|---|---|
| 2 | PASS | roteiro Lia/Ivo terminou cinco dias |
| 3 | BLOCKED | ('Mercado', 4, 'Lia', 'PA', 0, 1) |
| 4 | BLOCKED | ('Mercado', 4, 'Lia', 'PA', 0, 1) |
| 5 | BLOCKED | ('Mercado', 4, 'Lia', 'PA', 0, 1) |
| 6 | BLOCKED | ('Mercado', 4, 'Lia', 'PA', 0, 1) |

**Partidas integrais certificadas: 0/5 tamanhos.** O roteiro de Lia/Ivo de `src/review_five_days.py` percorre uma trajetória específica de cinco dias em H=2, sem exercer resgates. Ao aplicar o número correto de inimigos iniciais `ceil(H/2)`, o roteiro fixo H=3–6 para no Mercado, rodada 4: Lia precisa de 1 PA depois de chegar a 0. **Isso comprova falha de cobertura do replay, não que a campanha seja impossível nesses grupos.** O próximo trabalho é escrever ações legais para heróis adicionais e verificar todas as zonas, dados, cartas de Viagem/Horda e consequências. Nenhuma dificuldade foi ajustada nesta rodada.

## Componentes e limites

- [COMPONENTES_POR_GRUPO.json](COMPONENTES_POR_GRUPO.json) confere os 114 IDs, fichas e peões, 24 marcadores de inimigos, seis Pés de cabra e substituições de fórmula. Não houve esgotamento de carga nem de 24 marcadores nos ensaios de fases; isso não cobre picos posicionais do mapa.
- Regras §6: ao surgir o 25º inimigo simultâneo, a expedição é perdida e oferece retirada de emergência. Antes disso, falta de token físico usa token numerado e registro. Regras §7: falta de carta física de recurso usa ficha numerada de igual valor; cartas vazias retornam à reserva. Esses procedimentos foram conferidos no texto, não exercitados fisicamente.
- O registro impresso usa L/I como exemplos. O guia de impressão agora explicita que H3–H6 escrevem ID ou nome do herói no campo Local; T08/T09 recebem barracas iniciais para H5/H6. É esclarecimento de preenchimento, sem mudança de mecânica.
- Os ensaios de fases simplificam posições, PA táticos, cansaço, ferimentos individuais ao longo de dias, efeitos completos de Viagem/Busca, intenções verificadas e transporte de resgatados. Por isso nenhuma linha da tabela certifica uma vitória.
- Impressão física, duplex real, montagem e playtest humano não ocorreram.

**Estado:** campanha não validada integralmente para H=2–6. O grupo H=2 tem um replay tático favorável parcial existente; H3–H6 ainda exigem replay tático novo. Os 15 ensaios de fases estão completos e servem para orientar esse trabalho.
