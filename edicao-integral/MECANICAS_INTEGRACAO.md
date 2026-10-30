# Integração total das mecânicas — auditoria, matriz e plano (2026-10-30)

Missão "Integração total das mecânicas". Arte definitiva fora de escopo: esta
fase entrega regras, motor, simulação, especificação funcional de componentes
e o pacote de transição para direção artística.

## 1. Auditoria (início da missão)

| Item | Estado |
|---|---|
| Branch | `evolucao/zona-zero-sistema-v1`, HEAD `e53d358`, 31 commits locais sem push, árvore limpa |
| Outras branches | só remotas de arte (`arte/*`) e o físico 0.2; nenhuma alteração pendente |
| Sessões paralelas | nenhuma no Zona Zero (as abertas são de outros projetos) |
| Skill | `.claude/skills/zona-zero-game-director` (papéis, invariantes, ciclo) |
| Personas | 18 em 3 grupos (`virtual_players.py`, `experiments/persona_community.py`) |
| Testes | `tools/check.sh full` verde no HEAD |
| Protegidos | kit 0.2, `RULES.md`, `CAMPAIGN.md`, `content/`, seed 22 (98 decisões), replays, sementes 91–120 |

## 2. Matriz de rastreabilidade (pedido da missão → regra → código → teste → simulação → componente)

Legenda: ✓ pronto · ◐ existe, mas não no formato pedido · ✗ falta.

| § | Pedido | Antes desta missão | Lacuna | Bloco |
|---|---|---|---|---|
| 2 | Acampamento como sistema interligado | ◐ comunidade (trabalhos, viagens, obras, Moral, chegadas) | crescimento ainda é um número abstrato de terreno | D-24 |
| 3 | Tabuleiro 2×2 → 3×3 → … com categorias por lote | ◐ terreno abstrato 7 + cerca +3 | grade física, símbolos por lote, níveis, custo de expansão | D-24 |
| 4 | Barracas (1/2/família), alojamento, família com barraca própria | ◐ camas abstratas (8 + Alojamento +4) | barracas que ocupam lote, família traz barraca, penalidade proporcional | D-24 |
| 5 | Horta por lotes, trabalhador cuida de 2 (agricultor 4), água, falha | ◐ quatro hortas diferentes (EXP-BLD-01, §61, protótipo D, canteiro) | unificar em lotes de horta com água e perda | D-25 |
| 6 | Caça, pesca, coleta, armadilhas persistentes, ambientação | ✓ viagens, entorno finito, armadilhas (`community.dawn`) | manutenção de armadilha, espécies coerentes | D-27 |
| 7 | Economia de porções (carne 4, fruta hidrata, reservas, perdas) | ✓ porção = 1 comida; carne 4; fruta água a cada 2; carne estraga | estoque por categoria e nível | D-24 |
| 8 | Custo de esforço das obras | ✗ obra custa só material e trabalho | ração de obra nas obras pesadas, pausa na crise | D-26 |
| 9 | Painel físico de controle | ◐ `print/painel_abrigo.pdf` (estoques, Moral, dias) | nível, população/camas, capacidades por nível, crise 0–10 | D-30 |
| 10 | Crise alimentar 0–10 proporcional ao déficit | ◐ Moral 0–5 cai 1 por noite com alguém sem porção | escala proporcional, faixas com efeito, recuperação | D-26 |
| 11 | Expedições de vários dias com o abrigo funcionando | ✓ viagens automáticas, dia regional, trabalhos sem heróis | conferir em cenário E | D-28 |
| 12 | Conhecimento encontrado nas expedições | ✗ | cartas de projeto por local, desbloqueios | D-27 |
| 13 | Profissões revisadas, alternativas sem especialista | ◐ 10 + comum | fundir parecidas, caminho sem especialista | D-27 |
| 14 | Equilíbrio 2–6 heróis | ✓ D-17 (57–82% por tamanho) | remedir depois das mudanças | D-28 |
| 15 | Simulação integrada, situações A–H | ◐ campanhas inteiras; sem cenários dirigidos | `experiments/camp_scenarios.py` | D-28 |
| 16 | Administrável na mesa | ◐ | auditoria de contabilidade por amanhecer | D-29 |
| 17 | Baralhos definidos funcionalmente, ids estáveis | ✓ inventário 383 cartas | atualizar com barracas, conhecimento, lotes | D-31 |
| 18 | Pacote de transição para direção artística | ✗ | documento único | D-32 |
| — | Vitória da Última Transmissão (D-23) | ◐ defesa ganha em ~20% | seguir depois do acampamento | D-23 |

