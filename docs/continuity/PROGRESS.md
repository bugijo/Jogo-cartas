# 2026-10-26 — correção de fontes e reconciliação ativa

- Checkout confirmado: branch `evolucao/zona-zero-sistema-v1`, HEAD/remoto
  `081048f` após push do replay `stealth`; as alterações restantes são documentais.
- Corrigida a referência de fonte no dado gerado e na missão: `RULES.md §11,
  linha 64` (2 combustível/trecho). A linha 64 não é uma seção numerada.
- Mantida a conta experimental `EXP-MIS-104=12` (`far=3`, ida/volta, 2 por
  trecho) e a reserva experimental Oficina 8; nenhuma das duas virou regra
  definitiva. O2 do Posto segue sem combustível explícito.
- Grafo atualizado: a descoberta pré-rádio elimina o ciclo lógico, sem pista
  automática. Política `stealth` extrai a primeira pista da Estação; a rota
  balanced fica sem relógio após combate opcional. Ainda falta obter a segunda
  pista e concluir contato/recrutamento, sem nova pista inventada.
- Verificação: 321 testes passaram; `validate_data.py`, `compileall`, Cisterna
  seed22, replay `stealth` que retorna uma pista, caso `balanced` de emergência
  e comparação determinística do artefato passaram. Cisterna permanece certificada; replay `stealth` retorna uma pista e replay
  `balanced` registra emergência. Ambos são do motor tático regional e não resolvem cartas de Viagem/emboscadas, portanto não comprovam expedição canônica integral. Nenhum chega a rádio, Posto, van, transmissor
  ou defesa. Impressão física e playtest humano não ocorreram.

Correções adicionais desta unidade: fonte gerada agora aponta exatamente a
`RULES.md §11, linha 64`; controlador deixou de relatar saída enquanto um
inimigo ainda mantém o encontro aberto. Regressão cobre a extração falsa.

Próxima unidade: integrar a resolução de Viagem regional somente após definir
a ponte de recursos físicos e emboscada; em paralelo, implementar distribuição
de refeição e estados de Fome/Sede com decisões auditáveis, sem escolher
beneficiários automaticamente.

# Progresso

## 2026-10-26 — pista física, conservação e bloqueio mensurável da Estação

- Código/testes publicados no commit `3e65893` (`feat: validate regional clues and experimental fuel route`), branch experimental por fast-forward comum.

- A hipótese experimental separa descoberta física de Célia, cópia de pista e
  recrutamento. Encontrar Célia antes do rádio não concede pista; as duas
  evidências têm IDs distintos, custam 1 PA e só valem pré-rádio. Vicente é a
  identidade condicional original `ZC-MOR-0003`, sem duplicação.
- Corrigidos bypasses de marcador legado: `npc_contacts` sozinho não basta
  para recrutar, pista exige recibo anterior de investigação, e evidência não
  pode ser coletada depois da decodificação do rádio. `World.validate` confere
  o recibo com catálogo, ação e viagem; save JSON segue editável e não é
  autenticado criptograficamente.
- Corrigido o controlador regional para gastar PA de qualquer herói elegível
  antes de avançar o relógio e não tratar uma saída ocupada como interação.
- Replay legal atual: vitória da Cisterna seed 22, migração, expedição à
  Estação, investigação e cópia de 1 pista; retirada de emergência porque o
  retorno não cabe no clock 7. Limite inferior: 13 PA individuais do
  explorador, 9 PA disponíveis em três ativações locais far. Sem Célia
  recrutada, rádio, cartão, van, transmissor ou defesa. O script anterior foi
  preservado como `verify_continuous_campaign_historical.py`.
- Cache experimental finito da Oficina custa 2 PA, produz ruído 3, entra em
  carga e só retorna ao estoque via extração normal. Oito políticas
  programáticas retornaram as 8 unidades em seed 22. Isso não demonstra rota
  Posto/van. A hipótese 8+8−4=12 usa retorno regional `medium=2` e diverge do
  custo 2 do kit 0.2; não é regra final aprovada.
- O grafo, a matriz de combustível, replay schema 3 e CHECKPOINT registram o
  estado e as lacunas; a continuidade até Última Transmissão ainda não está
  provada.

## 2026-10-26 — controlador regional, custos táticos e auditoria de combustível

