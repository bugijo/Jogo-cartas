# Retomada do desenvolvimento experimental

## Estado atual — 2026-10-24

- HEAD de início: local e remoto `931d572e6cb318f76933af8498e79549190a97e3`;
  branch `evolucao/zona-zero-sistema-v1`, árvore limpa. Kit físico 0.2,
  `RULES.md`, `CAMPAIGN.md`
  e `content/catalog.json` permanecem intactos. Os cinco pontos de coleta de
  equipamento foram estruturados em `edicao-integral/data/equipment_pickups02.json`.
- Implementado `HordeDeck02`: compra determinística, descarte, embaralhamento
  reproduzível ao esgotar e validação de snapshot. Campanha, expedição e M1
  compartilham e salvam o mesmo sapato de Horda; snapshots antigos migram.
- M1 agora usa o grafo/porta, equipamentos e munição existentes, registra
  tiros/ruído, ativa inimigos, aumenta pressão, compra Hordas por pressão/noite
  e aplica fadiga em cada segmento 9–10. Entrada sem Emboscada preserva fadiga
  da escolha de Viagem. A lista de equipamentos de coleta está no catálogo e
  o inventário do herói persiste após entrega; emergência perde o item novo.
- Viagem reserva comida, água e materiais do estoque físico no início, impede
  declaração acima do estoque ou da capacidade. A reserva escolhe cartas
  físicas inteiras pelos cursors reais (inclusive cartas parciais) e devolve
  os mesmos cursors restantes uma vez após retorno legal.
  Escolhas de fadiga e rota são transferidas ao estado persistente; VIA-0003
  pula corretamente o trecho de retorno. Cães VIA-0009 chegam vinculados a uma
  família elegível. Viagem/retorno pendente bloqueia nova expedição e avanço.
- A liquidação do retorno roda em cópia e só publica recebimentos completos;
  cartas/decisões pendentes permanecem retomáveis. A retirada na M1 de retorno
  fecha o estado e aplica perda de carga/peças no chão; retirada pode ser
  escolhida mesmo no relógio 10.
- Verificação desta sessão: `python -m unittest discover -s
  edicao-integral/tests -q` (196 testes); `compileall`, validação (125 IDs,
  10 heróis, 70 habilidades, 15 NPCs, 8 mapas e 5 pontos de coleta) e
  `git diff --check`.
- Regressão de preservação: `python -m unittest discover -s tests -q` passou
  (51 testes). Um `ResourceWarning` preexistente aponta arquivo aberto em
  `tests/test_boards06.py:64`; não houve falha.
- Lote atual corrige dano acima de 3 ferimentos e impõe o limite de duas armas;
  também implementa o sapato persistente de Viagem com descarte,
  reembaralhamento determinístico, validação do trajeto e save/load.
- Pendências: efeito mecânico de rota/Ponte ainda não está ligado a navegação;
  carta extra de Viagem nos segmentos noturnos ainda não está resolvida;
  promessas, eventos, noites,
  cercos e sequência completa da campanha continuam incompletos. A M1 usa as
  armas legais disponíveis no inventário, mas isso não valida o balanceamento.
- O saldo de viagem é agregado para a equipe; fichas individuais de portadores
  e movimentação de carga dentro da expedição ainda não estão integradas. O
  limite atual comprova espaço total disponível, não transferência tática de
  provisões entre heróis.
- O lote M1/retorno foi publicado em `931d572`; os testes do lote desta sessão
  passaram e faltam commit/push.
- Não foram executadas campanhas completas, simulações de vitória, impressão
  física ou playtest humano.

Próximo passo: encerrar/publicar este lote; depois resolver viagem por
segmento (carta noturna extra) e efeitos mecânicos de Ponte/rota antes de
ampliar eventos, promessas e fases noturnas da Cisterna.

## Estado da branch

- Branch: `evolucao/zona-zero-sistema-v1`.
- Os checkpoints abaixo são histórico; prevalece o estado atual acima.
- Kit físico 0.2, `RULES.md`, `CAMPAIGN.md` e catálogo canônico permanecem
  preservados.

## Histórico de entregas anteriores

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
