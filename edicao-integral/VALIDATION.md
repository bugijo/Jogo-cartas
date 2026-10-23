# Validação digital da evolução experimental

Data: 23/10/2026. Fonte: `data/system.json`; testes: `python -m unittest discover -s edicao-integral/tests -q`. Repetir o ensaio: `python edicao-integral/simulate_system.py --seed 20261023 --seeds 100`.

## Cobertura real

- 10 IDs de protagonistas com nome/profissão preservados, seis atributos e 70 registros de marcos. Bônus são tipados no catálogo; o de construção foi ligado a projetos, mas os demais ainda não se conectam a uma ação do motor; as árvores não estão prontas para mesa.
- 15 NPCs com profissão, nível 1–3 e trabalho. Produção de comida/água/medicina, construção, reparo, investigação, resgate clínico e defesa têm operações; motorista e explorador atuam quando acompanham uma expedição; outras tarefas têm simplificações que exigem revisão de mesa.
- Sete construções têm terreno, custo, trabalho, dano e reparo. A horta produz após quatro dias; oficina, enfermaria e reservatório têm uma ação parametrizada cada; fabricação ampla, tratamento de infecção e água contaminada ainda faltam.
- Cinco locais têm distância, carga de busca e reposição apenas natural. Busca exige presença da expedição; recursos seguem com ela até o retorno. Dois grupos podem viajar em paralelo. Um furgão recuperável e combustível de ida/volta estão ligados; dano em viagem e outras classes de veículo faltam.
- Cinco crises têm rolagem rara de 1/12 por dia **sob este modelo**, alvo, dano e cooldown; crise ativa não repete. Os efeitos narrativos e soluções específicas seguem pendentes.
- O salvamento JSON inclui estoque, pessoas, estruturas, projetos, buscas, crises, expedições, carga, equipamentos e estado do PRNG. Teste de restauração no meio da viagem confirma sequência igual após carregar.

## Ensaio integrado

`ENSAIO_SISTEMA_20261023.json` registra 500 trajetórias de cinco dias, 100 sementes por grupo de 2–6 heróis. Preparação hipotética: comida e água para dois dias por herói (máximo 12 de cada), dois de madeira, dois de sucata, uma munição; metade das sementes acolhe uma agricultora se possível; constrói horta e faz uma busca no mercado. Os resultados foram idênticos após repetição com as mesmas sementes.

| Heróis | Replays | Replays com déficit de comida | Déficit total de comida | Replays com déficit de água | Déficit total de água |
|---:|---:|---:|---:|---:|---:|
| 2 | 100 | 7 | 11 | 100 | 750 |
| 3 | 100 | 100 | 311 | 100 | 1050 |
| 4 | 100 | 100 | 611 | 100 | 1350 |
| 5 | 100 | 100 | 911 | 100 | 1650 |
| 6 | 100 | 100 | 1211 | 100 | 1950 |

O déficit mostra que **esta rota fixa não abastece o grupo**. Ela só busca uma vez e não usa hospital/estação para água, reservatório ou estratégia adaptativa. Portanto os números não são probabilidades de derrota, estimativa de equilíbrio nem campanha completa. O mesmo conjunto de crises aparece por tamanho de grupo porque as sementes são iguais e, nessa rota, somente a horta é alvo elegível. Não alterar rendimentos ou custos a partir desta tabela isolada.

## Limitações e próxima prova

Prioridade 1: fechar inventário na rodada tática (PA, troca de equipamentos, durabilidade), consumo de combustível e capacidade de veículo. Prioridade 2: tornar os 70 marcos e os 15 trabalhos integralmente executáveis e diferenciar crises. Prioridade 3: ligar missão e eventos aos dados, implementar os dois arcos e condições de vitória/derrota. Prioridade 4: só então diagramar e validar peças de 20 × 20 cm, fichas e cartas. Impressão física e playtest humano não ocorreram nesta evolução.

Resultado de regressão: 28 testes experimentais e 51 testes existentes aprovados. A suíte existente emitiu um `ResourceWarning` conhecido por arquivo de imagem não fechado em `tests/test_boards06.py:64`; não é falha de teste nem foi alterado neste lote.

O resultado foi regenerado após distinguir danos das crises: a perda pontual de comida por gafanhotos afeta 7/100 ensaios H2. Não houve ajuste de custos, probabilidades ou preparação para eliminar esses déficits.

Uma prova adicional de rodada cobre troca por 1 ação, arma com durabilidade, D6 e ruído, absorção por capacete e reexecução do próximo ataque após restaurar o estado do PRNG. A unidade de combate ainda não possui alvo/horda/alcance e não entra nos 500 ensaios econômicos.
