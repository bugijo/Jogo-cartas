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

## 2026-10-24 — unidade P0: baralho de Viagem

- Criado `edicao-integral/travel02.py`, derivado das 12 cartas VIA do catálogo
  canônico.
- A unidade registra trechos curtos/longos, cartas reveladas, escolhas
  pendentes, Emboscada com mapa e rodada mínima, snapshot e resolução
  idempotente. Não concede recursos nem substitui a resolução tática.
- Testes focados: 5 aprovados. Suíte experimental completa: 129 aprovados,
  0 falhas. `compileall` e `git diff --check`: aprovados.
- Suíte física/legada repetida após a unidade: 51 aprovados, 1 ignorado,
  0 falhas em 169,824 s; permaneceu apenas o `ResourceWarning` conhecido em
  `tests/test_boards06.py:64`.
- Unidade seguinte de P0: resgate agora exige grupo, mapa e zona canônicos,
  consome 1 PA, gera recibo e só altera o abrigo no retorno. Suíte
  experimental após a mudança: 131 aprovados, 0 falhas.
- O próximo bloqueio de P0 é integrar esses recibos à expedição sem escolher
  efeitos implicitamente; P1/P2/P3 continuam bloqueadas.

- Fila persistente criada em `docs/continuity/`; P0 marcado como
  `em_execucao`, P1–P3 como `bloqueada` por dependências verificadas.

## Regra de atualização

Cada unidade deve registrar comando, resultado, commit e próximo bloqueio.
Não registrar como concluída uma tarefa apenas porque seus testes unitários
passaram se o gate de campanha ainda estiver fechado.
