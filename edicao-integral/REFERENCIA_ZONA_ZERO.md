# Referência consolidada — Sobreviventes: Zona Zero (motor experimental)

Documento de referência para quem desenvolve (pessoas e agentes). Antes de
mudar uma regra, procure-a aqui. Se a regra estiver marcada como **aprovada**,
não a substitua por preferência própria: registre a proposta e peça decisão.

- Regras do jogo físico 0.2: `RULES.md`, `CAMPAIGN.md`, `content/` (intactos,
  não editar nesta branch).
- Decisões aprovadas e leituras do motor: `MANUAL_EXPERIMENTAL.md`.
- Estado de trabalho: `docs/continuity/CHECKPOINT.md` (bloco "Estado ativo").
- Este arquivo: identidade, progressão, status de cada mecânica e matriz de
  rastreabilidade (regra → documento → código → teste).

## 1. Identidade

Jogo físico cooperativo de sobrevivência zumbi: heróis dos jogadores exploram
locais em mapas táticos, combatem, resgatam sobreviventes e trazem recursos; o
acampamento cresce com construções, trabalhadores e produção; toda noite a
comunidade come e bebe; eventos, ameaças e consequências pressionam; campanhas
narrativas (A Cisterna → Última Transmissão) têm objetivos e progressão.
Inspirações (Last Day on Earth, State of Decay 2, This War of Mine, Project
Zomboid, 7 Days to Die, Frostpunk, Dead of Winter) entram só como princípios de
jogo, nunca como conteúdo copiado.

## 2. Princípio de progressão (aprovado pelo criador, 2026-10-30)

| Estágio | O que os jogadores fazem | Como o motor deve sentir |
|---|---|---|
| Início — sobrevivência emergencial | heróis exploram por comida, água, madeira, ferramentas, remédios | déficit diário real; cada dia conta |
| Meio — estruturação | hortas, água, cozinha, oficina; sobreviventes trabalham e produzem | produção cobre parte do consumo; escolhas de investimento |
| Avanço — comunidade preparada | o acampamento supre parte relevante das necessidades | heróis dedicam dias às missões e ameaças |

A dificuldade evolui: a campanha não pode ser só a repetição da mesma busca
desesperada por comida. Derrota legítima continua possível.

## 3. Status das mecânicas

Legenda: **I** implementada no motor; **A** aprovada, ainda não implementada;
**P** valor provisório (balanceamento); **F** ideia futura (não implementar
agora); **S** regra antiga substituída.

### 3.1 Implementadas (antes da Missão Mestre)

| Mecânica | Status | Onde |
|---|---|---|
| A Cisterna 0.2 completa (motor `cistern02`), seed 22 certificada (98 decisões) | I | `cistern02.py`, `replays/` |
| Migração para a Última Transmissão (proveniência, excedente, filtro, Horta §61) | I | `integrated_campaign.py` |
| Campanha regional: expedições táticas, Viagem, Emboscada, pistas, rádio | I | `system.py`, `tactics.py`, `arc2.py` |
| Consumo noturno 1 comida + 1 água por consumidor; ferimento na 2ª noite seguida; Colapso com ceil(humanos/4) em 3 noites | I | `system.py::_end_day` (RULES l.49, §25) |
| Horta EXP-BLD-01: 2 madeira + 1 sucata, 2 trabalhos; amadurece em **4 dias** e então produz **2 comida por amanhecer** (sem trabalhador; bônus de herói designado) | I | `data/system.json`, `_end_day` |
| Horta §61 da Cisterna no regional: 4 comida/dia com 1 trabalhador | I | `assign_continuity_garden` |
| Filtro da Cisterna no regional: C água por amanhecer | I (opcional) | `_continuity_filter_dawn` |
| Descarte voluntário de água (colheita) e prioridade de comida F | I | `MANUAL_EXPERIMENTAL.md` |
| Protótipos G (ração-ponte), C2 (coleta), D (Horta com Sementes) | I (desligados) | `enable_regional_prototypes` |
| Estruturas EXP-BLD-01..07 (Horta, Oficina, Enfermaria, Vigia, Depósito, Reservatório, Alojamento) | I | `data/system.json` |
| Especialistas EXP-NPC com trabalho fixo (produção automática no fim do dia) | I | `_end_day` |

### 3.2 Aprovadas pelo criador na Missão Mestre (2026-10-30)

Implementação no módulo `community.py` (regras "Comunidade"), ligada por
campanha. Status atualizado na matriz da seção 4.

1. Sistema híbrido de produção: trabalhadores e construções mantêm o acampamento
   mesmo com todos os heróis fora; sobreviventes resgatados trabalham sem
   supervisão; uma função por período; produção nunca ilimitada; heróis seguem
   com as expedições táticas e missões narrativas; mesmo relógio de dias.
2. Sobreviventes com bagagem aleatória ao serem resgatados e profissões que dão
   vantagem em atividades compatíveis (sem impedir outras).
3. Expedições automáticas de trabalhadores: o jogador escolhe trabalhador,
   atividade e duração; rendimento-base = **D6 × dias**, convertido em recursos
   por fatores provisórios; uma carta de acontecimento decide consequências; sem
   combate tático nem decisões diárias.
4. Consumo durante a viagem sem cobrança dupla.
5. Recursos naturais com fontes alternativas (floresta, rio, ruínas), sem
   destruir a identidade dos locais existentes.
6. **1 carne = 4 porções** de alimento (decisão do criador); frutas alimentam e
   hidratam em parte; coletor de chuva limitado por clima e capacidade.
7. Revisar o bloqueio de camas sem eliminar a importância da capacidade.

### 3.3 Valores provisórios (sujeitos a balanceamento)

