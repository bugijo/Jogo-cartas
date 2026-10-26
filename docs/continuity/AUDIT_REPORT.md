# Relatório de auditoria — atualização 2026-10-26

Base local/remota antes deste lote: `d3d6137660cf0d3e4415e227fcf9b5edad13bccf`.
Implementação de código e testes: commit `709c48f`, publicado por fast-forward
normal. Este relatório de auditoria e o checkpoint do lote são a próxima
unidade de documentação.

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
