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

## Ciclos 4–9 (2026-10-30): controlador, fontes e Horta

Mesmos alvos T1–T5. Sementes 1–30 (ajuste) e 31–90 (confirmação, já vistas);
91–120 não usadas. Variantes de regra só na memória do experimento.

### Controlador (falha de estratégia × falha de regra)

- **Laço confirmado**: o controlador base vai ao Mercado sempre que a comida
  está abaixo de 2 dias de consumo. Com Mercado renovável: 435 dias de Mercado,
  3 de descanso, 0 de Estação (1–30). Além disso exige todos os heróis com Vida 3.
- **`StrategicRegionalPlayer`** (subclasse; o base e os artefatos não mudam):
  pista quando a noite está coberta (`risk='covered'`) ou também quando ninguém
  está em privação seguida (`risk='short'`); equipe de longe só com heróis
  Vida ≥ 2 e fadiga ≤ 1; buscas no Mercado proporcionais ao déficit.
- Falha de **regra**, não de estratégia: o Mercado renovável repõe no máximo 1
  busca/noite (2–3 comida) e o consumo é 5–11. Trocar dia de Mercado por pista
  sempre custa comida; o controlador só escolhe onde perder.
- Achado do motor: a carga entregue entra pelo depósito (`World.deposit`); com o
  depósito cheio da água do filtro, **22% da comida trazida se perde** (88 de
  408 na base; 176 de 1748 com reposição).
- A campanha migra com 4,4 de comida para 8,7 consumidores (média, 1–30): falta
  comida desde a noite 0.

### Variantes (sobrevivem / migradas; fome = porções faltando nas sobreviventes)

| Config | 1–30 | 31–90 | Fome | Rádio (todas) 1–30 / 31–90 | Metas 1–30 / 31–90 |
|---|---|---|---|---|---|
| A: motor + controlador base | 2/37 | 0/107 | 62% | 1 / 0 | ·✓··✓ / ····· |
| B: controlador estratégico (short) | 2/37 | 0/107 | 62% | 1 / 4 (pistas 18 / 68) | ·✓··· / ····· |
| C1: B + Mercado renovável ×1,5 (referência) | 7/37 | 25/107 | 46–58% | 2 / 7 | ·✓··· / ·✓·✓· |
| C2: B + coleta por trabalhador (≤ ceil(consumidores/2)) | 2/37 | 1/107 | 21–25% | 1 / 4 | ·✓··· / ·✓··· |
| D: B + Sementes guardadas viram Horta no dia 3 (teto) | 2/37 | 0/107 | 62% | 1 / 4 | ·✓··· / ····· |
| F: base + descarte de água na entrega | 1/37 | 0/107 | 59% | 0 / 0 | ·✓··· / ····· |
| G: base + ração-ponte (1 porção/consumidor) | 1/37 | 1/107 | 43–53% | 0 / 1 | ·✓··· / ·✓··✓ |
| B + G + C2 | 2/37 | 1/107 | 14% | **18 / 39** | ·✓··✓ / ·✓··· |
| **E: B + G + C2 + D + C1 ×1,5** | **26/37 (70%)** | **70/107 (65%)** | 36–38% | 17 / 38 | **✓✓·✓✓** / ✓✓·✓· |

Por tamanho em E (sobrevivem/migradas), 1–30: H2 4/4, H3 7/10, H4 5/8, H5 6/8,
H6 4/7; 31–90: H2 7/7, H3 26/28, H4 10/21, H5 12/22, H6 15/29.

Leitura:
- O controlador estratégico multiplica o avanço narrativo (pistas 2 → 18; com
  ração-ponte e coleta, rádio em 18/37 e 39/107), mas sozinho não muda a
  sobrevivência: falta de oferta.
- D: 31–90 tem 25 campanhas que terminam a Cisterna com Sementes e sem Horta
  (Materiais acabam no filtro). Mesmo pronta no dia 3, a Horta chega depois do
  Colapso típico (dia 4). Ela só pesa com uma ponte que segure os primeiros dias.
- E cumpre 4 de 5 metas no ajuste, mas **falha T3**: as sobreviventes ainda
  vivem de rodízio (36–38% de porções faltando). Em 31–90 também cai T5 (26%).
  E depende do Mercado renovável (referência, não solução) e de G (leitura nova).
- **Crescimento do acampamento: 0 construções regionais em todas as variantes.**
  As estruturas regionais custam madeira e nenhum local tem madeira no saque.
  Bloqueio de conteúdo para a Fase 7.

### Caminho legal da Horta (resumo)
- Sementes: só acolhendo `ZC-MOR-0006` no Condomínio (1–30: 19 vitórias com
  Sementes; 4 viram Horta ativa; 15 param sem Materiais).
- Materiais: 3 iniciais vão ao filtro; 1 carta por região, buscas 5/12.
- Regional: Materiais arquivados na migração; Oficina (`workshop_02`) tem mapa
  e sucata. Proposta D: Horta §61 regional com Sementes guardadas + 2 sucata
  como Materiais + 2 trabalhos (precisa de aprovação; medido só como teto).

### Propostas para decisão (nenhuma implementada no motor)
1. G — ração-ponte única na migração (estender CAMPAIGN l.32).
2. F — descarte voluntário de água também na entrega de comida (estende a regra
   já aprovada para a colheita).
