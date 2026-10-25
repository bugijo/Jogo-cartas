# Checkpoint — migração Cisterna → Última Transmissão

Branch: `evolucao/zona-zero-sistema-v1`
Base informada: `81a61e05f1cca494a32f961c2048c6d0927b6908`
Commit local da unidade: `3b9fe68ebb50025b0b64ce68dd0259ed2d609ce1`
Estado remoto conferido: ainda em `81a61e0` no último `ls-remote`; unidade local aguardando push.
`main` e kit físico 0.2 não foram alterados.

## Entregue

- Migração explícita, legal, atômica e idempotente em
  `IntegratedCampaign.transition_to_last_transmission()`.
- Certificado da Cisterna, recibos de peças, capítulos/noites completos e
  ausência de fase pendente são pré-condições. A projeção é validada antes de
  anexar `world`; nenhuma pista, combustível, Bateria, veículo ou NPC é dado.
- Save de origem integral, inclusive recibos táticos de retorno, fica em
  arquivo de continuidade não gastável com hash determinístico de proveniência.
  O hash serve para consistência/replay; saves editáveis não têm assinatura
  criptográfica contra adulteração manual.
- Todos os 12 IDs de fundador têm identidade no motor regional. Téo/Célia não
  são duplicados como NPCs se migrarem como heróis; habilidades específicas
  deles da edição 0.2 ainda não foram portadas ao segundo motor.
- Moradores adultos/crianças/cães e seu estado são preservados. Humanos contam
  para alojamento; cães também contam para consumo. Comida/água viram contadores
  com o total exato e as cartas/lotes originais ficam no arquivo.
- Valores sem equivalente (materiais, estruturas, Moral/Saúde/Pressão, itens
  sem modelo regional, Bateria/van 0.2 e relações) ficam registrados e não são
  convertidos para recursos gastáveis.
- Replay contínuo parcial em
  `edicao-integral/verify_continuous_campaign.py` e artefato
  `edicao-integral/replays/cistern_to_transmission_seed22_blocked.json`.
  Começa na preparação, reproduz cinco dias/noites e 98 decisões de A Cisterna,
  migra, faz uma viagem abstrata do motor regional à Estação, busca, obtém o
  cartão de acesso e retorna. A chamada a `decode_radio()` é bloqueada em
  `Frequência indisponível`: estado tem 0 pistas e a missão exige 2.

## Verificação

- `python -m unittest discover -s edicao-integral/tests -q`: 237 testes passaram.
- `python edicao-integral/verify_campaign_player02.py`: vitória H2 seed 22,
  5 dias/noites, 3 expedições, 98 decisões; aprovado.
- `python edicao-integral/verify_continuous_campaign.py`: replay determinístico
  até o bloqueio do rádio e round-trip save/load; aprovado.
- `python edicao-integral/validate_data.py`, `python -m compileall -q
  edicao-integral` e `git diff --check`: aprovados.
- Nenhuma defesa final, campanha completa, impressão física ou playtest humano.

## Primeiro bloqueio e próximos bloqueios

1. Fonte legal das duas pistas: `Cistern02` não guarda pistas e a rota seed 22
   não as gera; existe uma carta regional experimental com +1 pista, mas não
   está ligada a gatilho/deck. Recrutar pesquisadores também não tem encontro
   ou acolhimento que o autorize. Não injetar pistas.
2. Depois: destino Posto ausente de `LOCATIONS`; a Oficina oferece no máximo
   três unidades de combustível, insuficientes para as seis exigidas para a
   instalação; recuperação regional de veículo diverge da regra 0.2, que exige
   Bateria, 2 PA e teste no Posto; expedições regionais ainda não abrem encontro
   tático.

Próxima tarefa recomendada: portar, citando a regra/carta oficial, fonte legal
para pistas; em seguida integrar Posto, Bateria, van, combustível e encontro
militar com custo/capacidade canônicos. Só então retomar o controlador de
campanha. Não chamar `final_defense()` até os portões narrativos e logísticos
serem cumpridos pelo motor.

Retomada após publicação:

```bash
git fetch origin evolucao/zona-zero-sistema-v1
git merge --ff-only origin/evolucao/zona-zero-sistema-v1
python edicao-integral/verify_campaign_player02.py
python edicao-integral/verify_continuous_campaign.py
python -m unittest discover -s edicao-integral/tests -q
```
