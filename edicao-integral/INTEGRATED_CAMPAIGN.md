# Campanha contínua experimental

> **Relatório histórico.** Este documento registra o estado anterior ao replay
> H2 legal de 24/10/2026. `verified_victory` já foi obtido para seed 22; o
> estado atual e a evidência reproduzível estão em
> [`CAMPAIGN_INTEGRATION.md`](CAMPAIGN_INTEGRATION.md). A migração para
> `World` e a sequência completa até Última Transmissão continuam bloqueadas.

`IntegratedCampaign` é uma fronteira **incompleta e bloqueada** entre a caixa
0.2 e o motor experimental. Ela não altera `RULES.md`, `CAMPAIGN.md`,
`content/catalog.json` ou os PDFs existentes.

## Fluxo

1. `new(seed, founders, links)` usa a preparação canônica de `Cistern02`.
2. `collect_part()` continua bloqueado. `start_expedition()` abre uma viagem
   pelo mapa canônico; `Tactical02.pickup_part()` exige zona, PA, carga e teste
   da Bomba; `return_expedition()` entrega uma peça apenas após saída legal e
   retorno. Retirada de emergência não entrega carga. O método antigo debitava
   dois segmentos sem essas operações.
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

O núcleo tático já cobre lotes fixos, Saque regional finito e estado de mapa
entre visitas, mas ainda não cobre resgates, cartas de Viagem e fila completa do
dia. A van pode ser reparada e retornar no Posto; seu estado ainda não migra ao
segundo arco. O adaptador precisa
comprovar também essas operações e migrar todo o estado canônico antes de
emitir `verified_victory`. Há incompatibilidade entre
12 fundadores possíveis no kit 0.2 e dez protagonistas experimentais. O Posto
e sua economia de combustível ainda faltam no fluxo regional. A defesa e seus
mapas continuam experimentais.

O estado completo é salvo em JSON com schema próprio, incluindo o `World`, a
Cisterna, decisões, recompensas e motivo terminal. `load()` valida o estado
antes de permitir retomada.
