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
  experimental após a mudança: 132 aprovados, 0 falhas (inclui o commit
  remoto `052ada0`, que adicionou uma proteção de ordem futura).
- O próximo bloqueio de P0 é integrar esses recibos à expedição sem escolher
  efeitos implicitamente; P1/P2/P3 continuam bloqueadas.

## 2026-10-24 — unidade P0: efeitos de Viagem

- `TravelContext` agora aplica efeitos automáticos e escolhas das cartas VIA
  por direção, com validação antecipada de comida, água e material, sem
  mutação parcial em falhas.
- São registrados pressão, moral, fadiga, rota conhecida, Ponte, material
  deixado/recuperado e carta de retorno ignorada quando aplicável.
- Testes focados: 7 aprovados. Suíte experimental: 134 aprovados, 0 falhas.
- Próximo bloqueio: conectar o contexto aos recursos carregados da expedição
  e resolver a Emboscada no mapa M1.

## 2026-10-24 — unidade P0: Emboscada M1

- Criado `edicao-integral/ambush02.py` com mapa reduzido canônico, equipes na
  zona 1, Errantes em zona 6, porta 1–5 fechada, PA, movimento, combate,
  ativação inimiga, ferimentos, rodada obrigatória, retorno sem cobrança
  adicional e save/load.
- Testes focados: 3 aprovados. Suíte experimental: 140 aprovados, 0 falhas.
- O módulo ainda aguarda ligação ao `Travel02` e ao relógio da expedição; não
  foi usado para fabricar uma vitória de campanha.

- Fila persistente criada em `docs/continuity/`; P0 marcado como
  `em_execucao`, P1–P3 como `bloqueada` por dependências verificadas.

## Regra de atualização

Cada unidade deve registrar comando, resultado, commit e próximo bloqueio.
Não registrar como concluída uma tarefa apenas porque seus testes unitários
passaram se o gate de campanha ainda estiver fechado.

## 2026-10-24 — Continuação após avanço remoto

- O remoto avançou de `690a597` para `1ca38ea` com `Travel02` e seus recibos.
  Foi preservado e integrado por rebase sem force push; commit local de
  observações sem informação oculta foi publicado como `052ada0`.
- Uma tentativa local de deck paralelo foi removida por duplicar a interface
  `Travel02` recém publicada.
- Corrigida a falha em que peça única carregada se perdia na emergência e podia
  ser duplicada: o estado local registra o item no objetivo canônico, e a
  próxima expedição recupera por 1 PA. Teste integrado passa por save/load e
  comprova entrega única no dia 2.
- Testes atuais: experimental 133/133; legado 51/51; compileall, validação de
  dados e diff-check aprovados.
- Próximo bloqueio: conectar `Travel02` ao relógio/tático e executar efeitos,
  incluindo a emboscada M1, sem pagar trecho duas vezes. Nenhuma campanha foi
  simulada ou certificada neste lote.

## 2026-10-24 — atualização sobre base remota `052ada0`

- O remoto incorporou `Travel02` e testes determinísticos durante a sessão; a
  branch foi reconciliada sem reescrita forçada. O deck alternativo iniciado no
  workspace foi descartado como redundante, preservando o módulo canônico.
- Fechada localmente a falha de recuperação de peças únicas: estado no chão,
  bloqueio contra cópia, recuperação por 1 PA, entrega após retorno e save/load.
- Políticas usam informação pública e não recomendam arrombamento sem ferramenta.
- 135 testes da suíte experimental e 51 da suíte legada passaram; resta o aviso
  `ResourceWarning` em `tests/test_boards06.py:64`. Build Python, validação de
  conteúdo e diff-check passaram.
- Este lote permanece sem commit até concluir a revisão independente final.

## 2026-10-24 — fast-forward até `e6af1f7`

- A branch remota avançou com `afdc82c` (recibos de resgate no mapa) e
  `e6af1f7` (checkpoint correspondente). Os arquivos táticos e de campanha
  foram reconciliados com a correção local de peças de missão.
