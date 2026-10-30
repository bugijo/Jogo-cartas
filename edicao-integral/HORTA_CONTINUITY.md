# Horta entre a Cisterna e a campanha regional (2026-10-29)

## Descarte voluntário de água (aprovado; medição real)

Regra no `MANUAL_EXPERIMENTAL.md`. Medição H2–H6, 15 dias regionais, modo Horta.
Sementes 1–30 são de ajuste; 31–90 já vistas, usadas só como validação (nada
ajustado). 91–120 não usadas.

| Sementes 1–30 | Sem descarte | Com descarte |
|---|---|---|
| Vitórias da Cisterna | 53 | 53 |
| Migração recusada (camas) | 16 | 16 |
| Migram com Horta | 2 | 2 |
| Sobrevivem 15 dias | 0 | 2 (H5 s10, H6 s10) |
| Comida colhida (H5 / H6) | 1 / 0 | 56 / 56 |
| Água descartada (H5 / H6) | — | 4 / 4 (só no 1º dia) |

| Sementes 31–90 | Base | Horta sem descarte | Horta com descarte |
|---|---|---|---|
| Vitórias da Cisterna | 143 | 138 | 138 |
| Migração recusada (camas) | 0 | 31 | 31 |
| Migram com Horta | — | 1 (H3 s70) | 1 |
| Sobrevivem 15 dias | 0 | 0 | 0 (H3 s70 cai no dia 7, 20 comida colhidas, descarte 0) |

**Não está fácil demais no agregado** (2 de 191 vitórias sobrevivem, todas com
Horta), mas as 2 sobrevivências são **fome em rodízio**: 10–11 consumidores,
6–7 porções faltando **toda** noite, ninguém com 2 noites seguidas sem comer, logo
sem ferimento nem Colapso (RULES l.49). Rádio só em H5 s10; cartão em nenhuma.
O descarte só destrava o 1º dia; o que sustenta é a Horta + rodízio. Avaliar se a
regra de privação deve pesar nesse padrão — pendente, não alterado.

## Bloqueio de camas (investigação, nada alterado)

- Na Cisterna, acolher aceita até capacidade + 2 humanos como recepção
  temporária (`Cistern02.rescue`; RULES l.81: da 3ª noite, −1 Moral e −1 Saúde
  por noite sem vaga). O controlador vence com 1–2 humanos acima das vagas.
- No regional, `World.validate` exige residentes ≤ camas (camas = vagas da
  Cisterna) e a migração é recusada: 47 recusas em 1–90 (excedente 1 em 34,
  2 em 13). Hortas ativas perdidas: H4 s20, H5 s16, H4 s85, H6 s32, H6 s85.
- O regional não tem Barraca construível; não há como abrir vaga depois.

Opções para decisão:
1. **Migrar a recepção temporária**: excedente entra sem cama, com a penalidade
   da RULES l.81 por noite até haver vaga (no regional, para sempre).
2. **Ponte de acolhimento** (CAMPAIGN l.32: 2 vagas por fundador até construir):
   texto é da Evacuação; usar na migração seria nova leitura.
3. **Controlador só acolhe com vaga definitiva** (ou constrói Barraca antes):
   sem regra nova, mas perde as Sementes nessas sementes.
4. **Barraca regional** (Materiais + Lona): exige trazer Materiais ao regional,
   hoje arquivados.

Protótipo fora do repo (descarte ligado; nada commitado no motor):

| Opção | Sementes | Vitórias | Recusas | Migram com Horta | Sobrevivem 15 dias |
|---|---|---|---|---|---|
| Atual | 1–30 / 31–90 | 53 / 138 | 16 / 31 | 2 / 1 | 2 / 0 |
| 1: recepção migra, −1 Moral −1 Saúde por noite | 1–30 / 31–90 | 53 / 138 | 0 / 0 | 4 / 4 | 2 / 0 |
| 3: controlador só acolhe com vaga | 1–30 / 31–90 | 49 / 141 | 0 / 0 | 0 / 1 | 0 / 0 |

Na opção 1 as Hortas que antes eram recusadas (H4 s20, H5 s16, H4 s85, H6 s32,
H6 s85) migram, mas caem em 4–5 dias. Na opção 3 não sobram vagas para o grupo
das Sementes nas sementes 1–30. Nenhuma das duas muda a sobrevivência.

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
