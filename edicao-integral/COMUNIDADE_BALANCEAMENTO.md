# Comunidade — balanceamento e simulações (2026-10-30)

Reprodução: `python edicao-integral/experiments/community_economy.py --seeds 1-30
--configs BASE,STRAT,COMM,...` (nada é gravado em `replays/`). Fluxo: Cisterna
com o controlador publicado e Horta H1 → migração → 15 dias regionais (cartas
de Viagem e filtro ligados). Sementes 1–30 ajuste; 31–90 confirmação (já
vistas); **91–120 reservadas, não usadas** (o script recusa).

Controlador `CommunityRegionalPlayer` (`community_player.py`): só estado
visível; cozinha a carne que vai estragar, obras se a noite está coberta,
viagens de comida quando há menos de 2 dias de estoque (1 dia se a noite não
está coberta), lenha para a próxima obra, armadilha com madeira sobrando,
cuidado se há ferido. Pista na Estação só com a noite coberta.

## Mudanças de valores provisórios (com motivo)

| Ciclo | Valor | Antes → depois | Motivo medido |
|---|---|---|---|
| 1 | reservas do entorno (caça/peixe/frutas) | 4/6/8, reposição lenta → 6/8/10, +1/+2/+2 por dia | piloto 1–6: viagens esgotavam o entorno em 2 dias; produção natural sustentável ficava abaixo de 5 comida/dia |
| 2 | custo por dia sem ração | 2 → 1 ponto | com 0 comida na chegada, viagens sem ração rendiam ~0 (espiral); 1 ponto = o viajante come parte do que acha |
| 2 | controlador | ração só do excedente → ração cheia | a ração é a refeição de quem viaja (não come no abrigo); dar menos só desperdiçava pontos |

Defeitos corrigidos durante os ciclos: Horta escolhia trabalhador em viagem;
migração validava camas antes de ligar a Comunidade; descarte de água para a
colheita não fazia sentido com tanques separados; lenha antes de comida com a
noite descoberta.

## Resultados — sementes 1–30 (53 vitórias na Cisterna, H2–H6)

Sobrevive = 15 dias regionais sem derrota parcial. Fome = porções faltando ÷
consumidor-noites, só nas sobreviventes. G e heróis em viagem **não são regra
aprovada** (variantes para decisão).

| Cenário | Migram | Sobrevivem | Dias médios | Fome | Rádio (todas / sobrev.) | Estruturas | Dias de Mercado | Viagens | Ganho das viagens | Ferimentos em viagem |
|---|---|---|---|---|---|---|---|---|---|---|
| BASE (controlador publicado) | 37 | 2 (5%) | 4,6 | 62% | 1 / 1 | 0 | 44% | — | — | — |
| STRAT (estratégico) | 37 | 2 (5%) | 4,1 | 62% | 1 / 0 | 0 | 29% | — | — | — |
| **COMM (regras aprovadas)** | **53** | **3 (6%)** | **6,3** | **36%** | 9 / 1 | 0,42 | 20% | 584 | 699 comida, 41 carne, 50 madeira, 63 água | 89 |
| COMM sem viagens | 53 | 3 | 4,9 | 54% | 0 / 0 | 0,28 | 26% | 0 | — | — |
| COMM sem obras | 53 | 3 | 6,1 | 38% | 8 / 0 | 0 | 21% | 509 | 559 comida, 70 carne | 85 |
| COMM + G (ração-ponte) | 53 | 8 (15%) | 8,0 | 31% | 33 / 5 | 1,04 | 18% | 637 | 739 comida, 61 carne, 157 madeira | 99 |
| COMM + heróis viajam | 53 | 5 (9%) | 6,3 | 29% | 12 / 3 | 0,53 | 20% | 1 099 | 838 comida, 63 carne | 156 |
| COMM + heróis viajam + G | 53 | 11 (21%) | 8,9 | 21% | 35 / 10 | 1,23 | 16% | 1 325 | 971 comida, 124 carne, 166 madeira | 208 |

