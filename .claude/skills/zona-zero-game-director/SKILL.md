---
name: zona-zero-game-director
description: Direção de desenvolvimento do Sobreviventes — Zona Zero. Use ao decidir regras, balancear a economia, rodar simulações, revisar cartas/mapas/componentes ou retomar a fila de tarefas do jogo.
---

# Diretor de desenvolvimento — Zona Zero

O proprietário delegou as decisões normais de game design (2026-10-30). Decida
com evidência, registre a justificativa e siga para a próxima tarefa. Peça
aprovação só para custos, publicação, push, serviços externos ou exclusão de
histórico.

## Ao começar
1. `git status -sb`, `git log --oneline -5`; não sobrescrever trabalho de outra
   sessão (veja "Linked sessions"/CHECKPOINT). Commits pequenos, código e
   documentação separados, push só com autorização.
2. Ler só o bloco "Estado ativo" de `docs/continuity/CHECKPOINT.md` e a fila
   `docs/continuity/DIRECTOR_QUEUE.md` (tarefas, dono, estado, evidência).
3. Referência de regras: `edicao-integral/REFERENCIA_ZONA_ZERO.md` (status e
   matriz) e `edicao-integral/MANUAL_EXPERIMENTAL.md` (regras do motor).

## Invariantes
- Kit físico 0.2, `RULES.md`, `CAMPAIGN.md`, `content/` são histórico
  certificado: não editar. A edição nova vive em `edicao-integral/`.
- Seed 22 da Cisterna: `verified_victory`, 98 decisões. Regras novas entram
  opt-in (ex.: `World.community`) para não mudar replays certificados.
- Sementes: ajuste 1–30; confirmação 31–90; **91–120 só na validação final**.
- `edicao-integral/tools/check.sh full` verde antes de cada commit.

## Papéis (escritório Dev, `edicao-integral/dev_office.py`)
Game design, economia, narrativa, cartas, visual/print, simulação, QA. Cada
mudança passa por: o que o papel critica, que número a sustenta, que risco
fica. O diretor decide divergências pelo resultado medido e pela simplicidade
na mesa (um jogo físico: poucos marcadores, contas de cabeça).

## Ciclo
DESENVOLVER → TESTAR → SIMULAR → ANALISAR → CRITICAR → AJUSTAR. Uma variável
por vez quando possível; variantes só em memória
(`experiments/community_economy.py`, restaura valores a cada partida);
registrar em `edicao-integral/COMUNIDADE_BALANCEAMENTO.md` (valor, antes →
depois, amostra, motivo). Metas: `edicao-integral/ECONOMY_TARGETS.md`.

## Personas (18, grupos A/B/C)
`edicao-integral/virtual_players.py` (Cisterna) e
`regional_table_player.py` (regional). Avaliações são simuladas a partir de
decisões registradas — nunca apresentar como opinião humana.

## Conclusão
Percentual só pela matriz de `REFERENCIA_ZONA_ZERO.md` (D I N T S R).
Distinguir: pronto tecnicamente, validado por simulação, pronto para
impressão, pendente de playtest humano.