- A suíte experimental agora passa com 135 testes nessa base; `Travel02` ainda
  é infraestrutura isolada e não integra relógio, efeitos ou M1.
- A auditoria da peça única continua pendente de resposta independente final;
  nenhuma campanha completa foi rodada neste lote.
- A revisão independente não encontrou exploração no caminho canônico, mas
  pediu cobertura do save/load depois da recuperação e antes da entrega. O teste
  integrado agora salva/restaura nesse ponto e verifica a entrega única.

## 2026-10-24 — unidade P0: entrada de viagem e M1

- `IntegratedCampaign` agora oferece entrada explícita de viagem: cada trecho
  precisa ser revelado e resolvido antes do mapa; escolhas pendentes bloqueiam
  a entrada; snapshots preservam viagem, carga e Emboscada.
- Uma Emboscada M1 concluída atualiza o relógio real uma vez e a entrada no
  mapa usa `travel_paid`, evitando cobrança duplicada do trecho.
- Testes focados de entrada, save/load e M1; suíte experimental: 143
  aprovados, 0 falhas.
- O retorno ainda não consome o baralho de volta nem aplica todos os efeitos
  ao estoque real; a certificação da campanha continua bloqueada.

## 2026-10-24 — correções de relógio, grafo e ferimentos da M1

- A ida longa agora registra quantos trechos foram efetivamente iniciados e
  cobra os trechos restantes na entrada tática. Uma emboscada cobra os trechos
  revelados antes de começar, mais uma rodada M1; o teste cobre o percurso longo.
- A perseguição da Emboscada agora usa as conexões reais de M1; inimigos diante
  da porta comum fechada 1–5 gastam uma ativação para abri-la. Auditoria
  independente confirmou a topologia e a regra da porta.
- Ferimentos da Emboscada são transferidos aos fundadores ao completar o recibo
  de retorno. Um teste reproduz o ferimento e verifica persistência no estado da
  campanha.
- Travel02 bloqueia nova carta até aplicar a ocorrência anterior; testes
  cobrem autoefeitos, opções de retorno, material e cão elegível no contexto.
- Testes: suíte experimental 151/151; kit legado 51/51 (77 s; persiste o aviso
  de recurso aberto em `tests/test_boards06.py:64`); `compileall`, validação do
  catálogo (125 IDs únicos) e `git diff --check` passaram.
- Não foram executadas partidas completas/simulações de campanha. A integração
  de surgimento/Horda, ruído, fadiga noturna, combate equipado, retorno da
  viagem, eventos diários e vitória da Cisterna permanece pendente. Impressão e
  playtest humano não ocorreram.
- Este checkpoint local ainda não está publicado; conferir o remoto antes do
  commit/push.

## 2026-10-24 — unidade P0: retorno e liquidação de estoque

- A campanha preserva o estado `Travel02` após entrar no mapa e o retoma na
  volta. Cada trecho de retorno é revelado uma vez; escolhas pendentes impedem
  a entrega até resolução explícita.
- O efeito de Ferragens agora incrementa Materiais somente depois do retorno
  tático legal. Perdas de comida/água, pressão e moral ficam liquidadas no
  abrigo a partir do delta do contexto de carga.
- Testes focados de retorno automático e retorno com escolha pendente; suíte
  experimental: 153 aprovados, 0 falhas.
- Ainda faltam Emboscada de retorno, efeitos de cão/Ponte persistentes e a
  integração das cinco noites.

## 2026-10-24 — unidade P1: certificado de vitória da Cisterna

- `Cistern02.certify_victory()` agora transforma `candidate_victory` em
  `verified_victory` somente com os recibos `Oficina:Conexões`,
  `Estação:Bomba` e `Estação:Membrana`.
- `IntegratedCampaign.complete_cistern()` não aceita flags de filtro ou
  recursos sintéticos; sem recibos legais permanece bloqueado.
- Suíte experimental: 155 aprovados, 0 falhas; `compileall` e
  `git diff --check` aprovados.
- A certificação positiva de uma campanha completa ainda não foi declarada:
  eventos, cercos, cinco noites e migração de estado continuam pendentes.
