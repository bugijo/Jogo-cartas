# Escritório Dev, barra de progresso e jogadores virtuais (2026-10-29)

## Barra de progresso no Claude Code Desktop

| Pergunta | Resposta |
|---|---|
| Mecanismo | *Mod* oficial do Claude Code (skill `plugin-authoring`, versão 2.1.308 do Desktop): faixa acima do campo de mensagem (`AbovePrompt`), painel ao lado do chat (`/zz-progresso`) e entrada na linha de status. Nada do app é modificado. |
| Fonte dos dados | `docs/continuity/progress.json` (fora do git), escrito só por `tools/progress.py`. |
| Percentual | Soma dos pesos dos critérios marcados com `--evidence` (modelo do Hermes Dev Office). Nunca estimado. |
| Atualização | Automática: o mod relê o arquivo a cada 3 s e só redesenha quando ele muda. Quem marca os marcos é o agente, ao concluir cada critério verificável. |
| Onde mora o mod | Cópia versionada em `tools/desktop-mod/zona-zero-progresso/`. A cópia que carrega fica na pasta de mods da sessão (`~/.claude/dev-mods/<sessão>/`); para carregar em outras sessões é preciso instalar o mod ou apontar `CLAUDE_CODE_PLUGIN_DIRS` para a cópia do repositório — mudança de configuração persistente, só com sua aprovação. |
| Limitação | O mod só carrega depois de você aceitar "Turn them on" no aviso do app, e então no fim do turno. A lista de tarefas nativa do Desktop (abaixo da mensagem do agente) continua sendo o acompanhamento passo a passo. |

```bash
python3 edicao-integral/tools/progress.py start "Tarefa" --specialist simulacao --criteria "impl:Implementação:40" "testes:Testes:30" "docs:Docs:30"
python3 edicao-integral/tools/progress.py done impl --evidence "commit abc123"
python3 edicao-integral/tools/progress.py stage testes   # planejamento|implementação|testes|simulação|revisão|concluída
python3 edicao-integral/tools/progress.py tests "412 OK" ; python3 edicao-integral/tools/progress.py approval "regra X"
```

## Hermes como referência (somente leitura)

`Hermes Pc/hermes_core/dev_office.py`: metas com épicos e pesos somando 100,
critérios de aceite executáveis, evidências gravadas, percentual = pesos de
tarefas concluídas com evidência, bloqueio após tentativas idênticas, checkpoint
por tarefa e painel web local. Aqui foi reaproveitada só a ideia (pesos com
evidência, papéis, critérios); o Zona Zero continua usando `TASK_QUEUE.json` e
`CHECKPOINT.md` como fila e checkpoint, sem banco nem serviço.

## Papéis (`dev_office.py`)

| Chave | Papel | Entrega verificável |
|---|---|---|
| diretor | Diretor de Desenvolvimento | checkpoint, fila, commits após `check.sh full` |
| game_designer | Game Designer Sênior | decisão ou pendência no MANUAL_EXPERIMENTAL |
| board_games | Especialista em Board Games | mapa carregado e teste de rota |
| card_games | Especialista em Card Games | auditoria de baralho com números |
| narrativa | Designer Narrativo | dependências narrativas registradas |
| balanceamento | Especialista em Balanceamento | medição real × protótipo |
| simulacao | Engenheiro de Simulação | código, testes, determinismo, seed 22 intacta |
| qa | QA de Jogos | teste de regressão e suíte completa |
| grafico | Designer Gráfico | material gerado, kit 0.2 sem diff |
| ux_pesquisa | Pesquisador de Experiência do Jogador | hipóteses e plano de playtest humano |

Os papéis não ficam ativos. `route(descrição)` indica quem acionar; o Diretor
executa em sequência na sessão e usa subagentes do Claude Code só quando a
tarefa é grande e independente (cada subagente começa sem contexto e custa
tokens).

## Jogadores virtuais (`virtual_players.py`, `simulate_virtual_players.py`)

18 personas fictícias (6 por grupo: A até 19 anos, B 21–35, C 36+), cada uma com
risco, exploração, planejamento, cooperação, gestão de recursos,
assertividade, experiência, resiliência, estilo de comunicação, objetivo e
reação sob pressão. As idades são traços fictícios; os valores dos traços foram
escolhidos por mim e **determinam** os resultados abaixo.

- Cada persona é um fundador. No amanhecer a mesa vota a política (voto
  ponderado pela assertividade; líder = mais assertiva); sob pressão (falta
  de comida/água ou herói ferido) cada persona arrisca, recua ou segue.
- Mesa sem maioria de planejamento segue o roteiro fixo da Cisterna.
- Toda ação passa pelo controlador da Cisterna, que só lê estado visível na
  mesa. Leitura errada de regra vira proposta ilegal testada numa cópia do
  jogo; o motor recusa e nada muda.
- Com a política de referência, a mesa reproduz exatamente o controlador de
  referência (52/150 vitórias; teste dedicado).

### Resultado (sementes 1–30, tamanhos 2–6, 150 mesas por grupo)

| Grupo | Vitórias | Mesas no roteiro fixo | Noites médias | Heróis incapacitados | Erros de regra/mesa | Conflitos/mesa | Concordância com líder | Dias no regional (vitórias) |
|---|---|---|---|---|---|---|---|---|
| A | 4 | 125 | 3,46 | 223 | 5,27 | 11,8 | 0,85 | 4,25 |
| B | 34 | 0 | 4,99 | 363 | 3,95 | 34,1 | 0,72 | 2,94 |
| C | 34 | 11 | 4,87 | 300 | 5,17 | 17,1 | 0,90 | 2,85 |
| mista | 26 | 38 | 4,53 | 322 | 5,63 | 32,1 | 0,75 | 2,77 |

Mesas que planejam adaptativamente: 95/426 vitórias; no roteiro fixo: 3/174.
Nenhuma mesa sobrevive aos 15 dias regionais (mesma economia de comida já
medida).

### Hipóteses (não validadas; testar com pessoas)

1. O fator dominante é planejar o dia a dia (reservas, trabalho do filtro,
   comida); seguir um roteiro fixo quase sempre perde. Iniciantes podem precisar
   de um guia de planejamento do amanhecer.
2. Mesas com perfis de planejamento alto vencem mais, mas discutem mais (B e
   mistas): o jogo pode gerar debate longo em decisões de política.
3. Mesas que concordam muito com o líder (C) vencem tanto quanto B: possível
   dependência de líder, a observar no playtest (efeito "quarterback").
4. A Cisterna fere muito: incapacitações são frequentes em todas as mesas.
5. Vencer mais não significa gostar mais: diversão, clareza e interesse só se
   medem com pessoas (`PLAYTEST_HUMANO.md`).

Limitações: personas, traços e mapeamento para a política são escolhas de
projeto; o controlador é o mesmo para todas as mesas (muda só a política); não
há escolha individual por herói dentro do mapa tático; o campo
`rule_errors` mede compreensão simulada, não dificuldade real das regras.