Todos os números de `data/community.json` (fatores de conversão, reservas
naturais, capacidade de carga, baralho de acontecimentos, bagagem, coletor de
chuva, limite de lotação). Alterações ficam registradas em
`COMUNIDADE_BALANCEAMENTO.md` com amostra e motivo.

### 3.4 Ideias futuras (não implementar agora)

- Defumador e conservação longa de carne; qualidade de alimento.
- Carpintaria, sistemas avançados de água, fortificações, produção avançada.
- Novos mapas táticos (Floresta, Rio, Fazenda) — hoje floresta/rio/ruínas são
  zonas de trabalho automático, não mapas.
- Ataques ao acampamento com combate tático.
- Fibras, couro, pedras como recursos (sem uso de regra ainda).

### 3.5 Regras substituídas

| Regra antiga | Nova | Justificativa |
|---|---|---|
| Regional: migração recusada se moradores > camas | Com Comunidade: até +2 moradores em abrigo lotado (sem recuperação §25 de Vida enquanto lotado) | Mission: revisar bloqueio sem eliminar a capacidade; 47 recusas medidas em 1–90 (`HORTA_CONTINUITY.md`) |
| Só heróis trabalham obras EXP-BLD | Com Comunidade: trabalhadores adultos também | Produção híbrida aprovada |

As regras antigas continuam valendo quando a Comunidade está desligada
(replays certificados).

## 4. Matriz de rastreabilidade e percentual por subsistema

Critérios por subsistema (cada um vale 1/6): **D** regra documentada,
**I** implementação, **N** integração com campanha/motor, **T** teste
automatizado, **S** simulação relevante, **R** sem regressão conhecida
(`check.sh full` verde, seed 22 com 98 decisões). Percentual = critérios
cumpridos ÷ 6. Estado em 2026-10-30, commit `0c1bb06`.

| Subsistema | Regra | Código | Teste | D I N T S R | % |
|---|---|---|---|---|---|
| Cisterna 0.2 e seed 22 | RULES/CAMPAIGN | `cistern02.py` | `test_cistern02*`, replays | ✓✓✓✓✓✓ | 100 |
| Migração Cisterna → regional | MANUAL | `integrated_campaign.py` | `test_integrated*`, verificadores | ✓✓✓✓✓✓ | 100 |
| Exploração tática, combate, Viagem, pistas | MANUAL | `system.py`, `tactics.py`, `arc2.py` | `test_system`, `test_tactics*` | ✓✓✓✓✓✓ | 100 |
| Camas e abrigo lotado (+2, sem recuperação de Vida) | MANUAL §Comunidade | `community.crowded`, `World.validate` | `test_crowded_shelter…` | ✓✓✓✓✓✓ | 100 |
| Armazenamento: tanques de água separados | MANUAL §Comunidade | `World.free_space` | `test_water_tanks…` | ✓✓✓✓✓✓ | 100 |
| Trabalhadores sem heróis, 1 função/dia | MANUAL §Comunidade | `community.assign_job/day_work` | `test_workers_produce…`, `test_one_function…` | ✓✓✓✓✓✓ | 100 |
| Profissões (11) e bônus | MANUAL §Comunidade | `community.specialist` | `test_specialist_bonus…`, `test_garden_farmer…` | ✓✓✓✓·✓ | 83 |
| Viagens automáticas (D6 × dias, conversão, cartas, ração) | MANUAL §Comunidade | `community.send_trip/_resolve_trip` | 6 testes de viagem | ✓✓✓✓✓✓ | 100 |
| Caça, armadilhas, entorno finito | MANUAL §Comunidade | `community.dawn` | `test_traps…`, `test_yield…` | ✓✓✓✓✓✓ | 100 |
| Carne 4 porções, frutas, conservação curta | MANUAL §Comunidade | `community._cook/_deliver` | `test_meat…`, `test_fruit…`, `test_raw_meat…` | ✓✓✓✓✓✓ | 100 |
| Água: coleta, tratamento, coletor de chuva | MANUAL §Comunidade | `community._deliver/dawn` | `test_rain…`, `test_raw_water…` | ✓✓✓✓✓✓ | 100 |
| Madeira (floresta) e obras por trabalhadores | MANUAL §Comunidade | `community._build`, `start_build` | `test_workers_build…` | ✓✓✓✓✓✓ | 100 |
| Horta (EXP-BLD-01, §61, agricultor, dano/reparo) | este §3.1 + MANUAL | `system.py` | `test_garden_continuity`, `test_system` | ✓✓✓✓✓✓ | 100 |
| Bagagem dos resgatados | MANUAL §Comunidade | `community.join`, `tactics.py` | `test_rescued_survivor…` | ✓✓✓✓·✓ | 83 |
| Recursos iniciais dos heróis | MANUAL (leitura a confirmar) | `community.arrival_kits` | `test_hero_arrival_kits…` | ✓✓✓✓✓✓ | 100* |
| Vigia contra crise, cuidados | MANUAL §Comunidade | `guard_roll`, `after_meal` | `test_guard…` | ✓✓✓✓·✓ | 83 |
| Serraria e bancadas | sem regra escrita | — | — | ······ | 0 |
| Conservação longa (defumador) | ideia futura | — | — | ······ | 0 |

\* implementada como leitura do motor; precisa de confirmação do criador.

**Projeto (mecânicas listadas): (13 × 100 + 3 × 83,3 + 2 × 0) ÷ 18 = 86,1%.** Não é 100%: serraria,
bancadas e conservação longa não têm regra aprovada; profissões, bagagem e
vigia/cuidados ainda não têm simulação própria (S). Equilíbrio de
sobrevivência não entra no percentual: é meta de balanceamento (T1–T5,
`ECONOMY_TARGETS.md`) e **não está cumprida** (`COMUNIDADE_BALANCEAMENTO.md`).
