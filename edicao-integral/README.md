# Zona Zero — sistema integral em desenvolvimento

Esta pasta é uma **evolução experimental separada**. O kit físico 0.2, suas regras, campanha, artes e PDFs continuam canônicos para a primeira partida humana. Os seis atributos e a economia abaixo ainda não substituem `RULES.md` ou `CAMPAIGN.md`.

Unidade funcional atual: dados estruturados, quatro registros-modelo de equipamento, inventário espacial, combate D6 com semente, consumo/produção, alojamento, construção inicial, progressão, salvamento local e testes. Não existe aqui uma campanha completa, 16 placas prontas nem PDFs finais de impressão. O simulador verifica somente as operações implementadas; suas rodadas não estimam equilíbrio nem duração de mesa.

Executar: `python -m unittest discover -s edicao-integral/tests -v` e `python edicao-integral/simulate.py --seed 20261023 --runs 1000`.

Os nomes de dez protagonistas foram preservados do catálogo 0.2. Os outros 14 heróis existentes continuam intactos no kit anterior; uma migração futura para o papel de NPC exigirá revisão de conteúdo. Nenhuma identidade foi apagada.

## Sistema expandido

`data/system.json` é reconstruído por `python edicao-integral/data/build_system_data.py`; `system.py` fornece um estado de campanha experimental. Os 10 protagonistas têm 70 marcos tipados, mas os textos e efeitos ainda não foram aprovados como regras de mesa. Quinze NPCs possuem perfil, nível e tarefa; produção de recursos, construção, reparo, investigação, resgate clínico e defesa têm efeitos de motor neste lote. Estruturas, viagens e crises são cenários de teste, não campanha pronta.

O ensaio expandido é `python edicao-integral/simulate_system.py --seed 20261023 --seeds 100`; resultados e pressupostos estão em `VALIDATION.md`. `system.py` é o motor principal deste experimento; `engine.py` permanece como primeiro protótipo isolado para comparação e não deve ser usado como fonte das regras novas.

Validar referências e custos: `python edicao-integral/validate_data.py`. O relatório imprime contagens reais de IDs; essa validação não substitui revisão de conteúdo ou impressão.

O cenário de um dia está em `campaign.py`; sua prova em `PROVA_CICLO_17.json`. Os portões parciais do segundo arco estão em `arc2.py` e `ARC2_STATUS.md`. A defesa final e o modo sobrevivência livre ainda não existem.
