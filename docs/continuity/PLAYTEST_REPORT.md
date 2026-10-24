# Laboratório de jogadores automatizados

## Estado atual

Há oito políticas programáticas em `edicao-integral/player_policies02.py`:
Conservador, Explorador, Construtor, Combatente, Líder, Iniciante,
Oportunista e Adversarial. Cada uma escolhe destino, equipe apta e rota a
partir de estado público e registra justificativa. A escolha local parcial
considera posição, PA, portas, inimigos e objetivo observado. O teste cobre
40 aberturas reproduzíveis (8 políticas × 5 tamanhos H2–H6) e execução de uma
ação legal.

As políticas recebem cópias observáveis via `observe_campaign()` e
`observe_tactical()`, que não incluem a ordem futura dos baralhos de Saque ou
Horda. Isso reduz acesso acidental à informação oculta; ainda é preciso manter
essas fronteiras no simulador completo.

## O que esses dados significam

São decisões iniciais e testes locais. Não houve replays completos de cinco
dias, medição de vitória/derrota por estratégia, ou partidas com variação de
eventos e decisões. Nenhum resultado é taxa de vitória ou teste de equilíbrio.
O agente delegado que iniciou os testes de políticas atingiu o limite de uso;
as políticas e testes foram concluídos pelo agente principal, sem atribuir-lhe
execução que não ocorreu.

## Próximo gate

O motor precisa executar expedição, Saque, cartas Viagem, resgate, noite,
consumo, construção e vitória desde estado inicial antes de rodar lote de
campanha. Em seguida, cada replay deve registrar semente, decisões legais,
estoque por dia, ferimentos, mortes, missão, encerramento e hash do estado
após salvamento/restauração.

Playtest humano segue pendente.

## Regressão do motor, 2026-10-24

- `python -m unittest discover -s edicao-integral/tests -q`: 151 testes
  passaram, incluindo relógio de viagem curta/longa, pré-condições da M1,
  movimento por grafo, porta M1 e persistência de ferimentos no retorno.
- `python -m unittest discover -s tests -v`: 51 testes passaram em 77 s; o
  teste de renderização legado emitiu `ResourceWarning` por não fechar
  `assets/v0.6/bancada_topo.png` (`tests/test_boards06.py:64`).
- `python -m compileall -q edicao-integral src`, validação do catálogo e
  `git diff --check` passaram.
- Estes testes são unitários/de integração de módulos. Não são jogadores
  automatizados concluindo campanha: não foram medidos vitórias, derrotas,
  duração de mesa, escassez de campanha, diversão ou equilíbrio.
- A M1 segue incompleta quanto a surgimento/Horda, pressão, Horda noturna,
  fadiga noturna, combate equipado e ruído. Campanhas completas H2–H6,
  impressão física e playtest humano permanecem pendentes.

## Incremento 2026-10-24 — QA de persistência e política de informação

- Suíte experimental após integrar recibos de resgate da base remota mais
  recente: `python -m unittest discover -s edicao-integral/tests -q`; 135
  testes passaram.
- A validação de dados passou: 125 IDs, 10 heróis, 70 habilidades, 15 NPCs,
  7 estruturas, 6 locais, 5 crises, 1 veículo, 8 mapas táticos.
- Caso adversarial corrigido: retirada com peça única, salvamento do estado do
  local, nova expedição, recuperação por 1 PA e entrega sem duplicação.
- A cobertura inclui save/load após a recuperação e antes do retorno ao abrigo,
  verificando que a carga persiste, não pode ser recolhida de novo e é entregue
  uma única vez.
- `Travel02` mantém testes próprios de sequência, escolha explícita, emboscada
  pendente e restauração. Não está conectado ao fluxo de expedição.
- O resgate no mapa tem recibo e entrega integrados por `afdc82c`; promessas e
  intenções ainda não passaram por uma campanha completa.
- Não foram simuladas campanhas nem inferidas taxas de vitória. A integração
  VIA/campanha continua pendente; essas aprovações não cobrem A Cisterna ou
  Última Transmissão.

## Revisão de regressão 2026-10-24

- 135 testes experimentais passaram; 51 testes legados passaram.
- A suíte legada emitiu um aviso de recurso aberto em
  `tests/test_boards06.py:64`; não houve falha.
- Simulações de campanha completas não foram executadas, pois o motor ainda não
  integra o fluxo de Viagem e a campanha não é alcançável por trajetória legal
  comprovada. Os testes acima são regressões de módulos, não resultados de jogo.
