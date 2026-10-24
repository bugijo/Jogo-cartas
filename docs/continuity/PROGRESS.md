# Progresso

## 2026-10-23 — checkpoint remoto `8697db9`

- Expedição tática parcial, carga, retorno, peças e revisitas persistentes.
- Posto/combustível parcial e políticas determinísticas para oito perfis.
- Suíte experimental: 109 testes aprovados.
- Após a integração das políticas, persistência regional e expedição tática:
  suíte experimental atual: 124 testes aprovados.
- Suíte física/legada: 51 aprovados, 1 ignorado, sem falhas na execução com
  dependências e artefatos materializados.
- `compileall` e `git diff --check`: aprovados.
- Simulações: 1.250 ciclos de um dia, restauração divergente 0; 250 defesas
  isoladas, com pré-condições sintéticas.
- Bloqueios P0/P1 permanecem ativos; nenhuma publicação física nova foi
  declarada pronta.

- Fila persistente criada em `docs/continuity/`; P0 marcado como
  `em_execucao`, P1–P3 como `bloqueada` por dependências verificadas.

## Regra de atualização

Cada unidade deve registrar comando, resultado, commit e próximo bloqueio.
Não registrar como concluída uma tarefa apenas porque seus testes unitários
passaram se o gate de campanha ainda estiver fechado.