Por tamanho (sobrevivem/migradas), COMM: H2 0/4, H3 0/10, H4 1/14, H5 1/14,
H6 1/11. COMM + heróis + G: H2 1/4, H3 1/10, H4 3/14, H5 3/14, H6 3/11.

Outras métricas COMM (1–30): estoque médio de comida 0,38 dia; de água 2,6
dias; 13 trabalhadores incapacitados em 53 campanhas; bloqueio
`no_mapped_food_source` (Mercado esgotado) em 50 campanhas.

## Confirmação — sementes 31–90 (138 vitórias na Cisterna)

| Cenário | Migram | Sobrevivem | Dias médios | Fome | Rádio (todas / sobrev.) | Estruturas | Viagens | Ferimentos em viagem |
|---|---|---|---|---|---|---|---|---|
| STRAT | 107 (31 recusas) | 0 | 3,6 | — | 4 / 0 | 0 | — | — |
| **COMM** | **138** | **7 (5%)** | **5,6** | **44%** | 36 / 2 | 0,28 | 1 485 | 212 |
| COMM + G | 138 | 10 (7%) | 7,2 | 34% | 81 / 7 | 0,75 | 1 463 | 246 |
| COMM + heróis viajam | 138 | 8 (6%) | 5,4 | 34% | 40 / 4 | 0,36 | 2 456 | 337 |
| COMM + heróis + G | 138 | 13 (9%) | 7,6 | 27% | 87 / 11 | 0,91 | 2 828 | 451 |

Mesma direção do ajuste, com taxas menores: as regras aprovadas tiram as
recusas e alongam a campanha, mas a sobrevivência continua longe de T1.
Amostras pequenas por tamanho (7–38): diferenças de 1–3 campanhas não são
conclusivas.

## Leitura

- **Corrigido:** as 16 migrações recusadas por cama passam a migrar; água não
  ocupa mais o depósito de comida; madeira tem fonte legal e renovável
  (floresta) e as obras saem (0 → 0,4–1,2 estrutura por campanha); o
  Mercado deixa de ser a única fonte (44% → 20% dos dias).
- As viagens funcionam como alavanca: sem elas a campanha dura 4,9 dias e a
  fome nas sobreviventes é 54%; com elas, 6,3 dias e 36%.
- **Não cumpre as metas** (`ECONOMY_TARGETS.md`): T1 (40–85% sobrevivem) e T3
  (fome ≤ 10%) falham em todos os cenários; T5 (rádio) só passa com G.
- Causa dominante, vista nos rastros: a comunidade chega com comida para
  menos de uma noite (estoque médio 0,38 dia) e 7–11 consumidores, dos quais
  só 2–4 trabalham; as primeiras viagens voltam no 1º–2º amanhecer e o
  Colapso vem na 3ª noite de falta. Os heróis ficam ociosos quando o Mercado
  acaba, porque não há outro local tático com comida.
- Riscos reais preservados: 89–208 ferimentos em viagem, carne que estraga,
  perdas de carga; nenhuma variante passa de 21%.

## Decisões para o criador

1. Heróis podem fazer viagens automáticas quando não saem na expedição
   tática? (+3 sobrevivências em 53; mais ferimentos.)
2. Ração-ponte G na chegada (1 comida por consumidor, uma vez)? (+5.)
3. Mapa tático de comida além do Mercado (Horta abandonada EXP-LOC-01,
   floresta) — conteúdo novo.
4. Penalidade do abrigo lotado: sem recuperação de Vida pelo descanso (atual)
   ou outra.
5. Serraria e bancadas: sem regra escrita; não implementadas.

## Ciclos 3–5 (diretor, autonomia delegada, 2026-10-30)

Defeito encontrado no harness: variantes em memória vazavam entre partidas
nos processos reutilizados do Pool; corrigido (restaura os valores a cada
partida). As comparações de rendimento feitas antes disso foram descartadas.

