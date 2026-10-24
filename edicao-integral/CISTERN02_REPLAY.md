# Paridade da Cisterna com cinco trajetórias táticas fixas

`python edicao-integral/replay_cistern02_fixed.py` usa a saída de `src/scaled_tactical_replay.py` como oráculo. Para cada H2–H6, esse roteiro antigo executa Mercado, Oficina e Estação com rolagens, cartas de Viagem, objetivos e decisões fixas já declaradas. A versão projetada para `Cistern02` registra vínculos, porções, pressão, cercos sem brecha, peças, trabalhos A/B/C e refeições até o dia 5. `REPLAY_CISTERNA_FIXO.json` contém os saldos por dia; comida, água, Materiais, Pressão e ativação do filtro coincidem com os cinco resultados do oráculo.

Os cinco grupos terminam com `candidate_victory`, não `verified_victory`. O novo motor **ainda não executa por si** o combate, as ações de mapa, carga e aquisição das peças do oráculo; a projeção recebe entregas de um replay tático pré-existente, com rolagens favoráveis fixadas. Também usa a opção legal de não acolher Bia. Isso demonstra paridade de estado para cinco trajetórias específicas, sem provar os ramos alternativos, a campanha completa integrada ou equilíbrio. A transição para Última Transmissão permanece bloqueada.

Correção posterior: o filtro concluído agora entra na lista de estruturas ativas, pode ser danificado por cerco e reparado com 2 Materiais+1 trabalho, sem repetir o enchimento inicial. A paridade das cinco trajetórias fixas permanece inalterada.
