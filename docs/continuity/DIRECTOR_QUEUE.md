# Fila do diretor — Zona Zero (persistente)

Retomada: ler a skill `.claude/skills/zona-zero-game-director/SKILL.md`, o
bloco "Estado ativo" do `CHECKPOINT.md` e pegar a primeira tarefa `pendente`
cujas dependências estejam `concluída`. Não replanejar do zero.

| Id | Tarefa | Depende | Dono (papel) | Estado | Evidência / critério de conclusão |
|---|---|---|---|---|---|
| D-01 | Decidir as 5 pendências da Comunidade | — | diretor | concluída | `MANUAL_EXPERIMENTAL.md` §Decisões do diretor |
| D-02 | Suprimento de evacuação (1 ração/consumidor) e heróis em viagens automáticas | D-01 | simulação | concluída | `community.evacuation_supply`, `open_expedition` recusa herói em viagem; testes `test_community` |
| D-03 | Ciclo de balanceamento da economia contra T1–T5 (1–30) | D-02 | balanceamento | concluída | `COMUNIDADE_BALANCEAMENTO.md` ciclos 3–5 |
| D-04 | Confirmação 31–90 dos valores adotados | D-03 | balanceamento | concluída | tabela 31–90 no mesmo documento |
| D-05 | Fome crônica tardia (T3): ~17–26% nas sobreviventes; testar custo do rodízio e produção do abrigo | D-04 | economia | parcial | medido sem efeito: alvo de estoque 3–4 dias, trabalhar com 1 noite de fome, caça por rendimento/dia (`COMUNIDADE_BALANCEAMENTO.md` ciclo 6). Teto = produção sustentável por trabalhador; próxima: D-14 |
| D-06 | Personas (18) jogando a Comunidade no regional + avaliação simulada de 10 perguntas por persona, cruzada com métricas | D-04 | ux_pesquisa | concluída | `AVALIACOES_PERSONAS.md` (60 mesas, 1–10); ampliar para 1–30 antes de D-12 | artefato por persona; nada apresentado como opinião humana |
| D-07 | Inventário integral de baralhos (Cisterna, Viagem, Horda, acontecimentos de viagem 12, profissões 12, bagagem D6) → necessidade, quantidades, raridade, campanha | D-04 | card_games | concluída | `edicao-integral/INVENTARIO_CARTAS.md` com contagens que batem com `data/` |
| D-08 | Mapas: inventário dos mapas táticos e do tabuleiro de zonas (floresta/rio/ruínas, não tático); grade 10×10 e encaixes 5×5 | D-07 | board_games | pendente | mapa jogável por campanha; checagem automática de acesso |
| D-09 | Fichas de heróis (10 + 2 ponte) e cartas de sobrevivente/profissão | D-07 | game_designer | pendente | fichas batem com `data/system.json` |
| D-10 | Manual da edição integral (inclui Comunidade) e livro de campanha | D-07..D-09 | narrativa | pendente | exemplos legais conferidos pelo motor |
| D-11 | Kit A4: cartas frente/verso, tokens, tabuleiros, guia de montagem; QA automatizada de PDFs | D-10 | grafico + qa | pendente | inventário físico = baralhos definidos; render conferido |
| D-12 | Validação cega final 91–120 (uma vez, depois de congelar valores) | D-05, D-06 | qa | pendente | relatório sem ajuste posterior |
| D-13 | Playtest humano (`PLAYTEST_HUMANO.md`) | D-11 | ux_pesquisa | bloqueada | precisa de pessoas; fora do alcance do agente |
| D-14 | Estrutura de produção sustentada do meio de jogo (ex.: 2ª Horta ou canteiro que exige trabalhador) para baixar a fome tardia sem recurso grátis | D-05 | economia | parcial | Canteiro adotado: fome tardia 13,2→10,4% (1–30), 18,9→14,4% (31–90); T3 ainda falha; próxima: D-16 | fome tardia ≤ 10% em 1–30 e 31–90 sem perder T1/T4 |
| D-15 | Exploração tática perde motivo depois do Mercado (heróis em descanso/viagem 68% dos dias): local tático de comida/floresta com risco próprio | D-06 | board_games + game_designer | pendente | dias táticos > 40% nas mesas de personas sem baixar T1 |
| D-16 | Grupos pequenos (H2–H3) sobrevivem bem menos (31–90: 2/7, 11/28): avaliar migração proporcional (crianças/cães) ou bônus de escala sem recurso grátis | D-14 | economia + narrativa | pendente | H2–H3 ≥ 40% sem baixar H4–H6 abaixo de T1 |