| Ciclo | Mudança (uma por vez) | 1–30 sobrevivem | Fome nas sobrev. |
|---|---|---|---|
| 3 | + suprimento de evacuação + heróis em viagem (COMM-V1) | 7/53 | 9% |
| 3 | controlador escolhe a atividade pelo rendimento visível esperado | (incluído acima) | — |
| 4 | pesca/coleta 1 ponto por unidade (era 2) | 23/53 | 28% |
| 4 | + peixe/frutas até 12, +3/dia | 30/53 | 25% |
| 5 | + Horta EXP-BLD-01 4/dia com Comunidade (era 2) | **34/53 (64%)** | 17% |
| — | capacidade 8 em vez de 6 (rejeitado) | 20/53 | 30% |
| — | Horta 3/dia (intermediário) | 31/53 | 19% |

## Resultado adotado — metas T1–T5 (`ECONOMY_TARGETS.md`)

| Cenário | Sementes | Sobrevivem | T1 40–85% | T2 ≥ 50% com falta | T3 fome ≤ 10% | T4 nenhum tamanho zerado | T5 rádio ≥ 30% |
|---|---|---|---|---|---|---|---|
| COMM (adotado) | 1–30 | 34/53 = 64% | ✓ | ✓ 30/34 | ✗ 16,6% (tardia 12,9%) | ✓ | ✓ 31/34 |
| COMM (adotado) | 31–90 | 88/138 = 64% | ✓ | ✓ 85/88 | ✗ 21,7% (tardia 18,8%) | ✓ | ✓ 81/88 |
| COMM sem heróis em viagem | 1–30 | 36/53 = 68% | ✓ | ✓ | ✗ 21,9% | ✓ | ✓ |
| COMM sem heróis em viagem | 31–90 | 76/138 = 55% | ✓ | ✓ | ✗ 26,3% | ✓ | ✓ |
| Controlador anterior (STRAT) | 31–90 | 0/107 (31 recusas) | ✗ | — | — | ✗ | ✗ |

Por tamanho (31–90, adotado): H2 4/7, H3 11/28, H4 20/35, H5 20/30, H6 33/38.
Grupos pequenos (H2–H3) ficam bem abaixo: menos braços para o mesmo número de
crianças e cães migrados. Tarefa aberta (D-05).

Outros números (31–90, adotado): 4 188 viagens, 560 ferimentos em viagem,
2,4 estruturas por campanha, Mercado em 11% dos dias, dias médios 12,4.

Leitura crítica:
- 4 de 5 metas cumpridas no ajuste e na confirmação; T3 falha: as
  sobreviventes ainda vivem com ~1 porção faltando a cada 5 consumidor-noites.
- Heróis em viagem: ganho pequeno no ajuste, claro na confirmação (+12 em
  138); mantido.
- Sementes 91–120 não usadas.

## Ciclo 6 — fome crônica (D-05), 1–30

| Variante (uma por vez sobre o adotado) | Sobrevivem | Fome | Fome tardia (noites 8–14) | Decisão |
|---|---|---|---|---|
| Adotado | 34/53 | 16,6% | 12,9% | — |
| Alvo de estoque 3 dias | 31/53 | 18,3% | 13,5% | rejeitado |
| Alvo de estoque 4 dias | 34/53 | 17,3% | 12,1% | rejeitado (sem ganho) |
| Trabalhar com 1 noite de fome (exceção à RULES l.22) | 34/53 | 15,5% | 11,7% | rejeitado: ganho mínimo, regra extra na mesa |
| Escolha de viagem por rendimento/dia (caça 2+ dias) | 32/53 | 18,8% | 15,6% | rejeitado: dobra a carne, não a sobrevivência |

Diagnóstico: a fome tardia não vem da estratégia nem da regra de fome; o teto é
a produção sustentável por trabalhador perto do consumo (peixe e frutas se
esgotam; caça e madeira sobram). Próximo passo D-14 (estrutura de produção do
meio de jogo).

## Ciclo 7 — Canteiro (D-14)

