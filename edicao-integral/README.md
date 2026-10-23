# Zona Zero — evolução experimental do motor

Esta pasta é separada do kit físico 0.2. `RULES.md`, `CAMPAIGN.md`, cartas, artes e PDFs antigos continuam canônicos para a primeira partida humana; nada aqui os substitui. A evolução já executa **um cenário de um dia** de preparação → viagem → evento → combate → busca → retorno → produção/consumo → salvamento/restauração. Não executa os dois arcos completos e não possui PDFs novos.

Fontes editáveis: `data/build_system_data.py` gera `data/system.json`; `data/build_tactics_data.py` gera `data/tactics.json` a partir da geometria antiga; `data/equipment.json`, `data/cycle_cards.json` e `data/last_transmission.json` guardam itens e cartas experimentais. O motor atual é `system.py`, com `tactics.py`, `campaign.py` e `arc2.py`. `engine.py` e `simulate.py` são o primeiro protótipo histórico, não a fonte das regras novas.

Verificar:

```bash
python edicao-integral/validate_data.py
python -m unittest discover -s edicao-integral/tests -q
python edicao-integral/simulate_cycle.py --seed 20261023 --seeds 50
```

Leia `CYCLE_REPORT.md` para o cenário e os 1.250 replays de um dia, `SKILL_RULES.md` para os 70 marcos, `ARC2_STATUS.md` para os quatro portões implementados e a defesa final pendente, `PRINT_PREP.md` para medidas preliminares e `CHECKPOINT.md` para retomar. A edição ainda precisa de mapa militar, defesa final, duração real de mesa, playtest humano, artes, quantidade física de componentes e diagramação antes de virar Print & Play distribuível.
