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

## 2026-10-24 — baralho persistente de Hordas (base `9773da5`)

- O remoto avançou para `9773da5` com uma reversão explícita das integrações
  posteriores a `690a597`. A branch foi fast-forwardada; nenhum histórico,
  kit físico ou `main` foi alterado. As mudanças revertidas não foram
  reaplicadas. Um replay local não publicado, dependente dos módulos removidos,
  ficou preservado em stash e não foi usado como evidência.
- Implementado `edicao-integral/horde_deck02.py`: composição canônica de nove
  cartas, embaralhamento reproduzível, descarte, reshuffle determinístico e
  validação do estado.
- `Cistern02` mantém o estado do sapato no save. Saves anteriores sem o campo
  migram determinísticamente de `seed + 8102`.
- `Tactical02` agora usa o sapato compartilhado entre locais. Ordem de cartas
  injetável continua disponível somente para fixtures explícitas de teste.
- Testes: suíte experimental `128 passed`; round-trip do `IntegratedCampaign`
  durante uma expedição também passou. `compileall`, validação do catálogo e
  `git diff --check` aprovados.
- A revisão independente apontou a cobertura integrada que faltava; ela foi
  adicionada. Também foi corrigido o fechamento do PNG em `board_art06.crop()`;
  os testes direcionados passaram com `ResourceWarning` tratado como erro.
- Suíte legada pós-correção: `51 passed` com `ResourceWarning` promovido a
  erro. `compileall`, validação do catálogo e `git diff --check` passaram.
- Sem campanha completa, sem `verified_victory` e sem validação física.
- Próximo bloqueio: Viagem/retorno legais, emboscada e ligação dos recibos de
  expedição ao ciclo de cinco dias.

### Hardening de save

- A auditoria de dados não confiáveis encontrou que listas malformadas no
  snapshot do sapato poderiam escapar como `TypeError`. `HordeDeck02` agora
  valida tipo de pilha e valores antes de contar cartas, e rejeita estados
  inválidos com `ValueError`.
- Testes regressivos: experimental `129 passed`; o teste adversarial novo
  reproduz e cobre os formatos malformados. Validação de dados, compilação e
  whitespace passaram. A suíte legada com warnings como erro passou `51/51`
  após a correção do fechamento de PNG.

## 2026-10-24 — sapato canônico de Viagem

- Adicionado `TravelDeck02`, cuja composição deriva dos 12 IDs de família `VIA`
  presentes atualmente em `content/catalog.json`; cada carta aparece uma vez
  até o descarte completo. Seed, descarte e contador de reembaralhamentos são
  determinísticos e salvos dentro de `Cistern02`.
- Saves legados sem os sapatos de Horda e Viagem migram por offsets estáveis da
  seed da campanha. O teste integrado salva/restaura os dois sapatos e uma
  expedição tática suspensa; a migração também foi verificada por arquivo JSON
  schema 1 legado com ambos os campos ausentes.
- Suíte experimental: `130 passed`; validação de dados, `compileall` e
  `git diff --check` passaram.
- Revisão independente somente leitura: nenhum defeito reproduzível no sapato;
  as 12 cartas `VIA` têm IDs únicos no catálogo.
- Limite explícito: o estado de viagem ainda não compra automaticamente uma
  carta por trecho, não aplica efeitos das cartas e não executa M1. Portanto
  não há expedição completa nem vitória certificada.

## 2026-10-24 — recuperação seletiva após auditoria Git

- Conferidos local/remoto `94b6e7c`; os oito SHAs pedidos existem e são
  ancestrais da branch. `9773da5` é o revert que removeu seus arquivos da
  árvore. Não foi feito cherry-pick em massa nem alterada a `main`.
- Recuperados seletivamente Viagem por trecho, Emboscada M1, movimentação e
  combate tático, recursos/equipamentos coletáveis, liquidação de retorno,
  eventos diários, cercos e recibos/certificação da Cisterna. As cartas atuais
  de Horda e Viagem continuam como fontes únicas; duplicações históricas foram
  rejeitadas.
- Migração adicional cobre saves anteriores ao cursor diário: assinala eventos
  passados não auditáveis, aplica somente o evento atual e bloqueia certificado
  canônico para esse save. A migração não fabrica efeitos retroativos.
- O replay fixo H2–H6 foi reconciliado com os eventos canônicos e passa de novo;
  continua sendo uma rota roteirizada, não um replay integral de ações legais.
- Uma prova de expedição individual agora usa seed 22 e o baralho natural: Viagem
  para a Oficina, coleta legal de Conexões e retorno, sem substituir a ordem do
  sapato. Isso demonstra um objetivo tático isolado, não a campanha completa.
- Testes após a recuperação e migração: `220 passed`; `validate_data.py`,
  `compileall` e `git diff --check` passaram. Impressão e playtest humano não
  ocorreram. `RECOVERY_AUDIT.md` contém o inventário de SHAs, decisões e limites.
- Próximo bloqueio: ligar o fluxo público a um executor legal de campanha que
  recolha as peças e retorne com recibos; depois validar as cinco noites e
  emitir `verified_victory` apenas se essa trajetória passar.

## 2026-10-24 — primeira campanha H2 reproduzível

- `c8a4a0f` integrou alocação nominal de trabalhadores, bloqueio de trabalho
  durante expedições, ajuda de resgate paga pela carga física e controle dos
  recibos de retorno; inclui testes de regressão para o ciclo de noite.
- O controlador `campaign_player02.py` utiliza ações públicas do integrador e
  mapas observáveis. Não concede peças, não emite o certificado diretamente e
  não abre envelopes de intenção.
- Seed 22 concluiu cinco dias/noites: Mercado → Oficina → Estação; foram
  entregues Conexões, Bomba e Membrana. Os cinco eventos foram consumidos, os
  cercos de missão e de Pressão foram resolvidos, e o filtro A/B/C ficou ativo
  antes do encerramento. O motor retornou `verified_victory`.
- A rota não acolheu resgatados e não assumiu promessas. Isso não viola o
  capítulo: `CAMPAIGN.md` não exige resgate para vencer e condiciona promessa à
  escolha explícita. A rota não testa a compreensão/execução de promessas.
- `verify_campaign_player02.py` compara o replay determinístico e faz
  save/load terminal. Artefato: `edicao-integral/replays/cisterna_h2_seed22.json`.
- Amostra exploratória de dez seeds teve uma vitória H2, uma derrota parcial,
  emergências e bloqueios do controlador (incluindo carga e logística). Não é
  amostra estatística nem medida de equilíbrio.
- A revisão revelou um erro concreto de seleção do controlador: ele tentava
  resolver custo de material em Viagem sem conferir quantidade. A decisão agora
  exige material suficiente, e o controlador planeja carregar no máximo uma
  unidade já existente no estoque. Isso não muda regras nem concede recursos.
- Estado: campanha legal demonstrada para uma preparação H2; ainda não há
  campanha geral, cobertura H3-H6, resgate/promessa exercitados ou transição
  legal para Última Transmissão. Impressão e playtest humano seguem pendentes.
