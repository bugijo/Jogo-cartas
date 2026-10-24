# Checkpoint de retomada — Operação Campanha Viva

Branch: `evolucao/zona-zero-sistema-v1`
Base remota ao iniciar: `54a95f1a7a498e54a6e39748dca749b2319a6729`
Commits locais desta sessão: `c8a4a0f` (fases diárias, trabalho nominal e resgate pago), seguido pelo commit do replay de campanha.
Main e kit físico 0.2 permanecem intocados.

## Comprovado nesta sessão

- O controlador `edicao-integral/campaign_player02.py` inicia H2 legalmente a
  partir de semente e usa as APIs de viagem, tática, abrigo e campanha.
- Seed 22 completou Mercado no dia 1, Oficina no dia 2 e Estação no dia 3;
  recuperou e entregou Conexões, Bomba e Membrana com recibos táticos únicos.
- Foram processados os eventos `ZC-EVE-0001` a `ZC-EVE-0005`, cinco refeições,
  o cerco de missão do dia 3 e o cerco de Pressão do dia 5. O filtro concluiu
  A/B no dia 4 e C no dia 5; a noite final terminou abastecida, com Saúde/Moral
  positivas e sem ameaça pendente.
- O motor emitiu `verified_victory`. O replay registra seed, preparação,
  decisões, recibos, eventos, cercos, estado final e save terminal. O verificador
  repete as decisões e confere save/load.
- Nesta rota não houve grupo de resgate ou promessa assumida. A campanha oficial
  não exige resgate para a vitória; promessa só existe quando assumida.

## Evidência e comando

```bash
python edicao-integral/verify_campaign_player02.py --write
python edicao-integral/verify_campaign_player02.py
python -m unittest discover -s edicao-integral/tests -q
python edicao-integral/validate_data.py
python -m compileall -q edicao-integral src
git diff --check
```

Replay: `edicao-integral/replays/cisterna_h2_seed22.json`.
Relatório de fronteira entre arcos: `edicao-integral/CAMPAIGN_INTEGRATION.md`.

## Limitações reais

- Uma vitória H2 seed 22 é prova de possibilidade, não de equilíbrio ou de
  sucesso geral. Ensaios de outras sementes incluíram emergência, déficit,
  derrota parcial e falhas da política; eles não foram usados como taxa de
  vitória.
- O controlador ainda não é um jogador adaptativo completo. Algumas sementes
  param por plano de carga inadequado ou por uma expedição perdida.
- Ainda não há migração canônica dos fundadores e estado persistente para
  Última Transmissão. Não há campanha contínua certificada.
- A mecânica de promessas em encontros depende da decisão e do prazo anotado;
  certos textos de encontros ainda não definem um procedimento automatizado
  completo. A rota vencedora não precisou dela.
- Impressão e playtest humano seguem pendentes.

## Próximo passo

Implementar e testar a migração de um save `verified_victory` para Última
Transmissão, preservando elenco, vínculos, ferimentos, equipamento e estoque.
Depois, generalizar o controlador H2 e executar a cobertura de 2–6 heróis.

Retomada:

```bash
git fetch origin evolucao/zona-zero-sistema-v1
git merge --ff-only origin/evolucao/zona-zero-sistema-v1
python edicao-integral/verify_campaign_player02.py
python -m unittest discover -s edicao-integral/tests -q
```
