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
| D-05 | Fome crônica tardia (T3): ~17–26% nas sobreviventes; testar custo do rodízio e produção do abrigo | D-04 | economia | pendente | T3 na faixa ou meta revista com justificativa |
| D-06 | Personas (18) jogando a Comunidade no regional + avaliação simulada de 10 perguntas por persona, cruzada com métricas | D-04 | ux_pesquisa | pendente | artefato por persona; nada apresentado como opinião humana |
| D-07 | Inventário integral de baralhos (Cisterna, Viagem, Horda, acontecimentos de viagem 12, profissões 12, bagagem D6) → necessidade, quantidades, raridade, campanha | D-04 | card_games | pendente | `edicao-integral/INVENTARIO_CARTAS.md` com contagens que batem com `data/` |
| D-08 | Mapas: inventário dos mapas táticos e do tabuleiro de zonas (floresta/rio/ruínas, não tático); grade 10×10 e encaixes 5×5 | D-07 | board_games | pendente | mapa jogável por campanha; checagem automática de acesso |
| D-09 | Fichas de heróis (10 + 2 ponte) e cartas de sobrevivente/profissão | D-07 | game_designer | pendente | fichas batem com `data/system.json` |
| D-10 | Manual da edição integral (inclui Comunidade) e livro de campanha | D-07..D-09 | narrativa | pendente | exemplos legais conferidos pelo motor |
| D-11 | Kit A4: cartas frente/verso, tokens, tabuleiros, guia de montagem; QA automatizada de PDFs | D-10 | grafico + qa | pendente | inventário físico = baralhos definidos; render conferido |
| D-12 | Validação cega final 91–120 (uma vez, depois de congelar valores) | D-05, D-06 | qa | pendente | relatório sem ajuste posterior |
| D-13 | Playtest humano (`PLAYTEST_HUMANO.md`) | D-11 | ux_pesquisa | bloqueada | precisa de pessoas; fora do alcance do agente |