Estrutura nova do meio de jogo: 2 madeira + 1 sucata, 2 trabalhos, até 2 por
abrigo; 2 comida por dia com um trabalhador (agricultor +1). Transforma
trabalho em comida sem esgotar peixe e frutas. Construído em 31 de 53
campanhas (1–30); 2+ canteiros em várias.

| 1–30 | Sobrevivem | Fome | Fome tardia | Rádio (sobrev.) |
|---|---|---|---|---|
| Sem canteiro | 33/53 | 16,8% | 13,2% | 31 |
| **Com canteiro (adotado)** | **33/53** | **14,4%** | **10,4%** | 29 |

| 31–90 | Sobrevivem | Fome | Fome tardia | Rádio (sobrev.) |
|---|---|---|---|---|
| Sem canteiro | 89/138 | 21,8% | 18,9% | 82 |
| **Com canteiro (adotado)** | **92/138 (67%)** | **18,4%** | **14,4%** | 85 |

Metas com o canteiro: T1 ✓ (62% e 67%), T2 ✓, T4 ✓, T5 ✓; **T3 ainda ✗**
(fome tardia 10,4% no ajuste, 14,4% na confirmação). Grupos de 2–3 heróis
seguem abaixo (H2 2/7, H3 11/28 em 31–90).

## Ciclo 8 — cão na viagem (D-16)

Diagnóstico: grupos pequenos chegam com o mesmo ~1,5 cão e heróis feridos;
trabalhadores/consumidores 0,59 (H2) contra 0,75 (H6). Regra: o cão acompanha
uma viagem (+1 no D6, −1 ponto por noite), sai da refeição do abrigo.

| Cenário | Sobrevivem | Fome | Fome tardia | T2 | Rádio (sobrev.) | Por tamanho H2/H3/H4/H5/H6 |
|---|---|---|---|---|---|---|
| 1–30 sem cão | 33/53 | 14,4% | 10,4% | — | 29 | 3/4, 2/10, 9/14, 11/14, 8/11 |
| **1–30 com cão (adotado)** | **41/53 (77%)** | **8,1%** | 5,8% | — | 37 | 4/4, 5/10, 10/14, 14/14, 8/11 |
| **31–90 com cão (adotado)** | **100/138 (72%)** | **9,7%** | 7,0% | 89/100 | 95 | 2/7, 10/28, 27/35, 25/30, 36/38 |

**T1–T5 cumpridas nas duas faixas** pela primeira vez. Problema que fica:
escala por tamanho — H6 sobrevive 95% (fácil demais) e H2–H3 ~33–36% em 31–90.
Nova tarefa D-17 (dificuldade proporcional ao tamanho, sem recurso grátis).

## Ciclo 9 — escala por tamanho (D-17)

**Defeito encontrado.** Com todos os humanos fora em viagem, o limite de
colapso virava 0 (`(0+3)//4`) e o abrigo vazio "colapsava". Derrubava sobretudo
H2–H3. Correção como regra: uma viagem não pode deixar o abrigo sem humanos.
Sem o defeito, o jogo ficou fácil e desigual (1–90: H2 73%, H3 63%, H4 88%,
H5 93%, H6 98%).

**Diagnóstico.** Na chegada, Vida dos heróis 44% (H2–H3) contra 72% (H6):
herói com 1 de Vida não viaja. E o rodízio espalha a fome entre muitas pessoas:
H5–H6 passam mais fome (12%) e sobrevivem mais, porque ninguém chega à 3ª noite.

Variantes (1–90, 3 repetições do regional por fim de Cisterna; `--reps`):

