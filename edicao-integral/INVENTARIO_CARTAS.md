# Inventário de componentes — edição integral (D-07, 2026-10-30)

Gerado e conferido por `tools/card_inventory.py` (dados em
`data/print_inventory.json`; `check.sh full` falha se divergir). Nada aqui foi
contado à mão.

## Decisões do diretor

| Decisão | Motivo |
|---|---|
| A Cisterna 0.2 (324 cartas, 6 mapas, 12 heróis iniciais, 198 fichas) entra **sem mudança** | certificada (seed 22); é o primeiro arco jogável |
| Recursos no regional ficam em **trilhas no tabuleiro do abrigo**, não em cartas | estoque chega a 30 + 30; cartas de recurso viram trabalho de contagem |
| Carne da Comunidade usa as **8 cartas REC "Carne" do 0.2** (trilha de 6) | componente já existe; nenhuma carta nova |
| Acontecimentos de viagem: **1 baralho compartilhado de 12** para todas as atividades | menos baralhos; o risco por atividade vem do número de cartas tiradas (caça/sucata +1, 3 dias +1) |
| Profissões: **baralho de 12** (11 profissões, "comum" ×2) | um sorteio por adulto migrado ou resgatado |
| Bagagem: **tabela D6 numa carta de referência**, não baralho | 6 resultados cabem numa carta |
| Serraria, bancada, defumador: **sem carta** | eliminados ou futuros (`MANUAL_EXPERIMENTAL.md`) |

## Cartas

| Baralho | Cartas | Origem | Repetidas / raras | Campanha | Estado |
|---|---|---|---|---|---|
| Cisterna 0.2 (16 famílias) | 324 | `content/catalog.json` | REC 156, SAQ 36, EQU 18… | A Cisterna | pronto (kit 0.2) |
| Acontecimentos de viagem | 12 | `data/community.json#event_deck` | tranquila ×3; demais ×1 (pista = rara: vale uma vez) | Última Transmissão | regra e motor prontos; **arte/impressão pendente** |
| Profissões | 12 | `#profession_deck` | comum ×2 | Última Transmissão | idem |
| Estruturas regionais | 13 | EXP-BLD-01..07 + coletor + cozinha + canteiro + cerca + Depósito 2 + Alojamento 2 | 1 de cada (canteiro e cerca: carta única, até 2 marcadores) | Última Transmissão | idem |
| Locais regionais | 7 | EXP-LOC-01..07 | 1 de cada | Última Transmissão | idem |
| Crises do abrigo | 5 | EXP-CRI-01..05 | 1 de cada | Última Transmissão | idem |
| Última Transmissão (missão/defesa) | 5 | `data/last_transmission.json` | 1 de cada | Última Transmissão | mapa militar **pendente** (regra de combustível) |
| Referência da Comunidade | 5 | bagagem D6, viagem, comida e água, clima, chegadas D6 | — | Última Transmissão | idem |
| **Novas para imprimir** | **59** | | | | |

Total da edição integral: 324 (0.2) + 59 novas = **383 cartas**.

## Tabuleiros e mapas

| Peça | Estado |
|---|---|
| 6 mapas da Cisterna 0.2 | prontos (kit 0.2) |
| Mapas táticos do motor: market_intro, hospital_02, workshop_02, gas_station_02, condominium_02, station_02, camp_final | jogáveis no motor; impressão da edição integral pendente (D-08) |
| military_installation | **pendente**: depende da regra de combustível (`TACTICAL_FUEL_AUDIT.md`) |
| garden_edge_01 (Horta abandonada, EXP-LOC-01) | **novo**: jogável no motor (D-15); arte e impressão pendentes (D-08) |
| Tabuleiro do abrigo regional (trilhas de estoque, Moral, camas/lotação, terreno, obras, carne, dia/relógio com chegadas nos dias 4 e 10) | **novo, a desenhar** (D-08) |
| Tabuleiro do entorno (caça, peixe, madeira, frutas, sucata; não tático) | **novo, a desenhar** (D-08) |

## Heróis e fichas

12 heróis iniciais da Cisterna (24 no catálogo 0.2); o motor regional modela 10,
mais 2 perfis-ponte (Téo, Célia) com atributos do 0.2. Fichas regionais: D-09.

## Fichas novas

6 marcadores de viajante (dias restantes), 2 de armadilha, 3 de obra
comunitária. As demais fichas (fome, sede, dano, portas, buscas, inimigos) vêm
do 0.2.

## Faltando para o kit (fila do diretor)

D-08 tabuleiros do abrigo e do entorno; D-09 fichas regionais; D-10 manual
da edição integral; D-11 impressão A4 das 59 cartas novas, tabuleiros e
fichas, com QA de frente/verso.
