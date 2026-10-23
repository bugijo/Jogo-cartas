# Habilidades da edição experimental

Os 70 marcos dos dez protagonistas estão em `data/system.json`, gerado por `data/build_system_data.py`. Cada registro possui ID estável, limiar de XP, tipo de operação, bônus numérico e texto. Os limiares são 0, 5, 12, 20, 35, 50 e 75 XP; o bônus soma apenas enquanto o herói mantém aquele XP. O teste `test_all_seventy_skill_thresholds_activate_typed_bonus` verifica todos os registros.

Operações com efeito no motor: `medicine` (enfermaria), `water` (reservatório), `rescue` (socorro), `defense` (ação guardar), `attack` (dano se acertar), `noise` (intensidade do marcador), `infection` (D6 de mordida), `travel` (segmentos), `search` (primeiro recurso encontrado), `repair` (vida restaurada), `build` (trabalho), `craft` (munição na oficina), `food` (horta madura com trabalhador designado) e `storage` (capacidade). Limites de vida, distância e dados permanecem aplicados pelo motor.

Os efeitos são operacionais nos contextos citados, mas ainda não foram avaliados em playtest. Bônus cumulativos altos podem dominar o sistema; não ajustar sem partidas e cenários mais variados. A árvore é linear por limiar nesta implementação, sem escolhas ramificadas; isso ainda não satisfaz a árvore individual de opções desejada para o jogo final.
