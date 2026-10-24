# Auditoria independente — ciclo 2026-10-23

## Escopo auditado

Base remota inicial `8697db9`, avançada por fast-forward para `690a597`; código
dos módulos `cistern02.py`, `cistern_tactics02.py`, `integrated_campaign.py`,
catálogo legado `content/catalog.json`, regras `RULES.md` e campanha
`CAMPAIGN.md`.

## Evidência objetiva

- Um teste fixo percorre Oficina e Posto com ações legais no mapa, porta, PA,
  Bateria coletada e quatro cartas de combustível. Resultado: retorno em van
  com relógio em 8 após dado favorável 6 no reparo.
- Outro teste percorre uma busca no Mercado, confere o ID da carta e o saldo
  que chega ao abrigo somente após retorno.
- Coleta sem expedição e transição por `candidate_victory` foram fechadas após
  auditoria detectar os atalhos no remoto `8700073`.
- Fadiga de emergência agora persiste na pessoa e reduz no amanhecer se
  alimentada/hidratada.
- A geometria de seis mapas é comparada ao catálogo; Posto e Condomínio deixam
  de ser somente referência para a camada tática.

## Limites ainda críticos

- Falta Viagem/emboscada completa, promessas, eventos dos cinco dias, trabalhos
  e encerramento noturno integrado. A base remota `afdc82c` vincula recibos de
  resgate aos mapas; o ciclo completo de acolhimento ainda está incompleto.
- Revisitas preservam planta, busca e van, mas estados de grupos e promessas
  ainda não têm interação tática.
- A transição não migra todo estado para `World` e não emite
  `verified_victory`; Última Transmissão não é alcançável legitimamente.
- O teste da van é uma rota fixa com resultado de dado favorável. Não estima
  chance de sucesso, dificuldade ou diversão.
- As políticas automáticas ainda não completam partidas.
- A auditoria apontou que o objeto de motor expunha ordem futura de Saque e
  Horda às políticas. `observe_campaign()` e `observe_tactical()` agora entregam
  recortes sem essas ordens; o teste confirma que os dados ocultos não aparecem.

## Revisão incremental em `690a597` e rebase até `e6af1f7`

- A tentativa inicial de teste de Viagem esperava `Tactical02.travel_log`, que
  não existia. O teste de integração prematuro foi removido; não foi criada uma
  passagem falsa de cartas pela expedição.
- O remoto avançou durante esta sessão até `e6af1f7`, publicando `Travel02`
  (`ad297a9`) com recibos, escolhas e estado de emboscada pendente, além de
  recibos de resgate (`afdc82c`). A tentativa
  local redundante `travel_deck02.py` foi descartada em favor dessa fonte
  canônica mais recente. `Travel02` **ainda não está ligado** ao relógio e ao
  fluxo da expedição; a resolução ainda emite efeitos, sem aplicá-los a
  `Cistern02`; a emboscada ainda não executa M1 no motor tático.
- Auditoria independente encontrou falha crítica: peças únicas carregadas
  durante retirada de emergência eram apagadas e podiam ser recolhidas de novo
  do estoque inicial. `Tactical02` agora as deixa no objetivo canônico, salva a
  peça em `part_ground`, bloqueia cópia na origem e permite recuperação por 1
  PA. O integrador registra a peça como perdida até a recuperação e só a aceita
  no abrigo após retorno legal.
- Prova: testes tático e integrado cobrem emergência, local original, uma
  recuperação única, PA, entrega, round-trip de salvamento e ausência de cópia.
- O auditor independente confirmou não haver exploit no fluxo canônico. Ele
  apontou a ausência de save/load depois da recuperação e antes da entrega; o
  teste integrado agora cobre esse limite, impedindo nova coleta após restauração
  e comprovando uma única entrega.
- A suíte experimental após a integração remota de resgates passou com 135
  testes; a suíte legada está em reexecução antes da publicação deste lote.
- O teste que fora adicionado esperando `Tactical02.travel_log` foi removido,
  pois essa integração não existe; a cobertura de viagem permanece na suíte
  própria `test_travel02.py` e é descrita como parcial.

## Classificação

Revisão de código e testes automatizados; não é auditoria independente de
campanha completa. Impressão, equilíbrio e playtest humano não foram feitos.

## Lote local após a base remota `052ada0`

- Auditoria independente identificou perda e duplicação potencial de peças
  únicas quando a expedição terminava por emergência. O código agora persiste
  a peça no objetivo canônico, valida sua zona/carga, impede reposição da cópia
  inicial e libera recuperação por 1 PA. O integrador contabiliza recibo de
  recuperação somente após retorno.
- Testes dirigidos reproduzem emergência, save/load, recuperação e uma única
  entrega; entradas de estado adulteradas com zona/carga incompatíveis falham.
- O deck existente `Travel02` foi preservado. O lote não criou um módulo
  concorrente; seguem pendentes a integração ao relógio, aplicação efetiva dos
  efeitos e execução tática da Emboscada M1.
- Uma decisão automatizada sem ferramenta para arrombar porta bloqueada foi
  identificada e coberta por teste; equipamento agora consta no recorte público.

## Auditoria incremental — viagem/M1, 2026-10-24

- Reproduzido o defeito de cobrança: uma emboscada em rota longa podia iniciar
  sem registrar todos os trechos revelados. O estado passou a contar trechos
  pagos; antes da M1, o integrador cobra a diferença da ida e reserva uma
  rodada, evitando dupla cobrança ao entrar no destino. Testes de rota curta e
  longa verificam o relógio.
- Reproduzida perseguição pelo rótulo numérico de zona, que não representa
  distância. M1 agora procura o caminho mínimo no grafo canônico e desempata
  alvos por zona/ID; uma porta comum fechada consome uma ativação para abrir.
  Revisão independente leu `RULES.md` §38 e confirmou correspondência no trecho
  alterado; não executou testes próprios.
- Reproduzida perda de ferimentos M1 ao voltar ao `Cistern02`. O recibo agora
  transfere ferimentos ao fundador, limitado ao máximo de 3. Teste integrado
  reproduz dano, retorno e persistência.
- A suíte experimental passou com 151 testes; o kit legado, com 51. A validação
  de conteúdo, `compileall` e `git diff --check` também passaram.
- Lacunas críticas restantes na M1: surgimento inicial/Horda, pressão local,
  Hordas por pressão e noite, fadiga nos segmentos 9–10, armas/munição/ruído.
  Não certificar a M1 até implementar a sequência canônica completa.
- Lacunas críticas restantes na campanha: retorno de Viagem e liquidação de
  recursos/efeitos, promessas, trabalho, eventos e cercos dos cinco dias,
  certificação de vitória e transição legal para Última Transmissão.
- Escopo desta verificação é revisão de código e testes automatizados. Nenhuma
  partida completa, simulação de equilíbrio, impressão ou sessão humana foi
  executada.