| Variante | 1–30 | 31–90 | Fome sobrev. (31–90) | 31–90 H2/H3/H4/H5/H6 | Decisão |
|---|---|---|---|---|---|
| Sem defeito, sem regra nova | 89% | 77% | 10,3% | 71/65/80/81/80 | 1–30 acima de T1 |
| Ameaça noturna (1 dado/3–5 humanos, vigia anula) | — | 80–82% (1–90) | 10–11% | H6 88–93% | rejeitada |
| Limite de colapso mínimo 2 ou 1/6 | — | 86–88% (1–90) | 9% | sem efeito | rejeitada |
| Entorno +2/dia (R2) | 79% | 67% | 12,7% | 67/65/74/62/65 | fome acima de T3 |
| Baralho com mais ferimento/zumbis/perda | 84–87% | 71–77% | 11–11,5% | — | fome acima de T3 |
| Travessia (Vida máx. 2) | 83% | 78% | 11,1% | 57/61/83/83/87 | adotada |
| **Travessia + Moral (1 humano sem porção −1, todos +1)** | **75%** | **63%** | **7,2%** | 62/58/64/69/62 | **adotada** |
| Moral 1 a cada 4 humanos | 79% | 69% | 8,1% | 62/60/70/74/71 | mais fácil, menos simples |
| Moral sem recuperação | 62% | 51% | 5,1% | 62/46/57/50/46 | duro demais |
| Moral sem travessia | 79% | 69% | 6,0% | 62/57/66/79/75 | tamanhos se afastam |

Medição oficial (1 repetição, como nos ciclos anteriores):

| Cenário | Sobrevivem | Fome | Fome tardia | T2 | Rádio (sobrev.) | H2/H3/H4/H5/H6 |
|---|---|---|---|---|---|---|
| **1–30 adotado** | **39/53 (74%)** | **6,5%** | 3,6% | 30/39 | 37 | 4/4, 7/10, 9/14, 10/14, 9/11 |
| **31–90 adotado** | **91/138 (66%)** | **7,8%** | 2,1% | 79/91 | 89 | 4/7, 16/28, 23/35, 23/30, 25/38 |

T1–T5 cumpridas nas duas faixas; todos os tamanhos entre 40% e 85% (H2 em
1–30 é 4/4 com só 4 fins de Cisterna; nas repetições, 92–100%). Amostra pequena
de H2: 11 vitórias de Cisterna em 1–90.

Personas (18, sementes 1–30, 212 mesas): A 12/53 (23%), B 36/53, C 39/53,
mista 30/53. O controlador das personas não construía canteiro (corrigido).
O grupo A quase não constrói (0,4 estrutura/mesa) nem guarda comida → D-18.

Lacunas fora da Comunidade vistas com mais ferimentos (1 caso em 1.240 cada):
cartão de acesso no chão sem regra de recuperação; trabalhador indisponível no
controlador tático → D-19.

## Ciclo 10 — crescimento do abrigo (D-20)

Auditoria (1–90, regras D-17): a população não mudava em 15 dias; depósito
com pico de 14–20 de 30 (perda de comida ~0,3 por campanha); terreno com 2–4
livres no fim; só camas apertavam (H4–H6, 3–5 noites lotadas). Sem gente nova,
alojamento, terreno e depósito não tinham motivo.

Sistema adotado: chegadas de sobreviventes (D6), terreno para obras da
Comunidade, cerca (+3 de terreno), níveis 2 de Depósito e Alojamento
(`MANUAL_EXPERIMENTAL.md`).

| Variante (31–90) | Sobrevivem | Fome | H2/H3/H4/H5/H6 | Acolhidos / recusas por campanha |
|---|---|---|---|---|
| Sem crescimento (D-17) | 66% | 7,8% | 57/57/66/77/66 | — |
| 4 chegadas (3, 6, 9, 12), acolhe até lotar | 49% | 6,5% | 57/57/63/53/26 | 2,8 / 0,9 |
| 4 chegadas, acolhe só com cama | 58% (2 rep.) | 6,7% | 57/54/61/68/51 | 1,4 / 1,6 |
| **2 chegadas (4, 10), acolhe só com cama (adotado)** | **64%** | **8,7%** | 57/64/63/73/58 | 1,1 / 0,7 |
| 2 chegadas, sempre recusa | 61% | 7,5% | 71/57/63/67/55 | 0 / 1,3 |
| 2 chegadas, acolhe até lotar | 62% | 8,7% | 57/64/66/67/53 | 1,7 / 0,3 |