- Base real confirmada por fetch: `d3d6137660cf0d3e4415e227fcf9b5edad13bccf`, branch `evolucao/zona-zero-sistema-v1`; não havia alterações concorrentes no remoto.
- Commits `709c48f` (motor/testes/replays) e `1feacee` (documentação/checkpoint) publicados por push fast-forward; sem merge ou alteração da `main`.
- Alinhadas às regras atuais as ações táticas: mover custa 1 PA mais 1 ao sair de uma zona com inimigo; abrir porta comum custa 1 PA; romper porta bloqueada custa 2 PA com ferramenta, sem teste, perda de durabilidade ou ruído não especificados. Clientes e testes que usavam `breach` para porta comum foram migrados.
- `World.open_expedition()` verifica reserva para ida, uma rodada local e retorno em até dez segmentos antes de despachar. O desconto de motorista e habilidade é considerado antes do teste e de qualquer gasto; teste cobre uma ida de um segmento iniciada no relógio 7 e concluída no 10.
- `AdaptiveRegionalPlayer` executa um objetivo tático por APIs públicas, com decisões observáveis, save/load de política e retorno. Não dirige veículos enquanto custo/rota estiverem pendentes. Uma auditoria adversarial corrigiu contato de NPC tratado como sucesso por ausência do contato, rota bloqueada sem ferramenta quando há desvio, e mapa inválido cobrado antes da validação.
- Replay repetível seed 22: Cisterna legal (5 dias/noites, 3 expedições, 98 decisões, `verified_victory`), migração, uma expedição regional a pé ao Mercado, busca (2 comida + 1 água), save/load, retorno, conservação e fechamento do dia. Não prova Célia, Posto, transmissor nem defesa.
- Bloqueios documentais preservados: `RULES.md` da árvore tem §§1–14, então a referência §64 não está disponível; custo de combustível está em §11, rotas §5. Posto O1=8; O2 não define combustível/quantidade; `EXP-MIS-104` fixa 6, regional `far=3` implica 12 pelo custo canônico. Nenhuma alternativa foi escolhida ou implementada.
- Bloqueio narrativo novo: migração da Cisterna seed 22 produz zero pistas; somente Célia e Vicente têm saída de pesquisa no catálogo. Célia está marcada `post_cistern_radio_signal`, e o sinal exige duas pistas. A origem/ordem das pistas precisa de decisão de conteúdo.
- Verificação ao fechar a unidade: suíte completa 296 testes passou. Validação de dados (127 IDs, 10 heróis, 70 habilidades, 15 NPCs), `compileall`, validação de `TASK_QUEUE.json`, `git diff --check` e verificador da Cisterna passaram. Revisor independente executou 51 testes focados; os verificadores contínuo e regional reproduziram seus resultados limitados.
- Revisor independente read-only executou 51 testes focados e confirmou que o replay não é campanha completa. Sem impressão física, playtest humano ou avaliação de equilíbrio.

## 2026-10-25 — relógio regional, Hordas, fadiga e retirada

- Branch `evolucao/zona-zero-sistema-v1`; commits `2e07b08`, `6d25b43` e
  `2a24cc7` já publicados. A auditoria de combustível mantém as fontes em
  `edicao-integral/TACTICAL_FUEL_AUDIT.md`; O2 não foi tratado como combustível
  e a concessão experimental da Oficina foi removida.
- O motor regional agora cobra relógio comum de 10 segmentos em viagens e
  rodadas, impõe uma expedição/dia, aplica a fadiga das noites, reduz PA por
  fadiga, recupera 1 fadiga após noite alimentada/hidratada, persiste surgimento
  inicial e deck/pressão de Horda em save/load. Regras sem dados regionais novos
  (baralho de Viagem e frequência de Horda própria) continuam bloqueadas.
- Recrutar Célia exige contato tático e custo de PA/sustento/capacidade. A
  localização Station/O2 é adaptação experimental, explicitamente não canônica.
- Implementada retirada de emergência do arco regional: derrota local registrada,
  carga obtida perdida, heróis retornam com ferimento/fadiga, acompanhantes
  ficam no destino e veículo fica danificado; cartas carregadas do abrigo são
  conservadas. Save/load e conservação cobertos.
- Replay seed 22 continua provando Cisterna legal. No arco 2, após fechar o dia
  do Mercado, a rota provisória à Estação sofre incapacitação e termina em
  `local_expedition_defeat`; não conclui Célia, Posto, transmissor ou defesa.
- Verificações locais finais deste lote: 270 testes passaram;
  `verify_campaign_player02.py`, replay contínuo, `validate_data.py`,
  `compileall` e `git diff --check` passaram.

## 2026-10-25 — recuperação canônica, validação de fadiga e turno protegido

- Commit `60340c4` corrigiu validação de fadiga e o primeiro turno protegido;
  `f205e55` completou migração de fadiga e exclusividade diária; `0f1ce2a`
  restringiu trabalho a heróis aptos e horta operacional; `fb48fda` limita
  cuidado médico a quem está no abrigo. A suíte no HEAD publicado tem 282 testes;
  Cisterna seed 22, replay contínuo,
  validação de dados, `compileall` e `git diff --check` passaram.