3. D — Horta §61 regional com Sementes guardadas e sucata.
4. C2 — coleta por trabalhador, limitada a ceil(consumidores/2).
5. Fonte de madeira (ou custo em sucata) para as estruturas regionais (Fase 7).

## Ciclos 10–13 (2026-10-30): F aprovada, protótipos G, C2, D e obras

Motor: F como regra (opcional por decisão do grupo); G, C2 e D como protótipos
(`MANUAL_EXPERIMENTAL.md`). Controlador `CampRegionalPlayer` (estratégico com
risco 'short' + trabalhos do acampamento). Reprodução:
`experiments/camp_economy.py --seeds 1-30 [--configs ...] [--salvage 12]`.
Sobrevivem 15 dias / migradas; falta = porções faltando ÷ consumidor-noites
nas sobreviventes.

| Config (1–30) | Sobrevivem | Dias médios | Falta | Pistas | Rádio (sobrev./todas) | T1–T5 |
|---|---|---|---|---|---|---|
| B (estratégico) | 2/37 | 4,1 | 62% | 18 | 0/1 | ·✓··· |
| B+F | 2/37 | 4,4 | 62% | 18 | 0/1 | ·✓··· |
| B+G | 2/37 | 4,6 | 62% | 19 | 0/2 | ·✓··· |
| B+C2 | 2/37 | 5,5 | 57% | 18 | 0/1 | ·✓··· |
| B+D | 2/37 | 4,1 | 62% | 17 | 0/1 | ·✓··· |
| B+F+G | 2/37 | 5,2 | 55% | 40 | 0/18 | ·✓··· |
| B+F+C2 | 2/37 | 6,8 | 23% | 21 | 0/4 | ·✓··· |
| B+F+G+C2 | 2/37 | 7,8 | 16% | 40 | 2/18 | ·✓··✓ |
| F+G+C2+D (ALL) | 3/37 | 8,1 | 21% | 38 | 2/17 | ·✓··✓ |
| ALL + obras + W2 madeira | 5/37 | 6,5 | 15% | 10 | 3/4 | ·✓··✓ |
| idem + Mercado ×1,5 (ref.) | 7/37 | 7,2 | 38% | 6 | 1/1 | ·✓··· |

Confirmação 31–90 (vistas, só confirmação):

| Config | Sobrevivem | Falta | Por tamanho H2/H3/H4/H5/H6 | T1–T5 |
|---|---|---|---|---|
| B | 0/107 | — | 0/0/0/0/0 | ····· |
| B+F+G+C2 | 1/107 | 13% | 0/1/0/0/0 | ·✓··· |
| ALL | 18/107 (17%) | 28% | 2/7, 3/28, 1/21, 6/22, 6/29 | ·✓·✓· |
| ALL + obras + W2 | 12/107 | 23% | 1/7, 3/28, 3/21, 3/22, 2/29 | ·✓·✓· |

Leitura:
- Isoladas, F, G e D não mudam a sobrevivência; C2 alonga a campanha. Juntas, F
  e G liberam a Estação (pistas 18 → 40) porque a chegada deixa de ser só água.
- F+G+C2 corta a falta de 62% para 16%: é a primeira combinação perto de T3
  (≤ 10%), mas as campanhas ainda caem (média 7,8 dias).
- D quase nunca acontece em 1–30: as campanhas com Sementes são recusadas na
  migração por camas (11 de 12 em 1–30). Em 31–90 a Horta D sai em 19.
- Obras (ciclo 12, com madeira só pela variante W2): 22 Hortas EXP-BLD-01 e 2
  Depósitos em 37 campanhas; primeiras sobrevivências de H3 e H4 em 1–30; mas o
  investimento custa comida agora e as pistas caem (38 → 10).
- Ciclo 11 (não melhorou, revertido): poupar herói ferido do trabalho corta a
  coleta pela metade (683 → 333) e a campanha encurta (7,8 → 5,8 dias).
  Reposição do entorno de 25% a 100% dos consumidores: sem efeito (o limite são
  os trabalhadores aptos, não o entorno).
- Ciclo 13 (defeito do controlador corrigido): obras não buscam sucata sem a
  madeira no estoque. Mesas de personas: pistas 6 → 36 na faixa B. ALL + obras
  com W2: 3/37 e 9/107 (a Horta EXP-BLD-01 sai mais tarde).

### Revisão de abordagem (ciclos 10–13)

Nenhuma configuração legal chega a T1 (40%). As causas são estruturais, não do
controlador:
1. Chegada em déficit: comida para menos de uma noite e depósito cheio de água.
   F+G resolvem o depósito, mas G cobre uma noite.
2. Espiral da fome: com Fome ou Sede não se trabalha (RULES l.22); o Colapso
   vem em 3 noites. Obras com 4 dias de crescimento chegam tarde.
3. Grupos pequenos: poucos trabalhadores; heróis chegam feridos da Cisterna.
4. Camas: quem tem Sementes é recusado na migração (D fica fora de alcance).
5. Água: o filtro produz C inicial; com acolhidos falta água toda noite
   (H6 s29: 4 por noite).
6. Madeira: nenhum local tem; sem a variante W2 não há obra regional.

Mercado renovável segue só como referência (aumenta a sobrevivência, mas a falta
sobe para 38% e o rádio some). Propostas estruturais em `CAMP_GROWTH.md`.