Oficial (1 repetição): **1–30 35/53 (66%)**, fome 5,8%, T2 28/35, rádio 34;
**31–90 88/138 (64%)**, fome 8,7%, T2 75/88, rádio 84. T1–T5 cumpridas; todos
os tamanhos entre 55% e 90%. Obras por campanha (31–90): cerca 46, alojamento
35, Depósito nível 2 2, Alojamento nível 2 0 em 138 — o 2º nível quase não é
necessário em 15 dias (fica como opção de mesa; o depósito raramente enche).

Personas (1–30, 212 mesas): A 11/53, B 35/53, C 34/53, mista 29/53.

## Ciclo 11 — Horta abandonada (D-15) e preparação Acolhedor (D-18)

D-15: depois do Mercado não havia comida tática (bloqueio
`no_mapped_food_source` em 104–169 campanhas); heróis descansavam 65% dos dias.
EXP-LOC-01 ganhou mapa (`garden_edge_01`). Controlador vai lá quando a noite
não está coberta.

| Variante (1 rep. salvo indicado) | 1–30 | T2 1–30 | 31–90 | T2 31–90 | Fome 31–90 | Descanso |
|---|---|---|---|---|---|---|
| Sem Horta abandonada | 66% | 28/35 | 64% | 75/88 | 8,7% | 65% |
| Renova toda noite, vai com < 2 dias de estoque | 74% | 16/39 | 59% | 43/82 | 2,8% | 37% |
| Renova toda noite, vai com noite descoberta (2 rep.) | 72% | 35/76 | 62% | 92/170 | 3,5% | — |
| Rende 1 comida por busca (2 rep.) | 67% | 49/71 | 48% | 89/131 | 5,6% | — |
| **Renova a cada 2 noites (adotado)** | **72%** | **22/38** | **69%** | **64/95** | **5,0%** | **44%** |
| Renova a cada 3 noites (2 rep.) | 75% | 51/79 | 65% | 130/179 | 5,0% | 49% |

Adotado por tamanho: 1–30 4/4, 8/10, 9/14, 9/14, 8/11; 31–90 5/7, 17/28,
23/35, 24/30, 26/38. T1–T5 cumpridas.

D-18: o grupo A (casual) não planeja obras. Canteiro pronto na chegada como
regra padrão tirava a pressão das mesas que planejam (T2 15/45 e 35/94), então
virou preparação opcional **Acolhedor** (canteiro + 2 rações por consumidor).

| Personas 1–30 (53 mesas cada) | A | B | C | mista |
|---|---|---|---|---|
| D-17 (antes) | 12 | 36 | 39 | 30 |
| Normal com Horta abandonada | 16 | 35 | 39 | 29 |
| Acolhedor só com canteiro | 19 | 35 | 41 | 37 |
| **Acolhedor (canteiro + 2 rações)** | **31** | **36** | **39** | **33** |

Controlador no Acolhedor: 1–30 72%, 31–90 62%, fome 1,3–1,7% (modo fácil:
pressão baixa por desenho). Personas no Normal: descanso 46% dos dias,
Mercado/Horta 33%, pistas 15%.

## Ciclo 12 — fim de campanha jogado pelo controlador (D-22)

O controlador da edição integral percorre: rádio → cartão → bateria
(Oficina) → Posto (inspecionar, consertar, combustível, voltar de van) →
combustível → Instalação militar de van (transmissor) → defesa final.

| Passo do ajuste | 15 dias: venceu / perdeu defesa | 25 dias: venceu / perdeu | Trava |
|---|---|---|---|
| Primeira versão | 1 / 2 | — | 7 erros "defesa indisponível" |
| Defesa uma vez só | 8 / 22 | — | 30 |
| Visitas curtas ao Posto, equipe descansada | 3 / 5 | — | 25 |
| Combustível largado volta ao Posto | 3 / 5 | 7 / 21 | 9 (15 d) |
| Tanque do caminhão 6 | 6 / 25 | 20 / 65 | 1 |
| Defesa abre rodada nova | 7 / 22 | 22 / 59 | — |
| **Manutenção de arma (1 sucata)** | **12 / 17** | **38 / 42** | — |