## 3. Decisões de desenho (diretor, com base no estado medido)

1. **Acampamento em lotes** (modo `camp` da Comunidade). Grade 2×2 → 3×3 → 4×4
   (3 níveis; um 4º só se a simulação mostrar lotes esgotados antes do dia 25).
   Cada lote tem 1–2 símbolos de categoria. O núcleo (fogueira + estoque) já
   começa construído. A cerca ampliada passa a ser a própria expansão.
2. **Unificar as hortas**: EXP-BLD-01, Horta §61 migrada, protótipo D e canteiro
   viram **lotes de horta**. Um trabalhador cuida de 2 lotes (agricultor 4);
   cada lote cuidado e regado dá 1 porção; 1 água a cada 2 lotes; D6 = 1 perde
   1 porção do dia. A Horta da Cisterna chega como lote já plantado.
3. **Barracas ocupam lotes**: barraca (2 lugares, até 2 por lote), barraca
   familiar (4, 1 por lote, só encontrada ou trazida), alojamento coletivo (8,
   obra pesada) e seu nível 2 (+4). Pessoas sem cama não recuperam Vida; acima
   de 2 sem cama a Crise sobe.
4. **Estoque por categoria** (resolve a água ocupando o espaço da comida):
   comida pelo nível da Despensa, água por tanques, madeira e metal em trilhas
   próprias de 0–20; remédio, munição, combustível e peças continuam como cartas.
5. **Crise 0–10 substitui o Moral da escassez** (uma trilha, não duas):
   sobe pelo déficit proporcional e pela repetição, desce com noites servidas;
   faixas leve/moderada/grave com efeitos que não cortam a produção de comida
   (evita a espiral). 10 = colapso (derrota parcial existente).
6. **Ração de obra**: só obras pesadas cobram 1 porção por trabalho feito.
7. **Conhecimento**: uma carta por local tático, ganha na primeira busca do
   local; desbloqueia uma melhoria que exige estrutura + profissional (ou 1
   trabalho a mais sem ele).
8. **Profissões**: pescador funde em caçador e lenhador em coletor (mesma
   posição no baralho, para não mudar o sorteio das sementes).

Números iniciais são hipóteses; o ajuste fica em `COMUNIDADE_BALANCEAMENTO.md`.

## 4. Plano único (fila do diretor)

| Id | Bloco | Critério de conclusão |
|---|---|---|
| D-24 | Grade, lotes, barracas, expansão, estoque por categoria | motor + testes; campanhas 1–30 sem erro do motor |
| D-25 | Horta por lotes (unificação) | testes; produção por trabalhador medida |
| D-26 | Crise 0–10 e ração de obra | testes; T1–T5 em 1–30 e 31–90 |
| D-27 | Conhecimento, profissões fundidas, armadilha com manutenção | testes; uso medido |
| D-28 | Situações A–H, tamanhos 2–6, personas | relatório por situação |
| D-29 | Auditoria de mesa (contas por amanhecer) | ≤ 8 atualizações de marcador por amanhecer típico |
| D-30 | Painel e tabuleiro do acampamento (funcional, sem arte) | PDF funcional + manifesto |
| D-31 | Inventário técnico de componentes | ids estáveis, quantidades, finalidade |
| D-32 | Pacote de transição para direção artística | documento único |
| D-23 | Vitória e prazo da Última Transmissão | meta registrada na fila |
