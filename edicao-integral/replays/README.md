# Replay reproduzível — A Cisterna H2

Arquivo: [`cisterna_h2_seed22.json`](cisterna_h2_seed22.json)

Execute da raiz do repositório:

```bash
python edicao-integral/verify_campaign_player02.py
```

Para reconstruir o artefato a partir do motor e conferir de novo:

```bash
python edicao-integral/verify_campaign_player02.py --write
python edicao-integral/verify_campaign_player02.py
```

O verificador repete as decisões com a mesma semente, compara o registro de
ações/recibos e reabre o save terminal. O certificado só é aceito se vier do
fluxo de coleta tática, retorno e conclusão do capítulo. O arquivo não é uma
estimativa de equilíbrio: é uma trajetória legal H2. Não houve resgate ou
promessa nesta rota; a regra oficial não exige resgate e só considera promessa
quando o grupo opta por assumir uma.

## Tentativa contínua bloqueada

`cistern_to_transmission_seed22_blocked.json` é schema 3. Reproduz vitória e
migração da Cisterna; na Estação, investiga Célia e copia uma pista por ações
físicas distintas. A equipe não consegue extrair antes do limite do relógio e
faz retirada de emergência no segmento 7. Célia não é recrutada, o rádio não é
decifrado e nenhum acesso militar é concedido. Repita com:

```bash
python3 edicao-integral/verify_continuous_campaign.py --write
python3 edicao-integral/verify_continuous_campaign.py
```

A saída é `local_defeat_clock_blocked`, não uma vitória de campanha. O relatório
`../NARRATIVE_DEPENDENCIES.md` registra o limite de PA/mapa. O antigo
verificador roteirizado está preservado como
`../verify_continuous_campaign_historical.py` e não deve ser usado como estado
atual.
