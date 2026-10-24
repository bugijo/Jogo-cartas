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

## Auditoria adversarial da certificação — 2026-10-24

- O auditor encontrou um bypass reproduzível em `Cistern02.certify_victory()`:
  com `result='candidate_victory'`, chamar o método com três nomes de missão
  emitia vitória mesmo com `parts={}` e `filter_completed=False`.
- Corrigido: a certificação agora exige o candidato, filtro concluído, as três
  peças presentes no estado persistente e as referências de objetivos. O
  integrador também exige seus recibos de entrega. Um novo teste reproduz o
  payload forjado e confirma que o resultado permanece candidato.
- Este bloqueio não prova, sozinho, origem tática das peças se um chamador
  adulterar diretamente todo o estado em memória; o gate de campanha continua
  dependendo dos recibos integrados e da ausência de mutação administrativa.
- Auditoria separada do retorno aponta P0 ainda aberto: Emboscada na volta pode
  deixar a expedição fechada sem retomada; efeitos da ida se perdem; liquidação
  pode mutar parcialmente o estoque antes de falhar; faltam estado persistente
  para cão/rota/Ponte e baralho de Viagem por campanha. Nenhuma correção desses
  itens foi incluída neste lote.

## Primeira reauditoria M1/Horda e carga — 2026-10-24 (estado anterior)

- Implementado baralho compartilhado de Horda com descarte/embaralhamento
  determinístico, snapshots e migração de save legado; a M1 persiste estado
  junto às expedições.
- M1 agora resolve movimento no grafo, abertura de porta, combate equipado,
  munição, ruído, surgimento por disparos, pressão local, Horda por pressão e
  por noite, fadiga por segmento noturno e penalidade de PA. A revisão da regra
  não tratou Z6 como compra inicial adicional: `RULES.md` §30 define o ponto de
  surgimento, enquanto §§33 e 39 definem os momentos de Horda.
- Viagem reserva os recursos declarados do estoque ao partir e devolve o saldo
  restante após retorno. Liquidação de recibos no retorno é transacional.
- Auditoria independente repetiu o teste de falha parcial e confirmou que
  recibos, estoque e referência tática permanecem íntegros quando a liquidação
  falha. A falta de recursos reais na preparação é rejeitada.
- Pendente P0: retirada durante Emboscada M1 de retorno ainda falha; a auditoria
  reproduziu `ValueError` ao tentar usar o recibo de `return_travel`. Também
  faltam efeitos persistentes para cão/rota/Ponte, efeitos da estrada durante
  emergência, promessas, noites, cercos e campanha completa.
- Verificação local não publicada neste registro: 175 testes experimentais
  passaram; validação de dados, `compileall` e `git diff --check` passaram.
- Estes são testes de módulos e integração, não trajetórias completas nem
  estimativas de equilíbrio. Não houve simulação completa, impressão ou
  playtest humano.

## Fechamento de achados de estrada/M1 — 2026-10-24

- Após essa reauditoria, foram corrigidos: retorno VIA-0003 (skip sem reaplicar),
  capacidade pelas cartas físicas escolhidas (cada cursor parcial ocupa carga), M1 de retorno em
  emergência inclusive no relógio 10, segundo cão em família distinta, fadiga
  VIA-0002 no retorno e sincronização de fadiga antes/depois da M1 de retorno.
- O auditor de viagem também encontrou que um teste antigo considerava
  incorretamente 2 comida + 1 água + 1 Material impossível para um herói com
  Pé-de-cabra; o teste agora cobre o limite legal e um excesso real de carga.
- Implementados locais de coleta de equipamentos canônicos em
  `edicao-integral/data/equipment_pickups02.json` e inventário persistente por
  herói. A coleta/emergência impedem recuperar o mesmo item como cópia nova.
- Testes após essas correções: 188 testes experimentais, validação de dados
  (inclui cinco locais de coleta), `compileall` e `git diff --check` passaram.
- Revisões independentes apontam ainda que a carga é agregada na preparação
  (não há ficha de portador individual para suprimentos), o baralho de Viagem
  ainda não é um sapato persistente entre dias e efeitos de rota/Ponte não têm
  uso mecânico. Eventos/noites/cercos também não formam ciclo completo.
- Nenhuma campanha completa foi simulada; não há inferência de equilíbrio,
  duração ou diversão. Impressão e playtest humano permanecem pendentes.
