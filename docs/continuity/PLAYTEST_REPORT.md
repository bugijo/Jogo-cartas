# Relatório de partidas automatizadas — atualização 2026-10-26

## Provas reproduzidas

| Execução | Resultado | O que prova | O que não prova |
| --- | --- | --- | --- |
| `verify_campaign_player02.py`, seed 22 | `verified_victory`, 5 dias/noites, 3 expedições, 98 decisões | Uma trajetória legal da Cisterna desde a preparação, mantendo seu certificado como regressão. | Equilíbrio, outras sementes/tamanhos, ou sucesso no arco 2. |
| `verify_continuous_campaign.py`, seed 22 | `local_expedition_defeat` | Migração após vitória e uma expedição da Estação que termina em retirada legal após incapacitação; Célia não é contabilizada como recrutada. | Campanha completa; a rota/contacto está provisória. |
| `verify_regional_player.py`, seed 22 | `regional_agent_round_trip_verified` | Cisterna → migração → Mercado; porta comum, movimento, busca, save/load, saída/retorno, entrega de 2 comida e 1 água, consumo do dia sem déficit, sem criar combustível. | Célia, cartas de Viagem regionais, Posto, transmissor, veículo, gate militar, defesa final ou vitória do arco 2. |

## Método e limite

`AdaptiveRegionalPlayer` é uma política programática determinística, com
prioridades observáveis e chamadas às APIs públicas do motor. Os nomes de
perfil variam a preferência de combate de forma limitada; não representam oito
agentes cognitivos independentes e não recebem informação futura/oculta.
Somente o perfil explorador foi usado na prova regional acima. O teste de
contato de Célia é uma unidade isolada com fixture, não uma partida/replay.

Não foram calculadas taxas de vitória nem avaliação de equilíbrio. Não houve
playtest humano, impressão física ou teste de montagem. Nenhum tempo de mesa foi
estimado por tempo computacional.

Comando de reprodução:

```bash
python3 edicao-integral/verify_campaign_player02.py
python3 edicao-integral/verify_continuous_campaign.py
python3 edicao-integral/verify_regional_player.py
```
