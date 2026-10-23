# Ensaio isolado da defesa final

Comando: `python edicao-integral/simulate_defense.py --seeds 50 --seed 20261023 --output edicao-integral/ENSAIO_DEFESA_20261023.json`.

Foram executadas 250 defesas, 50 sementes consecutivas por equipe de 2 a 6 heróis. Uma única política aproxima-se do inimigo mais perto do objetivo e ataca com pé de cabra. Em **cada** partida, os quatro portões, o transmissor e um pé de cabra por herói foram injetados. A aquisição legal deles, o consumo dos dias anteriores e as decisões dos arcos não foram simulados.

| Heróis | Vitória | Derrota |
| ---: | ---: | ---: |
| 2 | 7 | 43 |
| 3 | 34 | 16 |
| 4 | 47 | 3 |
| 5 | 50 | 0 |
| 6 | 50 | 0 |

O caso de dois heróis merece playtest e revisão de viabilidade, mas esses números **não** são taxa real de vitória nem evidência suficiente para mudar ondas ou atributos. O modelo só tem quatro equipamentos estruturados e não representa a seleção real dos itens do kit 0.2. Não houve impressão nem partida humana.