- Regressão legada repetida após restaurar `content/catalog.json`: 51 passaram.
  Permanece um aviso `ResourceWarning` já conhecido em
  `tests/test_boards06.py:64`.
- Auditor M1 independente verificou o caso de cartas parciais: quatro cartas
  `[1,1,1,1]` são rejeitadas com um Pé-de-cabra (estoque não muda), três cartas
  `[1,1,1]` cabem exatamente. A seleção minimiza número de cartas e, depois,
  excesso de porções; por isso `[3,3]` para solicitação 4 leva os dois lotes
  (6 porções) sem criar recurso. O hash do catálogo voltou a coincidir com o
  baseline congelado.

## Revisão independente e extensão de estrada — 2026-10-24

- Auditoria independente no HEAD `931d572` confirmou o gap de sapato: cada
  `start_travel()` recriava todas as cartas e não mantinha descarte entre dias.
  O lote atual introduz `TravelShoe02`, compartilhado por campanha, com monte,
  descarte, reshuffle determinístico, validação de sequência e snapshot.
  Cartas explícitas usadas por testes permanecem fixtures isoladas.
- Auditoria encontrou ainda que a regra `RULES.md` seção 6 permitia ao motor
  acumular ferimentos acima do máximo 3; o combate tático agora limita dano no
  teto canônico. A M1 já fazia esse limite. Teste reproduziu Bruto com 2 e 3
  ferimentos iniciais.
- O motor aceitava três armas por herói apesar do limite de duas armas
  transportadas em `RULES.md` seção 6. O gate foi acrescentado à preparação
  integrada e tática, sem reduzir as quatro cargas gerais; teste confirma que
  o estoque não é reservado quando a preparação é rejeitada.
- A revisão encontrou ambiguidade sobre munição: o ataque tático desconta
  `Cistern02.ammo` global, enquanto a regra diz que cada tiro gasta uma munição,
  mas não define transporte de munição pela expedição. Não foi aplicada
  interpretação mecânica silenciosa. Clarificar documentação e carga antes de
  alterar esse comportamento.
- Permanecem sem cobertura: carta extra de Viagem no segmento noturno (§33),
  uso mecânico dos marcadores Ponte/rota, encaminhamento/Contato, promessas,
  eventos/noites/cercos integrados e qualquer replay de campanha completa.
- Os testes independentes (60 testes de estrada/integrador e 75 de
  tática/M1 no estado pré-lote) passaram. Isso foi revisão automatizada, não
  simulação de campanha nem playtest.
- Após as correções, teste integrado percorre ida/volta comum e retirada M1 e
  confirma descarte de duas cartas, cursor persistente e ausência de segunda
  liquidação. A suíte experimental passou com 197 testes.
- Auditoria adicional do ciclo do sapato apontou reshuffle antes do esgotamento
  quando o trajeto máximo era maior que o monte restante. O código local agora
  planeja o prefixo incluindo o descarte embaralhado sem mutar o snapshot;
  `finish_trip` só move o descarte após compra real da pilha reciclada. Novos
  testes cobrem viagem interrompida antes do fim do monte e compra após
  esgotamento; suíte experimental 199/199.
- Uma segunda auditoria adversarial reproduziu snapshot de Viagem adulterado:
  `index=2` com apenas um trecho outbound era aceito, permitindo contar carta
  falsa e recibo forjado. `Travel02.from_snapshot` agora cruza cardinalidade
  dos eventos, ordem/IDs, cartas do prefixo, segmentos de cada perna, estado de
  escolha/Emboscada e efeitos dos recibos. Teste integrado confirma rejeição no
  `IntegratedCampaign.load`. Persistem somente alterações locais até revisão e
  commit; 200 testes experimentais passaram.
- O auditor confirmou que o recibo resumido de M1 não prova, por si só, combate
  real em um save editado: uma pessoa que altera manualmente um snapshot coerente
  ainda consegue forjar um recibo plausível. O validador agora também rejeita
  duração de M1 maior que os 10 segmentos possíveis, mas o formato não tem
  assinatura criptográfica e não promete resistência a edição manual. Isso não
  afeta o fluxo normal da API; campanhas não recebem selo anti-falsificação.
- Estado de publicação: correção do reshuffle, invariantes de snapshot e limite
  de duração de M1 foram commitados e enviados em `06b03f45` na branch
  experimental. A revisão independente não achou falso rejeite nos snapshots
  válidos cobertos; saves editados manualmente continuam sem autenticidade
  criptográfica.