Defesa isolada (300 partidas por tamanho, armas inteiras): ondas fixas davam
5–13% (H2) a 100% (H6); com ondas por defensores, Vida 2: H2 63%, H3 60%,
H4 80%, H5 75%, H6 73%.

Vitória na campanha (defesa vencida), 25 dias: 1–30 15/53 (28%), 31–90 23/138
(17%); por tamanho em 31–90: 0/7, 4/28, 10/35, 5/30, 4/38. Sobrevivência a 15
dias inalterada (1–30 70%, 31–90 65%). A campanha precisa de ~20 dias para
fechar: prazo e equilíbrio da vitória → D-23.

## Ciclo 13 — acampamento em lotes (D-24..D-26), 1–30 × 2 repetições

Modelo novo (`camp.py`): grade 2×2 → 3×3 → 4×4, barracas em lotes, horta por
lotes, estoque por categoria, Crise 0–10, ração de obra. 106 campanhas por
linha (sementes 1–30, 2 repetições do regional); 15 dias.

| Passo | Sobrevivem | Fome nas sobreviventes | Observação |
|---|---|---|---|
| Modelo abstrato anterior (referência) | 73/106 (69%) | 3,8% | terreno 7, canteiro, Moral |
| 1ª versão (núcleo ocupa lote, expansão 4 madeira + 2 metal, Crise +1/+2/+1) | 20/53 (38%) | 10,3% | 46/53 sem expandir |
| Expansão 3 madeira; Crise sem agravamento | 28/53 (53%) | 14% | grupos de 12 enchem a clareira de barracas |
| Fogueira e estoque fora dos lotes; 1 porção/lote | 21/53 (40%) | 11% | horta rende menos que pescar |
| Horta 2 porções por lote cuidado e regado | 30/53 (57%) | 5% | H6 1/11 |
| Mutirão na expansão (até 3 pessoas) | 30/53 (57%) | 7,5% | — |
| Viagens de água (rejeitado) | 20/53 (38%) | 8% | ferver gasta a madeira das obras |
| Chuva no D6 do amanhecer (4–6): horta sem água | 53/106 (50%) | 10,6% | base das ablações |
| Ablação: estoque 30 em vez de 24 | 52/106 (49%) | 9,5% | estoque não é o gargalo |
| Ablação: sem ração de obra | 67/106 (63%) | 7,7% | ração custa ~13 pontos; mantida (pedido do proprietário) |
| Ablação: Crise +1 em qualquer déficit | 73/106 (69%) | 13,2% | tolera fome demais |
| Crise com agravamento em noites seguidas | 52/106 (49%) | 9,4% | rejeitado |
| Horta só com trabalho (sem madeira) | 48/106 (45%) | 8,8% | madeira fica para cerca e cozinha |
| **Crise +1 até metade dos humanos sem porção, +2 acima** | **63/106 (59%)** | **10,9%** | H2 5/8, H3 14/20, H4 16/28, H5 19/28, H6 9/22 |

Adotado: a última linha. Tudo dentro de T1 (40–85%) por tamanho; T3 (≤10%)
no limite. Grupos grandes ficaram mais difíceis que os pequenos (o contrário
do D-17): mais bocas na mesma clareira. Confirmação em 31–90 e situações A–H
no ciclo 14.

### Ciclo 13b — controlador e colapso (1–30 × 2)

| Passo | Sobrevivem | Fome nas sobreviventes |
|---|---|---|
| Situações (1ª rodada): base com viagem de água abaixo de 2 noites | 52/106 (49%) | 13,6% |
| Viagem de água só abaixo de 1 noite de água | 69/106 (65%) | 12,8% |
| Sem viagem de água | 64/106 (60%) | 12,1% |
| Horta só com 2+ lotes por pessoa | 66/106 (62%) | 14,4% |
| **Crise como único colapso (sem §25 de 3 noites)** | **68/106 (64%)** | **14,7%** |
| Acolhedor antigo (1 lote plantado) | 56/106 (53%) | 12,2% |
| **Acolhedor em lotes (3×3 + 2 lotes plantados)** | **93/106 (88%)** | **3,5%** |

