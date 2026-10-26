# Relatório de partidas automatizadas — atualização 2026-10-26

## Tentativa narrativa/combustível desta retomada

| Execução | Resultado | Leitura correta |
|---|---|---|
| `verify_continuous_campaign.py`, seed 22, schema 3 | `local_defeat_clock_blocked`; 27 decisões regionais | Cisterna legal e migração; expedição legal à Estação; Célia investigada e uma pista copiada por ações físicas; extração não coube no clock e ocorreu retirada no 7/10. Não recrutou Célia, não decifrou rádio, não visitou Posto ou instalação. |
| Oficina `EXP-FUEL-CACHE-WORKSHOP-01`, seed 22, 8 perfis | 8/8 retornaram e depositaram 8 combustíveis | Uma expedição experimental isolada; perfis são políticas programáticas determinísticas compartilhando o mesmo motor, não jogadores cognitivos nem provas de equilíbrio. Não prova Posto/van ou campanha completa. |
| Regressão completa | 314 testes passaram nesta árvore | Inclui recibos, identidade, custos, PA de companheiro, saída, save/load, cache/rota da Oficina, Cisterna e bloqueio regional. Fixtures isoladas não comprovam rota integral. |

## Provas reproduzidas

| Execução | Resultado | O que prova | O que não prova |
| --- | --- | --- | --- |
| `verify_campaign_player02.py`, seed 22 | `verified_victory`, 5 dias/noites, 3 expedições, 98 decisões | Uma trajetória legal da Cisterna desde a preparação, mantendo seu certificado como regressão. | Equilíbrio, outras sementes/tamanhos, ou sucesso no arco 2. |
| `verify_continuous_campaign.py`, seed 22 | ver atualização ativa acima | Uma pista regional obtida legalmente e retirada porque a extração não cabe no clock/PA atual. | Prova de recrutamento, rádio, combustível da missão, transmissor ou vitória. |
| `verify_regional_player.py`, seed 22 | `regional_agent_round_trip_verified` | Cisterna → migração → Mercado; porta comum, movimento, busca, save/load, saída/retorno, entrega de 2 comida e 1 água, consumo do dia sem déficit, sem criar combustível. | Célia, cartas de Viagem regionais, Posto, transmissor, veículo, gate militar, defesa final ou vitória do arco 2. |

## Método e limite

`AdaptiveRegionalPlayer` é uma política programática determinística, com
prioridades observáveis e chamadas às APIs públicas do motor. Os nomes de
perfil variam a preferência de combate de forma limitada; não representam oito
agentes cognitivos independentes e não recebem informação futura/oculta.
Os oito perfis foram comparados somente na expedição experimental da Oficina,
na mesma seed. A tentativa da Estação usou `balanced`. Testes de safe-zone e
recibos ainda incluem fixtures isoladas.

Não foram calculadas taxas de vitória nem avaliação de equilíbrio. Não houve
playtest humano, impressão física ou teste de montagem. Nenhum tempo de mesa foi
estimado por tempo computacional.

Comando de reprodução:

```bash
python3 edicao-integral/verify_campaign_player02.py
python3 edicao-integral/verify_continuous_campaign.py
python3 edicao-integral/verify_regional_player.py
```
