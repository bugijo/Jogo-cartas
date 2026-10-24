# Retomada prioritária — ciclo diário/Cerco e bloqueio do replay (2026-10-24)

## Estado de código nesta retomada

- Base remota confirmada em `4add0b3c2c86cbb89ed19119bcd7826fafe9b486`; entrega desta retomada publicada em `6dfe141` na branch `evolucao/zona-zero-sistema-v1`; sem divergência remota.
- `Cistern02` aplica EVE-0001..0005 uma vez, na ordem de dia. EVE-0003 enfileira Barulho no vale (Força 4); eventos de pressão seguem `raise_pressure`.
- Cartas CER usam baralho determinístico e persistente; força normal vem da carta revelada, CER-0005 considera relação Ponte e CER-0006 permite cancelamento apenas mediante pagamento de quatro porções de comida e água. A resolução grava descarte/recibo; um gatilho arbitrário não pode ser injetado pela API.
- O plano de vigias do dia 5 fica bloqueado após refeição/resolução; recibo final da quinta noite é exigido para `verified_victory`. Saves passam por checagem estrutural de calendário, cerco, baralho e certificado. Isso não autentica saves editados manualmente.
- A API pública `start_expedition()` agora recusa entrada sem Viagem; a abertura privada `start_tactical_fixture` aparece somente nas provas isoladas. `start_travel → resolver ocorrências → enter_expedition` continua sendo o caminho integrado.
- O teste adversarial de um save de dia 1 com flags/peças/nomes falsos agora falha ao certificar/carregar.
- Suíte experimental: 220 passou; suíte legada: 51 passou; `compileall`, validador (125 IDs) e `git diff --check` passaram. O teste do PNG/PDF com `ResourceWarning` elevado a erro também passou. O teste legado foi corrigido para fechar o documento PyMuPDF.

## Resultado do pedido de campanha

- Dias completos reproduzidos pelo executor legal integrado: **0/5**.
- Foi executada **1 expedição integrada legal** em teste focado (Dia 2, Oficina, seed 14), com Viagem do sapato, ações táticas e entrega de Conexões só após retorno. Não é replay de campanha.
- Os cinco perfis do `replay_cistern02_fixed.py` continuam alimentados por entregas do oráculo antigo e são apenas testes de paridade, não partidas legais.
- Eventos EVE: cinco eventos são aplicados pelo estado. O evento fixo do dia 3 e cartas CER têm APIs persistentes e testes de fase; ainda não há controlador integrado que coordene expedição, retorno, trabalho, cerco, refeição, intenção e resultado numa noite jogável.
- `verified_victory`: não emitido por campanha real. Migração para Última Transmissão: não ocorreu.

## Primeiro bloqueio concreto restante

A integração não possui executor de noite/expedição que gere recibos táticos legais de Conexões, Bomba e Membrana, devolva-os ao abrigo e então execute os cinco dias. Os métodos de `Cistern02` para as peças ainda são estado de baixo nível; falta um controlador integrado de Cerco/Evento/Noite e uma trajetória de Estação completa. Próxima tarefa: criar testes failing para um único ciclo legal H2 (Mercado→retorno; Oficina→Conexões e retorno; Estação→Bomba/Membrana e retorno), ligando a fase de cerco e consumo antes de ampliar o roteiro.

O método `Cistern02.receive_part()` ainda é uma entrada administrativa de baixo nível e não prova coleta; a rota normal integrada precisa chamar apenas entrega de recibos táticos. O resultado de revisão do save é estrutural, não criptográfico: JSON pode ser editado e um estado sintaticamente consistente ainda pode ser forjado. Não prometer resistência a adulteração manual. Kit físico 0.2, regras oficiais e catálogo não foram alterados. Nenhuma impressão física ou sessão humana ocorreu.

# Retomada do desenvolvimento experimental

## Estado atual — 2026-10-24

- HEAD de início: `931d572e6cb318f76933af8498e79549190a97e3`; HEAD publicado
  atual `06b03f45ccb9234e25e8b0318e210c2d84f16a8b` na branch
  `evolucao/zona-zero-sistema-v1`, árvore limpa. Kit físico 0.2,
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
  edicao-integral/tests -q` (201 testes); `compileall`, validação (125 IDs,
  10 heróis, 70 habilidades, 15 NPCs, 8 mapas e 5 pontos de coleta) e
  `git diff --check`.
- Regressão de preservação: `python -m unittest discover -s tests -q` passou
  (51 testes). Um `ResourceWarning` preexistente aponta arquivo aberto em
  `tests/test_boards06.py:64`; não houve falha.
- Lote publicado corrige dano acima de 3 ferimentos, limita loadout a duas
  armas e implementa sapato persistente VIA. Ajuste local novo prepara um plano
  determinístico de reshuffle, mas só move o descarte quando uma carta reciclada
  é realmente comprada, preservando cartas que restam se a viagem abortar.
- Pendências: efeito mecânico de rota/Ponte ainda não está ligado a navegação;
  carta extra de Viagem nos segmentos noturnos ainda não está resolvida;
  promessas, eventos, noites,
  cercos e sequência completa da campanha continuam incompletos. A M1 usa as
  armas legais disponíveis no inventário, mas isso não valida o balanceamento.
- O saldo de viagem é agregado para a equipe; fichas individuais de portadores
  e movimentação de carga dentro da expedição ainda não estão integradas. O
  limite atual comprova espaço total disponível, não transferência tática de
  provisões entre heróis.
- O lote M1/retorno está em `931d572`; sapato e correções em `b399d41`, testes
  de ida/volta em `1ca150e`, e reshuffle/snapshot em `06b03f4`.
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