- Portada a recuperação do §25 para heróis e NPCs modelados: refeição completa
  remove uma fadiga; pessoa que não trabalhou nem saiu também recupera um
  ferimento. Registros diários de trabalho/saída persistem em saves e são
  validados. Civis genéricos do ledger continuam sem estado operacional para
  aplicar a mesma recuperação.
- `World.validate()` rejeita fadiga fora de 0–3. O primeiro turno tutorial do
  Mercado mantém Hordas anunciadas pendentes sem contagem regressiva ou geração.
- Revisão seguinte encontrou e corrigiu a exclusividade trabalho/expedição de
  `RULES.md` §4 nos dois sentidos; NPC em expedição não executa automação de
  abrigo naquela noite. A migração agora projeta fadiga 0–3 para o arco regional,
  além de preservar o estado-fonte. O teste de fadiga não zero é uma fixture de
  unidade e não afirma que uma campanha legal tenha terminado cansada.
- Replay contínuo segue terminando em derrota local na Estação, relógio 7/10;
  não chega ao Posto, ao combustível regional nem à instalação militar.
- O conjunto direcionado executou 55 testes de sistema, transição e tática antes
  da última correção; a suíte completa de 282 cobriu os módulos restantes.

## 2026-10-25 — migração seed 22 e primeiro bloqueio contínuo

- Implementada `IntegratedCampaign.transition_to_last_transmission()`: exige
  certificado real, fim das cinco noites/eventos, recibos legais das três
  peças e ausência de resolução pendente. A projeção é atômica, idempotente,
  tem SHA-256 determinístico de proveniência e sobrevive ao save/load.
- Preservados o estado completo da Cisterna e do integrador em arquivo não
  gastável; os campos comuns são projetados como recursos contadores, pessoas
  genéricas seguem consumindo (inclusive cães), o Pé de cabra segue como item
  ativo, e valores sem equivalente não são convertidos nem descartados.
- IDs de todos os 12 fundadores são aceitos no `World`. Téo e Célia não são
  duplicados como NPCs quando já migrados como heróis. As habilidades 0.2 deles
  permanecem arquivadas e ainda não têm efeito no arco regional.
- Criado `verify_continuous_campaign.py` e replay bloqueado: seed 22 vence a
  Cisterna (5 dias, 3 expedições, 98 decisões), migra, executa viagem/busca na
  Estação, recupera cartão e retorna. A tentativa legal de decifrar o rádio
  falha com 0 pistas frente ao requisito de 2.
- O diagnóstico independente confirma bloqueios seguintes: Posto ausente no
  mapa regional; combustível de Oficina limitado a 3 buscas vs. 6 exigidos
  pelo motor para a instalação; recuperação de furgão regional diverge da
  regra canônica de Bateria/PA/teste no Posto; faltam encontros táticos nas
  expedições regionais. Nenhum desses gates foi contornado.
- Testes focados: 8 aprovados. Regressão: 237 aprovados; replay da Cisterna,
  verificador contínuo (até o bloqueio), validador de dados, compileall e
  `git diff --check` aprovados. Sem campanha integral, defesa final, impressão
  ou playtest humano.

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

## 2026-10-25 — rota de pistas e bloqueio logístico (revisão da migração)

- A auditoria independente encontrou caminho legal no motor para as duas
  pistas: quatro buscas no Mercado sustentam quatro consumidores por dois dias;
  Célia (`EXP-NPC-02`), ausente como fundadora nesse H2, pode ser recrutada e
  designada a `teaching`, produzindo uma pista por dia. O rádio consome as duas.
  Não há déficit alimentar nessa rota. Recrutar sem encontro é permitido pelo
  motor, mas continua uma lacuna narrativa do arco experimental.
- O replay passou a executar essa rota, depois obtém cartão de acesso na
  Estação, busca três vezes na Oficina e retorna com apenas três combustíveis.
  Posto `EXP-LOC-07` falha por destino inexistente; autorização militar falha
  por veículo indisponível e reverte o gate. Não se chama defesa final.
- A auditoria canônica confirma Posto com oito cartas únicas (1 PA cada),
  Bateria da Oficina e van de seis lugares (inspecionar + 2 PA e Técnica 6 no
  Posto), mas o motor experimental recupera furgão de quatro lugares na Oficina
  sem Bateria. A equivalência de custo também conflita: 6 unidades no arco 2
  vs. 2 por trecho 0.2 aplicados a `far=3` (8/12 no round-trip conforme a
  leitura). Nenhum custo foi alterado nesta rodada.
