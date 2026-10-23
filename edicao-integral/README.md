# Zona Zero — motor experimental

Esta pasta não substitui o kit físico 0.2. `../RULES.md`, `../CAMPAIGN.md`, `../content/catalog.json` e os PDFs antigos seguem como fontes da primeira caixa. O motor executa um cenário de **um dia** com viagem, evento, combate, busca, retorno, economia e salvamento. `integrated_campaign.py` fornece a camada contínua: prepara A Cisterna com os dados canônicos, exige a obtenção das três peças pelo fluxo de missões, transfere protagonistas/recursos somente após o filtro e retoma a Última Transmissão no `World`. Os textos e regras originais continuam preservados; a integração é uma adaptação experimental, não uma substituição silenciosa da edição 0.2.

Arquivos estruturados: `data/system.json`, `data/equipment.json`, `data/cycle_cards.json`, `data/last_transmission.json` e `data/tactics.json`. Os geradores `data/build_system_data.py` e `data/build_tactics_data.py` são editáveis. `tactics.json` inclui as seis geometrias exatas do catálogo 0.2 e dois mapas experimentais; Posto e Condomínio são apenas referência até existir destino regional correspondente. Os motores são `system.py`, `tactics.py`, `campaign.py` e `arc2.py`. `cistern02.py` é uma porta parcial e isolada das regras oficiais; ainda não autoriza a transição narrativa.

Verificações:

```bash
python edicao-integral/validate_data.py
python -m unittest discover -s edicao-integral/tests -q
python -m unittest discover -s tests -q
python edicao-integral/simulate_defense.py --seeds 50 --seed 20261023
python -m unittest edicao-integral.tests.test_integrated_campaign -q
```

`CYCLE_REPORT.md` descreve 1.250 replays de um dia. `DEFENSE_REPORT.md` e `ENSAIO_DEFESA_20261023.json` descrevem 250 defesas isoladas, com pré-requisitos injetados. `CAMPAIGN_INTEGRATION.md` documenta diferenças impeditivas entre os motores. `ARC2_STATUS.md` detalha o arco experimental e `CHECKPOINT.md` registra a próxima unidade. Ainda não foram gerados PDFs desta edição, nem ocorreu impressão física ou playtest humano.