Por tamanho (base): H2 7/8, H3 15/20, H4 19/28, H5 15/28, H6 12/22 — todos
≥ 54% (T1). T3 (fome ≤ 10% nas sobreviventes) **não** está atendida: 14,7%.
A fome passa a ser o custo de sobreviver nos primeiros dias, antes da horta; a
Crise segura o colapso. Pendência registrada para o ajuste fino (D-28).

## Ciclo 14 — situações A–H, tamanhos e D-23 (acampamento em lotes)

Situações dirigidas (1–30 × 2, 15 dias, 106 campanhas cada; E e H em testes
determinísticos de `tests/test_camp.py`):

| Situação | Sobrevivem | Fome | Leitura |
|---|---|---|---|
| Base | 68/106 (64%) | 14,7% | referência desta rodada |
| A — barracas antes de produzir | 50/106 (47%) | 15,9% | expandir sem comida custa caro; ainda há recuperação |
| B — família de 3 com barraca acolhida no dia 3 | 64/106 (60%) | 13,2% | mais bocas, mais braços |
| B — mesma família recusada | 71/106 (67%) | 15,3% | recusar (Crise +1) não domina: dilema real |
| C — meta de 10 lotes de horta | 68/106 (64%) | 14,7% | igual à base: o gargalo é lote livre e braço |
| D — ninguém com profissão | 67/106 (63%) | 15,5% | nenhuma profissão é indispensável |
| E — heróis 3 dias fora | teste | — | horta, refeição e retorno sem eles |
| F — chegada sem comida | 57/106 (54%) | 20,8% | Crise alta, mas há saída |
| G — acampamento desenvolvido (4×4, 6 hortas, água, Depósito, Oficina, Vigia) | 102/106 (96%) | 1,9% | autossuficiente |
| G — o mesmo sem Mercado nem Horta abandonada | 102/106 (96%) | 2,4% | não precisa de exploração repetitiva |
| H — dependências | teste | — | toda obra tem caminho legal a partir da clareira |

Correções do controlador nesta rodada: herói escalado duas vezes no mutirão
(erro do motor), rega só com água acima da bebida, viagem de água só abaixo
de 1 noite, horta só com 2+ lotes por pessoa.

Tamanho: com a clareira 2×2 para todos, 31–90 dava 75/138 (54%), H5 14/30,
H6 12/38. Grupo com 9+ humanos chegando no 3×3: 97/138 (70%), H6 27/38
(limite 10: 93/138). Adotado 9.

Resultado (antes do ajuste final do controlador, 15 dias): 1–30×2 86/106
(81%), fome 9,6%; 31–90 98/138 (71%), fome 12,0%; por tamanho em 31–90:
6/7, 22/28, 24/35, 19/30, 27/38. Acolhedor: 94% e 82%, fome ~4%.

D-23 (25 dias, 1–30×2): vitórias 36/106 sem apoio; **39/106 (37%)** com
Vigia e guardas atirando (2/8, 6/20, 12/28, 12/28, 7/22). Prazo do dia 25
adotado. Meta pré-registrada (≥ 30%, nenhum tamanho < 15%) atingida em 1–30;
31–90 fica para a validação cega (D-12).

**Final do ciclo 14 (controlador definitivo, 15 dias):** 1–30×2 83/106
(78%), fome 10,4%; 31–90 100/138 (72%), fome 12,9%; por tamanho em 31–90:
7/7, 22/28, 26/35, 18/30, 27/38. Acolhedor: 92% e 81%, fome 3,7–5,6%.
Personas 1–30 (Normal): A 30, B 37, C 42, mista 41 de 53; Acolhedor: A 47,
B 47, C 50, mista 46. 0 erros do motor.
