# Relatório de auditoria — atualização 2026-10-26

## Revisão desta retomada (código/testes em `3e65893`, push concluído)

- A investigação de Célia deixou de exigir estoque/vaga de recrutamento; esta
  condição agora só se aplica ao contato que efetivamente adiciona Célia à
  expedição. A coleta de pistas exige investigação física anterior, janela
  pré-rádio, zona segura e ID não usado.
- Corrigido bypass em saves: marcador legado `npc_contacts` sozinho não recruta;
  cópia de pista precisa de recibo real de investigação. O validador do mundo
  confere valor, personagem, lugar, custo, quantidade, trip aberto e
  investigação anterior. Saves continuam editáveis; essa validação não é
  autenticação criptográfica.
- Corrigido o controlador: não renova relógio/PA quando outra pessoa da equipe
  ainda pode executar a ação; saída ocupada por inimigo não é tratada como
  interação. Regressões TDD demonstraram falhas antes das correções.
- O verificador de campanha foi atualizado e agora prova uma pista obtida
  fisicamente, mas bloqueia na extração do mapa da Estação (clock 7). A
  investigação lógica do ciclo de rádio está resolvida experimentalmente; a
  rota de mesa ainda exige 13 PA individuais mínimos contra 9 disponíveis.
- Revisão independente identificou que a hipótese de retorno regional do
  Posto (4) diverge do texto do kit 0.2 (2). A diferença está explícita no JSON
  e no relatório de combustível; a conta 12 não está aprovada como regra final.
- Verificação final da árvore: `python3 -m unittest discover -s
  edicao-integral/tests -q` (314 testes), `validate_data.py`, `compileall`, JSON
  dos dados/fila, `git diff --check`, Cisterna seed22, replay do Mercado e
  replay regional bloqueado passaram.
- Região não tem ainda baralho próprio de viagem/emboscada com resolução e
  efeitos definidos; permanece um bloqueio independente.

Base local/remota antes deste lote: `d3d6137660cf0d3e4415e227fcf9b5edad13bccf`.
Implementação de código e testes: commit `709c48f`; relatório/checkpoint:
`1feacee`. Ambos publicados por fast-forward normal.

## Evidência documental de combustível

`RULES.md` nesta árvore tem 14 seções numeradas, não §64. A regra de veículo é
§11: `EXP-VEI-02` consome 2 Combustíveis por trecho; rota curta é 1 trecho por
sentido e longa 2, conforme §5. `CAMPAIGN.md` e `content/catalog.json`
especificam oito cartas únicas em O1 do Posto e “um lote de cada provisão” em
O2; a definição de lote é Conserva e Água, sem combustível adicional explícito.
`data/last_transmission.json` exige/cobra seis para `EXP-MIS-104`; o mapa
regional `EXP-LOC-06` está em `far=3`, que a regra da van traduz em 12. A matriz
com cálculos e propostas sem escolha está em
[`TACTICAL_FUEL_AUDIT.md`](../../edicao-integral/TACTICAL_FUEL_AUDIT.md).

## Defeitos de código identificados e corrigidos neste lote

- Movimento e portas divergiam do manual: o movimento não cobrava PA adicional
  para deixar uma zona com inimigo, e `breach` modelava resistência, ruído e
  desgaste para uma porta comum. Agora a implementação usa os custos explícitos
  e distinguiu `open_door` de porta bloqueada.
- O teste de relógio regional era executado antes de desconto de motorista NPC;
  uma viagem viável no segmento 10 podia ser recusada. O preflight agora usa o
  custo final e ocorre antes de custo de combustível/mutação.
- O controlador considerava Célia recrutada quando ela só estava ausente da
  lista de contatos; uma rota mais curta podia ser escolhida mesmo sem
  ferramenta de porta bloqueada apesar de existir desvio aberto; um mapa
  incompatível era descoberto após abrir uma expedição. Testes de regressão
  cobrem os três casos.

## Auditoria de escopo e risco remanescente

- Contato físico e custeio de Célia estão implementados em `TacticalGame`, mas
  dados de localização/momento são provisórios. A prova unitária reposiciona
  herói e limpa inimigos; não prova uma rota legal de resgate.
- A migração seed 22 produz zero pistas. Só Célia e Vicente geram `research` no
  catálogo, enquanto a adaptação de Célia diz `post_cistern_radio_signal`; o
  rádio requer duas pistas. A ordem de pista/recrutamento está bloqueada por
  inconsistência de conteúdo, sem mudança silenciosa.
- Hordas, surgimento e combate tático regional local já existem e têm cobertura;
  cartas de Viagem/emboscadas regionais e uma cadência específica de Hordas para
  Última Transmissão não foram inventadas nem integradas.
- Saves JSON são editáveis: validação estrutural e reprodução determinística
  não autenticam autoria. Nenhuma fraude por alteração manual é impedida.

## Revisão independente

Agente de auditoria read-only reexecutou 51 testes focados e confirmou as
correções de PA/porta/preflight e o limite do replay. Não houve implementação
por agente externo. A suíte completa e os verificadores oficiais foram
reexecutados antes da publicação; consultar o checkpoint para resultados
finais e SHA.
