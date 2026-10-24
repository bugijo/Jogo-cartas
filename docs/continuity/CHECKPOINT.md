# Retomada do desenvolvimento experimental

## Estado da branch

- Branch: `evolucao/zona-zero-sistema-v1`.
- Base local atual fast-forward: `49cb7ccea2764b594bc07ea9015960f12095b823`.
- O remoto avançou após `d6acc24`: `9aeb935` liquidou cartas de retorno,
  `7787e48` adicionou certificação pelo integrador e `49cb7cc` atualizou gates.
- O ajuste adversarial da certificação está local e ainda precisa de commit e
  push; conferir novamente o remoto antes de publicar.
- Kit físico 0.2, `RULES.md`, `CAMPAIGN.md` e catálogo canônico permanecem
  preservados.

## Entregue nesta rodada (local)

- A viagem de ida paga cada trecho iniciado uma única vez antes da Emboscada;
  a entrada tática recebe apenas os trechos ainda não pagos.
- A entrada na expedição é bloqueada enquanto houver escolha, efeito automático
  ou Emboscada pendente.
- O recibo de Emboscada requer uma rodada completa e retorno seguro em Z1.
- Movimento inimigo da M1 agora usa o grafo real (Z1–Z2, Z1–Z5, Z2–Z6,
  Z5–Z6), e inimigos gastam a ativação abrindo a porta comum fechada 1–5.
- Ferimentos sofridos na M1 agora persistem no fundador ao concluir o retorno.
- Travel02 exige resolver cada ocorrência; testes cobrem eventos automáticos,
  efeitos, retorno ignorado, carga e save/load.
- Uma auditoria reproduziu certificação direta com três nomes falsos sem filtro
  nem peças; `Cistern02.certify_victory()` agora também exige filtro concluído e
  as três peças persistidas. Teste regressivo dedicado está incluído.

## Verificação executada

- `python -m unittest discover -s edicao-integral/tests -q`: 156 passaram após
  o fast-forward para `49cb7cc` e o teste do bypass.
- `python -m unittest discover -s tests -v`: 51 passaram; 1 aviso conhecido de
  arquivo PNG aberto em `tests/test_boards06.py:64`; levou 77 s.
- `python -m compileall -q edicao-integral src`: passou.
- `python edicao-integral/validate_data.py`: passou (125 IDs únicos, 10
  protagonistas, 70 habilidades, 15 NPCs, 8 mapas táticos).
- `git diff --check`: passou.
- Auditoria independente somente leitura confirmou que a perseguição segue a
  topologia M1 e a regra de porta; apontou surgimento/Horda e fadiga noturna
  ainda ausentes.
- Auditoria independente confirmou que a certificação por nomes isolados foi
  fechada. Outra revisão apontou bloqueios críticos de retorno, liquidação
  atômica e efeitos da ida; consultar `AUDIT_REPORT.md`.

## Bloqueios ativos

- M1 ainda não aplica surgimento/Horda inicial, pressão local, Horda por
  pressão/noite ou fadiga nos segmentos noturnos. Ataques não usam armas,
  munição ou ruído. Ferimentos agora persistem, mas a integração segue parcial.
- Viagem ainda não está integrada por completo ao retorno: custos e efeitos não
  são todos liquidados no estoque real e efeitos contextuais como material
  deixado no caminho precisam de representação física persistente.
- Resgates, promessas, trabalho, eventos diários, cercos e encerramento dos
  cinco dias não formam ainda um ciclo completo executável.
- Não há trajetória legal comprovada desde preparação até vitória da Cisterna
  e transição para Última Transmissão; campanhas H2–H6 não foram executadas.
- Nenhuma simulação de campanha completa, produção de PDF novo, impressão,
  montagem física ou playtest humano foi feita nesta rodada.

## Próxima retomada

1. Conferir `git status`, `git fetch origin evolucao/zona-zero-sistema-v1` e
   reconciliar eventual avanço remoto sem reescrever histórico.
2. Concluir o fluxo de Horda/ruído/fadiga da M1 com estado de baralho
   persistente e regras canônicas, incluindo teste de salvar/restaurar.
3. Integrar arma, munição e desgaste real da expedição à Emboscada sem criar
   carga ou recursos.
4. Integrar ida e volta de Viagem, recursos carregados e efeitos ao estado do
   abrigo; então auditar resgates e sequência dos cinco dias.
5. Somente após um ciclo legal reproduzível, desbloquear replays completos e
   preparar a edição física experimental.

Comando de retomada:

```bash
git status --short --branch
git fetch origin evolucao/zona-zero-sistema-v1
git merge --ff-only origin/evolucao/zona-zero-sistema-v1
python -m unittest discover -s edicao-integral/tests -q
python -m unittest discover -s tests -q
python -m compileall -q edicao-integral src
python edicao-integral/validate_data.py
git diff --check
```
