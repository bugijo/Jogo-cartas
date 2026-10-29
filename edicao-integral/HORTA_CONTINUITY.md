# Horta entre a Cisterna e a campanha regional (2026-10-29)

## Resultado real da H1 (escolhida pelo responsável; commit `7f19a5e`)

Medição H2–H6, sementes 1–30 (sementes de ajuste), `auto_settings`.

Variantes do controlador da Cisterna (só ações legais; nada criado):

| Variante | Vitórias | Acolheram | Horta pronta | Vitória + Horta ativa |
|---|---|---|---|---|
| Base (sem Horta) | 52 | 0 | 0 | 0 |
| Ingênua (troca dias de comida, repete idas) | 19 | 41 | 5 | 3 |
| **A: só dia livre, 1 ida (padrão do modo)** | **53** | 31 | 4 | **4** |
| B: dia livre ou de comida, 1 ida | 29 | 41 | 3 | 2 |
| C: A + só se já suprido até a noite 5 | 53 | 31 | 4 | 4 |
| D: dia de comida, até 2 idas | 19 | 41 | 5 | 3 |
| E: A sem buscar Material | 48 | 36 | 0 | 0 |

A perde 3 vitórias da base (H2 s30, H3 s20, H6 s16) e ganha 4 (H4 s8 e s26,
H5 s13 e s26). Hortas com vitória: H4 s20, H5 s10, H5 s16, H6 s10. As derrotas da
ingênua vinham de emergências no Condomínio (96) que deixavam o filtro sem
trabalhadores aptos.

Campanha regional (`replays/regional_campaign_garden_sweep.json`, 15 dias):

| | Base | H1 |
|---|---|---|
| Vitórias da Cisterna | 52 | 53 |
| Migração recusada | 0 | 16 |
| Migram com Horta | — | 2 |
| Sobrevivem 15 dias | 0 | 0 |
| Comida colhida no regional (total) | — | 1 |

Protótipo anterior (Horta pronta + filtro, sem os bloqueios abaixo): 31/53. A
diferença vem de dois bloqueios reais, **pendentes de decisão**:

1. **Camas regionais.** Acolher o grupo (3 humanos) faz o censo exceder as camas
   do abrigo regional: "Capacidade excedida" em 16 migrações (2 das 4 Hortas).
2. **Depósito cheio de água.** O depósito regional (30) chega com 27–28 água
   (migração + filtro a cada amanhecer); a colheita antes da refeição não cabe
   (0 ou 1 de 4). Opções: colher depois da refeição; permitir descarte
   voluntário de água; aumentar o depósito por estrutura migrada.

Sem uma dessas decisões a H1 não muda o resultado regional.

## Investigação anterior

## Fatos levantados

| Pergunta | Resposta | Fonte |
|---|---|---|
| Sementes existem? | Sim: 2 cartas `ZC-REC-0155/0156` (carga 1, "nunca monte/estoque"). | `content/catalog.json` |
| Onde se obtêm? | Só ao **acolher** Samuel, Bruna e criança (`ZC-MOR-0006`) no Condomínio O2: "ganhe Sementes se houver carga". | `CAMPAIGN.md` l.24, carta `ZC-MOR-0006` |
| O motor da Cisterna dá Sementes? | Não. `Cistern02.rescue`/`Tactical02.rescue` acolhem o grupo, mas não entregam Sementes. O controlador não visita o Condomínio. | `cistern02.py`, `cistern_tactics02.py` |
| Horta na 0.2 | `ZC-PRO-0007`: 2 Materiais + Sementes + 2 trabalhos, 1 terreno; um trabalhador produz 4 comida/dia a partir do amanhecer seguinte. | RULES §61 |
| O motor da Cisterna constrói projetos? | Não: só as etapas do filtro. Não há reserva de Materiais/terreno/trabalho para Horta. | `cistern02.py` |
| Materiais sobrando nas vitórias | 0 ou 1 em todas as 52 vitórias (H2–H6, sementes 1–30): o filtro consome os 3 iniciais. | medição local |
| Materiais vão para o regional? | Não: a migração arquiva Material como não gastável (`materials_archived`); o regional não tem recurso Material. | `integrated_campaign.py` |
| Regras sobre levar recursos entre capítulos | Nenhuma explícita; CAMPAIGN só fala da Continuação (filtro/terrenos persistem) e da Evacuação (cargas). | `CAMPAIGN.md` l.32–33 |
| Horta regional existente | `EXP-BLD-01` experimental: 2 madeira + 1 sucata, colheita de 2 comida a cada 4 dias; madeira sem fonte. Não é a §61. | `data/system.json` |

## Alternativas

| | Como | Custo de implementação | Consequências | Compatibilidade |
|---|---|---|---|---|
| **H1 — construir na Cisterna e migrar** | Sementes ao acolher `ZC-MOR-0006`; projeto Horta na 0.2 (2 Materiais + Sementes, 2 trabalhos, terreno, limite de 2 trabalhos/dia com o filtro); migra como o filtro (`continuity_garden`, 4 comida com trabalhador). | Alto: Sementes no resgate, sistema de projetos na Cisterna, controlador visitando o Condomínio e buscando Material, migração e testes. | Compete com o filtro por Material (vitórias terminam com 0–1); pode reduzir vitórias da Cisterna. Replays certificados intactos se for opcional. | Total com RULES §61 e CAMPAIGN. |
| **H2 — construir no regional** | Levar Sementes (se acolhidas) como carga única e definir equivalência de Material no regional. | Médio, mas exige duas decisões: Material regional (sucata? desarquivar?) e fonte regional de Sementes (o mapa do Condomínio é só referência). | Sem Sementes da Cisterna não há Horta; equivalência de Material muda a economia regional. | Parcial: depende de regras novas. |
| **H3 — usar a Horta regional experimental** | `EXP-BLD-01` com madeira + sucata. | Baixo no motor, mas madeira não tem fonte. | 2 comida a cada 4 dias: não sustenta (protótipos mostram necessidade de ~4/dia). | Não é a §61. |
| **H4 — sem Horta** | Só Mercado + filtro (estado atual). | Nenhum. | Medição real: 0/52 sobrevivem; colapso em 3–5 dias. | — |

Teto medido em protótipo (não é resultado real): Horta §61 pronta + filtro → 31/53
campanhas sobrevivem 15 dias.

## Alterações mínimas para H1
1. `Tactical02.rescue(..., 'welcome')` do grupo `ZC-MOR-0006` entrega 1 Sementes na carga se houver espaço (texto da carta).
2. `Cistern02`: projeto Horta com reserva de 2 Materiais + Sementes, 1 terreno, 2 trabalhos (dentro do limite de 2/dia), produção 4 comida/amanhecer com um trabalhador alocado.
3. Controlador adaptativo: incluir o Condomínio quando sobrar dia e Material (opcional, medido em 1–30 e validado em 91–120).
4. Migração: `continuity_garden` (ativa, trabalhador exigido), produção diária no regional pelo depósito, opcional como o filtro.

Decisão do responsável (2026-10-29): H1. Resultado no topo deste arquivo.