- Verificador contínuo agora cobre 34 ações e atualiza o primeiro bloqueio para
  Posto/veículo/escala de combustível. A campanha integral permanece pendente.

## 2026-10-25 — Posto, Bateria, van e busca regional

- Ativado `EXP-LOC-07` Posto e a planta `gas_station_02` com a geometria
  existente ligada ao destino. O catálogo registra oito retiradas finitas de
  combustível; o mapa não gera combustível via busca abstrata.
- Migração projeta a Bateria de acordo com sua proveniência: já retirada vai ao
  estoque único; ainda disponível fica no O1 da Oficina; perdida não reaparece.
  A campanha seed22 a recupera por movimento, porta e 1 PA e a devolve ao
  estoque como carga única.
- Implementada a van canônica `EXP-VEI-02` (6 lugares, 12 cargas, 2 unidades por
  segmento): inspecionar custa 1 PA; reparo requer Bateria, O1, 2 PA e teste
  Técnica 6 determinístico. Falha preserva Bateria; sucesso consome. Retorno
  com van consome combustível da carga da expedição. API `recover_vehicle` não
  permite burlar essa sequência; campanha migrada exige a van canônica.
- Busca de uma campanha migrada exige mapa tático, presença na área de busca e
  1 PA. O cartão de acesso é carga única e precisa retornar ao abrigo antes de
  liberar o gate militar.
- O replay parcial atualizado tem 62 registros resumidos, chega ao Posto e
  recupera van com seed22, mas para no gate militar: 7 unidades após retorno vs.
  12 requeridas. Fontes conhecidas somam 3 Oficina + 8 Posto = 11 antes de
  retorno. A divergência do arco experimental (6) contra `RULES.md` §11 (2 por
  trecho) permanece; não foi aplicada alteração de equilíbrio.
- Revisões read-only independentes confirmaram a incompatibilidade de combustível
  e que trechos do segundo arco ainda são abstratos (contato/recrutamento,
  relógio/eventos/encontros). Nenhuma campanha integral ou vitória do arco 2 é
  declarada.

## 2026-10-25 — legalidade dos turnos e regressão completa

- A regressão inicial encontrou seis quebras: o simulador de um dia usava busca
  sem ator mesmo após entrar no mapa; um teste de mapa também usava a chamada
  abstrata; o gerador do catálogo ainda marcava Posto como referência sem
  destino. O simulador agora busca pela ação tática que cobra 1 PA, e o gerador
  associa `gas_station_02` a `EXP-LOC-07`. Todos os 251 testes passaram.
- A busca no mapa exige presença do herói na zona de busca e ação disponível;
  o replay usa o método tático em vez de busca abstrata.
- O controlador contínuo deixou de renovar PA via `World.begin_round()` e usa
  `TacticalGame.activate()`, processando a ativação do mapa. A interface de
  planejamento ganhou `path_to()` e `exit_zone` públicos para as rotas do
  controlador. O teste cobre caminho fechado antes e aberto após arrombamento.
- O replay ainda termina sem mutação no gate militar. A unidade regional é
  incoerente com a oferta: 7 combustível após retorno; demanda canônica 12;
  oferta máxima modelada 11 antes do retorno. A regra experimental que diz 6
  permanece sem alteração. Isso não constitui replay integral físico: contato
  narrativo, relógio/eventos e surgimentos regionais ainda não estão integrados.
- `verify_campaign_player02.py` preserva a vitória da Cisterna seed22; o replay
  contínuo tem 62 registros resumidos (não ações atômicas), conclui o ciclo do
  Posto/van e não invoca defesa final.

## 2026-10-25 — correções da auditoria adversarial da ponte

- Auditoria independente do commit `359ec46` encontrou dois defeitos reproduzíveis:
  save/load rejeitava `access_card` em carga regional autorizada; busca não
  descontava `special_cargo` da capacidade. Foram acrescentados testes que
  falharam antes da correção e passaram depois.
- `World.validate()` aceita agora o cartão como componente de missão único e
  mantém a verificação de não duplicação. `World.search()` inclui carga especial
  no limite e não gasta PA nem contador se não houver espaço.
- A verificação independente de fontes não encontrou combustível adicional
  explícito nas cartas de busca. Porém, `CAMPAIGN.md` deixa indefinido se o
  “lote de cada provisão” do Posto O2 inclui combustível e sua quantidade; o
  déficit 11 versus 12 é confirmado pelo modelo atual, não prova definitiva de
  impossibilidade canônica até essa frase ser esclarecida.
- Revalidação após as correções: 253 testes passaram; validação de dados,
  compilação, `git diff --check`, replay da Cisterna e reprodução idêntica do
  bloqueio contínuo passaram. Nenhum mapa/PDF físico novo foi gerado.
