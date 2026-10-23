# Campanha contínua experimental

`IntegratedCampaign` é uma fronteira **incompleta e bloqueada** entre a caixa
0.2 e o motor experimental. Ela não altera `RULES.md`, `CAMPAIGN.md`,
`content/catalog.json` ou os PDFs existentes.

## Fluxo

1. `new(seed, founders, links)` usa a preparação canônica de `Cistern02`.
2. `collect_part()` recusa entregar qualquer peça. O método antigo debitava
   dois segmentos sem entrada, PA, teste, carga ou retorno e foi bloqueado.
3. O relógio, refeições, reservas e trabalho continuam sendo validados por
   `Cistern02`. O filtro só é considerado concluído quando A/B/C realmente
   terminam.
4. `complete_cistern()` também permanece bloqueado. A antiga versão aceitava
   `candidate_victory`, descartava moradores, vínculos, ferimentos e outros
   estados, truncava porções e criava duas pistas sem ação comprovada. Além
   disso, não emitia o `cistern_record` exigido por `Arc2`.
5. A Última Transmissão **não é alcançável** por campanha legítima nesta
   integração. Testes isolados do segundo arco usam fixtures sintéticas.

## Limites conhecidos

O adaptador precisa receber recibos verificáveis de expedição e migrar todo o
estado canônico antes de emitir `verified_victory`. Há incompatibilidade entre
12 fundadores possíveis no kit 0.2 e dez protagonistas experimentais. O Posto
e sua economia de combustível ainda faltam no fluxo regional. A defesa e seus
mapas continuam experimentais.

O estado completo é salvo em JSON com schema próprio, incluindo o `World`, a
Cisterna, decisões, recompensas e motivo terminal. `load()` valida o estado
antes de permitir retomada.
