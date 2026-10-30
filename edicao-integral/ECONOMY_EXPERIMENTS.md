# Experimentos da economia de comida regional (Fase 6, 2026-10-29)

Script reproduzível: `edicao-integral/experiments/food_economy.py` (variantes só
na memória; motor, regras e artefatos intactos). Alvos T1–T5 registrados antes em
`ECONOMY_TARGETS.md` (commit `b01d7e7`). Regra de fome atual mantida. Modo Horta
e descarte de água ligados; 15 dias; H2–H6. Metas na ordem T1..T5 (✓ cumpre).

## Ciclo 1–2: recompensa de comida × produção da Horta

Comida por busca arredondada para cima de metade: 2 → 3 (×1,25 e ×1,5 dão o
mesmo valor), 2 → 4 (×2).

| Comida | Horta | 1–30 sobrevivem | Fome nas sobreviventes | 31–90 sobrevivem | Metas 1–30 |
|---|---|---|---|---|---|
| ×1 | 4 | 2/37 | 62% | 0/107 | ·✓··✓ |
| ×1 | 8 | 2/37 | 21% | 0/107 | ·✓··✓ |
| ×1,5 | 6 | 1/37 | 35% | 0/107 | ·✓··✓ |
| ×2 | 4 | 1/37 | 64% | 0/107 | ·✓··· |
| ×2 | 8 | 2/37 | 18% | 1/107 | ·✓··✓ |

(As 12 combinações estão no log do experimento; nenhuma passa de 2/37 ou 1/107.)

Leitura: a comida regional total é só o Mercado, 4 buscas × 2 = 8 por campanha,
sem reposição; dobrar dá +8, cerca de 1 dia para 8 consumidores. A Horta só chega
ao regional em 1–2 campanhas (Sementes do acolhimento + bloqueio de camas), então
produzir 6 ou 8 não muda o total. **Sem melhora significativa.**

## Ciclo 3: Mercado repõe 1 busca por noite (protótipo, regra nova)

| Comida | 1–30 | Dias médios | 31–90 | Fome nas sobreviventes | Rádio | Metas 1–30 / 31–90 |
|---|---|---|---|---|---|---|
| ×1 | 14/37 | 9,1 | 31/107 | 54–56% | 0 | ·✓·✓· / ·✓··· |
| ×1,5 | 25/37 (68%) | 11,8 | 76/107 (71%) | 48–53% | 0 | ✓✓·✓· / ✓✓·✓· |
| ×2 | 33/37 (89%) | 13,7 | 100/107 (93%) | 44–48% | 0 | ·✓·✓· / ·✓·✓· |

Reposição é a alavanca que muda a sobrevivência, mas **nenhuma variante passa
T3 nem T5**: as sobreviventes ainda faltam ~50% das porções (rodízio) e o
controlador vai ao Mercado todo dia, sem avançar o rádio.

## Revisão de abordagem (3 ciclos sem cumprir as metas)

- Oferta diária (3–4 comida) continua abaixo do consumo (5–11). Com a regra de
  fome atual, qualquer oferta acima de ~metade do consumo vira sobrevivência por
  rodízio; T1 sobe sem a economia ficar saudável.
- Economia e regra de fome estão acopladas: ou a oferta cobre ~o consumo (T3),
  ou a privação precisa pesar (variantes A–D, mantidas fora por decisão).
- O controlador regional não equilibra comida e avanço (T5 = 0): é limitação do
  controlador, não prova de desequilíbrio do jogo.

Propostas para decisão (nada implementado):
1. Fonte renovável proporcional ao grupo (ex.: Mercado repõe 1 busca/noite e a
   busca rende 1 comida por 2 consumidores). Mede T3 diretamente.
2. Mapa tático para a Horta abandonada (`EXP-LOC-01`, já tem renovação natural e
   2 comida) — conteúdo novo, exige Designer Narrativo e Board Games.
3. Horta §61 construível no regional com Materiais e Sementes levados da
   Cisterna (hoje arquivados).
4. Ajustar o controlador para alternar comida e pistas antes de julgar T5.
