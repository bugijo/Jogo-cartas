# Retomada do desenvolvimento experimental

## Estado da branch

- Branch: `evolucao/zona-zero-sistema-v1`.
- Base remota conferida nesta rodada: `91ca01146d04cd1c240f3ac7b93a1ca62d5127fc`.
- O lote local atual ainda precisa de commit e push; confirme novamente o remoto
  antes de publicar, pois a branch tem avançado durante as sessões.
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

## Verificação executada

- `python -m unittest discover -s edicao-integral/tests -q`: 151 passaram.
- `python -m unittest discover -s tests -v`: 51 passaram; 1 aviso conhecido de
  arquivo PNG aberto em `tests/test_boards06.py:64`; levou 77 s.
- `python -m compileall -q edicao-integral src`: passou.
- `python edicao-integral/validate_data.py`: passou (125 IDs únicos, 10
  protagonistas, 70 habilidades, 15 NPCs, 8 mapas táticos).
- `git diff --check`: passou.
- Auditoria independente somente leitura confirmou que a perseguição segue a
  topologia M1 e a regra de porta; apontou surgimento/Horda e fadiga noturna
  ainda ausentes.

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
