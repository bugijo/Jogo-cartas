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
