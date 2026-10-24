# Paridade da Cisterna com cinco trajetórias táticas fixas

`python edicao-integral/replay_cistern02_fixed.py` usa a saída de `src/scaled_tactical_replay.py` como oráculo. Para cada H2–H6, esse roteiro antigo fornece ao estado de `Cistern02` entregas e decisões calculadas previamente. Os eventos fixos são aplicados pelo estado atual; cercos usam o gatilho do dia 3 ou carta CER revelada e persistida.

Os cinco grupos terminam com `candidate_victory`, não `verified_victory`. O novo motor **ainda não executa por si** o combate, as ações de mapa, carga e aquisição das peças do oráculo; a projeção recebe entregas de um replay tático pré-existente, com rolagens favoráveis fixadas. Também usa a opção legal de não acolher Bia. Isso demonstra paridade de estado para cinco trajetórias específicas, sem provar os ramos alternativos, a campanha completa integrada ou equilíbrio. A transição para Última Transmissão permanece bloqueada.

Em 2026-10-24, o script foi ajustado para não acrescentar novamente a pressão dos eventos automáticos. Ele continua sendo uma comparação de saldos com dados táticos pré-fornecidos, **não uma execução legal de campanha**. O relatório atual deste ciclo comprova zero dias completos jogados pelo executor integrado.

Correção posterior: o filtro concluído agora entra na lista de estruturas ativas, pode ser danificado por cerco e reparado com 2 Materiais+1 trabalho, sem repetir o enchimento inicial. A paridade das cinco trajetórias fixas permanece inalterada.
