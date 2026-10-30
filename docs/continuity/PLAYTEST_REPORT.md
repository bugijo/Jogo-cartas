# Crescimento do abrigo (D-20) — simulação, 2026-10-30

Simulação, não playtest. Com chegadas de sobreviventes: 1–30 35/53 (66%), 31–90 88/138 (64%); fome 5,8% e 8,7%. Acolher, recusar ou lotar: 61–64% (31–90). Personas 1–30: A 11/53, B 35/53, C 34/53, mista 29/53. `edicao-integral/COMUNIDADE_BALANCEAMENTO.md` ciclo 10.

# Escala por tamanho (D-17) — simulação, 2026-10-30

Simulação, não playtest. Sobrevivem 15 dias: 1–30 39/53 (74%), 31–90 91/138 (66%); fome nas sobreviventes 6,5% e 7,8%.

| Heróis | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|
| 1–30 | 4/4 | 7/10 | 9/14 | 10/14 | 9/11 |
| 31–90 | 4/7 | 16/28 | 23/35 | 23/30 | 25/38 |

Personas (1–30, 212 mesas): A 12/53, B 36/53, C 39/53, mista 30/53. `edicao-integral/COMUNIDADE_BALANCEAMENTO.md` ciclo 9.

# Comunidade rebalanceada pelo diretor — simulação, 2026-10-30

Simulação, não playtest. Sobrevivem 15 dias: 1–30 34/53 (64%), 31–90 88/138 (64%); antes 2/37 e 0/107. Fome nas sobreviventes 17–22% (meta ≤ 10% não cumprida). `edicao-integral/COMUNIDADE_BALANCEAMENTO.md`.

# Comunidade (Missão Mestre) — simulação, 2026-10-30

Simulação automatizada, não playtest. `experiments/community_economy.py`; H2–H6, 15 dias.

| Cenário | 1–30 sobrevivem | 31–90 sobrevivem | Fome nas sobreviventes (1–30) |
|---|---|---|---|
| Base publicada | 2/37 (16 recusas) | 0/107 (31 recusas) | 62% |
| Comunidade (aprovada) | 3/53 | 7/138 | 36% |
| + heróis em viagem + G (não aprovados) | 11/53 | 13/138 | 21% |

Detalhes e decisões: `edicao-integral/COMUNIDADE_BALANCEAMENTO.md`.

# Acampamento regional e personas no regional — simulação, 2026-10-30

F+G+C2+D: 3/37 (1–30) e 18/107 (31–90); falta de comida 21–28% nas sobreviventes
(meta ≤ 10%); rádio 2 e 0 nas sobreviventes. Com obras e madeira experimental
W2: 22 Hortas e 2 Depósitos em 37 campanhas, 5/37 sobrevivem. Mesas de personas
(600, 1–30) no regional: 2 sobrevivem com protótipos. Simulação, não playtest.
Detalhes em `edicao-integral/ECONOMY_EXPERIMENTS.md` e `CAMP_GROWTH.md`.

# Controlador estratégico e fontes de comida — simulação, 2026-10-30

Base 2/37 (1–30) e 0/107 (31–90). Controlador estratégico: pistas 2 → 18, sem
mudar a sobrevivência. Melhor combinação experimental E: 26/37 e 70/107, rádio
17 e 38, mas 36–38% das porções faltando nas sobreviventes (falha T3).
Nenhuma construção regional (sem madeira). Simulação, não playtest. Detalhes em
`edicao-integral/ECONOMY_EXPERIMENTS.md`.

# Economia de comida regional — experimentos, 2026-10-29

Alvos pré-registrados (`ECONOMY_TARGETS.md`). Comida ×1,25–×2 e Horta 4–8: até
2/37 (1–30) e 1/107 (31–90). Mercado repondo 1 busca/noite com comida ×1,5:
68% e 71%, porém ~50% das porções faltando nas sobreviventes e nenhum rádio.
Nenhuma variante cumpre T1–T5. Simulação, não playtest. Detalhes em
`edicao-integral/ECONOMY_EXPERIMENTS.md`.

# Fome em rodízio — protótipo, 2026-10-29

Quatro variantes da privação medidas fora do repositório (1–30 e 31–90). A
sobrevivência atual (2/191) vem do rodízio, permitido por RULES l.49 + §25.
Endurecer a sequência (A) ou punir Moral (C) leva a 0/191; B não muda; D 2/191
com sementes diferentes. Tabela em `edicao-integral/HORTA_CONTINUITY.md`.

# Horta com descarte voluntário de água — resultado real, 2026-10-29

H2–H6, 15 dias regionais. Sementes 1–30: 2 de 53 sobrevivem (H5 s10 e H6 s10,
56 comida colhidas cada; sem descarte 0). Validação 31–90: 0 de 138 (só H3 s70
migra com Horta e cai no dia 7). As duas sobrevivências mantêm 6–7 porções
faltando por noite em rodízio, sem ferimento (RULES l.49): não indicam economia
saudável. 47 migrações recusadas por camas em 1–90. Detalhes em
`edicao-integral/HORTA_CONTINUITY.md`.

# Horta H1 — resultado real, 2026-10-29

Motor e controlador (`7f19a5e`), H2–H6, sementes 1–30. Cisterna: variante A
53 vitórias (base 52), 4 com Horta pronta. Regional (15 dias): 16 migrações
recusadas por camas (base 0), 2 migram com Horta, **0 sobrevivem**, colheita
total 1 comida porque o depósito chega cheio de água. Diferente do protótipo
B+D (31/53), que não tinha esses limites. Tabelas em
`edicao-integral/HORTA_CONTINUITY.md`.

# Campanha regional com filtro contínuo — resultado real, 2026-10-29

Filtro implementado no motor (decisão aprovada). Medição real (`simulate_regional_campaign.py`,
52 vitórias H2–H6, sementes 1–30, até 15 dias): **0 sobrevivem**, colapso por
fome em 3,3–4,6 dias, 1 pista no total, rádio nunca — igual ao protótipo D.
A comida trava antes da água; a Horta (protótipo B+D: 31/53) depende de decisão
(`edicao-integral/HORTA_CONTINUITY.md`). Os números da tabela abaixo marcados
como protótipo não são resultados do motor.

# Opções de comida regional — PROTÓTIPOS medidos, 2026-10-29 (não implementadas)

Protótipos só no rascunho (fora do repositório), mesma varredura: 53 campanhas
(vitórias da Cisterna H2–H6, sementes 1–30, mais a seed 22 fixa), até 15 dias.

| Opção | Base | Sobrevivem 15 dias | ≥1 pista | Rádio | Cartão |
|---|---|---|---|---|---|
| Atual | — | 0 | 2 | 0 | 0 |
| A — Coleta §26 (2 porções/dia) | RULES §26 | 0 | 3 | 1 | 0 |
| C — mapa para a Horta `EXP-LOC-01` | dados regionais (sem mapa hoje) | 0 | 0 | 0 | 0 |
| D — filtro produz C água/amanhecer | CAMPAIGN (Cisterna) | 0 | 2 | 0 | 0 |
| B — Horta-estrutura 4 comida/dia | RULES §61 | 0 | 10 | 3 | 0 |
| **B + D** | RULES §61 + CAMPAIGN | **31** | 39 | 24 | 10 |
| A + D | | 2 | 3 | 1 | 0 |
| A + B + D | | 21 | 15 | 7 | 0 |

- Comida e água travam juntas: só B+D fecha as duas. Com B+D, todo caminho
  vivo termina no bloqueio de combustível da instalação militar.
- B assume a Horta pronta na migração; a regra exige 2 Materiais + Sementes +
  2 trabalhos, e o regional não tem Sementes nem Materiais gastáveis.

# Campanha regional — após descarte do excedente na migração, 2026-10-29

Mesma medição (sementes 1–30, até 15 dias, sem ajuste), com o excedente de
estoque descartado na migração (decisão aprovada). Todas as vitórias migram.

| Tam. | Vitórias migradas | Derrota parcial | ≥1 pista | Rádio | Dias médios |
|---|---|---|---|---|---|
| H2 | 5 | 5 | 0 | 0 | 4.6 |
| H3 | 11 | 11 | 1 | 0 | 4.6 |
| H4 | 12 | 12 | 0 | 0 | 3.8 |
| H5 | 12 | 12 | 0 | 0 | 3.3 |
| H6 | 12 | 12 | 0 | 0 | 3.8 |

- 52/52 campanhas terminam em derrota parcial por fome em 3–5 dias; 1 pista no
  total; rádio nunca. O gargalo restante é a comida regional
  (`P2-REGIONAL-FOOD-ECONOMY`).

# Campanha regional multi-dia — 2026-10-29

Política regional escrita só com a seed 22 H2; medida sem ajuste a partir das
vitórias legais da Cisterna (adaptativo publicado, sementes 1–30), até 15 dias,
cartas de Viagem ligadas. Artefato: `edicao-integral/replays/regional_campaign_sweep.json`.

| Tam. | Vitórias Cisterna | Migração recusada | Derrota parcial | ≥1 pista | Rádio | Dias médios |
|---|---|---|---|---|---|---|
| H2 | 5 | 2 | 3 | 0 | 0 | 4.3 |
| H3 | 11 | 1 | 10 | 1 | 0 | 4.4 |
| H4 | 12 | 7 | 5 | 0 | 0 | 3.8 |
| H5 | 12 | 9 | 3 | 0 | 0 | 3.0 |
| H6 | 12 | 12 | 0 | 0 | 0 | None |

- Recusa de migração: água da Cisterna acima do depósito regional 30 (regra pendente).
- Toda campanha migrada colapsa por fome em ~3–4 dias: o Mercado (9 porções no
  máximo) é a única comida com mapa; a Estação a pé com cartas quase nunca cabe
  no relógio 10. Só H3 seed 20 coletou 1 pista; nenhuma decodificou o rádio.
- Seed 22 H2 (replay `regional_campaign_seed22.json`): 6 dias, 3 expedições,
  1 pista (Célia), derrota parcial no dia 6.
- Leitura: limite de design da economia regional, não do controlador; decisão
  pendente `P2-REGIONAL-FOOD-ECONOMY`.

# Relatório de partidas automatizadas — atualização 2026-10-27 (validação 61–90, H2, auditoria)

## Decisões aprovadas aplicadas

Registradas em `edicao-integral/MANUAL_EXPERIMENTAL.md` (sem alterar `RULES.md`):
escolta custa 1 PA para iniciar, movimento normal depois; Ferragens
(`ZC-VIA-0010`) sem Material levado não causa perda nem bloqueia a viagem.

## Validação cega nas sementes inéditas 61–90

Medida uma vez, antes de qualquer ajuste e antes da regra de Ferragens:

| Controlador | H2 | H3 | H4 | H5 | H6 | Total |
|---|---|---|---|---|---|---|
| Fixo | 0 | 0 | 0 | 0 | 0 | 0 |
| Adaptativo anterior | 3 | 1 | 0 | 2 | 3 | 9 |
| **Adaptativo com táticas** | 4 | 8 | 13 | 14 | 17 | **56** |

Depois da regra aprovada de Ferragens (mesmas sementes; não é mais medida cega),
o adaptativo com táticas fica em 66/150 (4/13/13/19/17). Métricas finais nas
sementes 61–90 (`replays/cistern_sweep_h2_h6.json`, grupo `adaptive_auto_validation`):

| | H2 | H3 | H4 | H5 | H6 |
|---|---|---|---|---|---|
| Vitórias /30 | 4 | 13 | 13 | 19 | 17 |
| Fome/Sede no fim (média de pessoas) | 2.97 | 3.0 | 2.63 | 1.6 | 3.07 |
| Emergências na Estação | 30/56 | 10/45 | 9/43 | 8/36 | 14/39 |
| Incapacitações | 36 | 25 | 16 | 11 | 15 |
| Rodadas por expedição (média / Estação) | 5.94 / 6.68 | 5.82 / 6.82 | 5.47 / 6.44 | 5.5 / 7.25 | 5.76 / 7.38 |

Adaptativo anterior, mesmas sementes: emergências na Estação 46/53 (H3) a 78/82
(H5), incapacitações 52–93, fome média 5–8 pessoas a partir de H3.

## H2 (investigação apenas nas sementes de ajuste 1–30)

- A hipótese "a rota cautelosa prejudica H2" **não se confirmou**: sozinha ela
  dá +1 vitória. Quem eleva as emergências em H2 é o apoio (18/40 → 24/33), sem
  perder vitórias.
- Em 16/30 partidas a nova tentativa na Estação era abortada pelo planejador de
  carga (equipe reduzida não comportava as duas peças) e a campanha parava.
  Corrigido: o adaptativo leva as peças que cabem ou fica no abrigo. Vitórias
  iguais (5/30), campanha não aborta mais.
- Testadas e descartadas: dupla (um herói leva as duas peças, o outro apoia):
  5 → 2; rota longa para H2 na Estação: 5 → 0.
- Leitura: com dois heróis a Estação é muito dura para este controlador. Sinal
  de design para avaliar com playtest humano (não é prova de equilíbrio).

## Auditoria de apoio e escolta (sementes 1–30, vitórias H2..H6)

| Configuração | Vitórias | Observação |
|---|---|---|
| Todas as táticas | 5/11/12/12/12 | apoio: 112–387 ataques por 30 partidas |
| Sem apoio | 4/0/2/10/13 | apoio é a alavanca de H3–H4 |
| Sem escolta | 5/8/11/10/12 | escolta soma +3/+1/+2 em H3–H5 |
| Escolta custando 0 PA | 5/11/12/12/12 | sobrevivência com escolta H3 8/12 → 11/12 |

Escolta em H2 nunca salvou (0/4): um único herói apto não consegue resgatar e
voltar. O custo aprovado de 1 PA tem efeito marginal nas vitórias.

## Tática da Estação 2026-10-27

## Diagnóstico

Nas expedições à Estação que falhavam, as tarefas em geral já estavam feitas.
A emergência vinha de um herói incapacitado longe da saída (ninguém sai sem
ele), quase sempre o portador da Membrana: ele ia sozinho pela rota 7→11→15→14,
vizinha ao surgimento (16), enquanto colegas sem tarefa esperavam na saída.

## Mudanças

- **Motor** (`cistern_tactics02.py`): escolta de incapacitado (§31/§43), que não
  existia. Herói apto na mesma zona liga a escolta; mover não custa PA extra e
  leva o incapacitado junto; ocupa 2 cargas; um por escoltante; ligação refeita
  se o escoltante cair; persiste no snapshot (saves antigos carregam).
  **Decisão pendente:** o texto não fixa o custo de *ligar* a escolta; o motor
  usa 1 PA (`ESCORT_LINK_AP`), leitura conservadora.
- **Controlador** (só no modo adaptativo; `tactics` liga cada uma):
  `escort` (resgatar e levar à saída), `late_retreat` (abandonar tarefas quando
  só resta tempo para sair, mantendo a carga), `cautious` (rota evita inimigos e
  vizinhança do surgimento) e `support` (herói sem tarefa acompanha o colega com
  a tarefa mais distante e ataca os inimigos da zona dele).
  `wounded_retreat` foi medido e **piorou** (−7 nas sementes 1–30); fica
  desligado.
- Política escolhida só nas sementes 1–30: Oficina primeiro em todos os
  tamanhos. A regra anterior (Estação primeiro em H5+) ficou pior com as táticas.

## Resultado nas sementes reservadas 31–60 (vitórias certificadas / 30)

| Controlador | H2 | H3 | H4 | H5 | H6 | Total |
|---|---|---|---|---|---|---|
| Fixo | 2 | 0 | 0 | 0 | 0 | 2 |
| Adaptativo anterior (sem táticas) | 7 | 0 | 0 | 6 | 10 | 23 |
| **Adaptativo com táticas** | 5 | **15** | **19** | 9 | **18** | **66** |

Emergências na Estação (falhas/expedições), anterior → novo: H2 17/47 → 23/50,
H3 55/59 → 8/36, H4 60/62 → 3/35, H5 62/71 → 19/40, H6 51/64 → 8/35.

Leitura: a tática de apoio é a maior alavanca em H3+. Em H2 não há herói livre
para apoiar; H2 piorou um pouco (dentro do ruído). A suposição de que a rota
cautelosa seria a causa foi refutada depois (ver investigação de H2 acima). Nota de método: as
sementes 31–60 já tinham sido observadas em medições anteriores; nenhum
parâmetro novo foi escolhido olhando para elas. Continua sendo medida de um
controlador, não de equilíbrio nem de jogadores humanos.

## Coleta de emergência 2026-10-27

## Coleta de emergência (RULES §26) no motor e no controlador adaptativo

`Cistern02.plan_emergency_collection()` / `IntegratedCampaign.plan_emergency_collection()`:
no amanhecer, até 2 pessoas (heróis ou adultos confiáveis, sem Fome/Sede/fadiga 3,
fora de observação) escolhem Conserva ou Água; cada uma gera **1 porção avulsa**
na fase de trabalhos, máximo 2 por dia para a comunidade. Um trabalho por pessoa:
não acumula com filtro, vigia ou expedição. Cerco pendente precede a coleta;
o plano sobrevive a save/load e é limpo no dia seguinte. 9 testes novos.

O controlador adaptativo usa quem sobra no abrigo depois de filtro e vigias,
quando há déficit projetado. Sementes reservadas 31–60:

| Controlador | H2 | H3 | H4 | H5 | H6 |
|---|---|---|---|---|---|
| Fixo | 2 | 0 | 0 | 0 | 0 |
| Adaptativo automático, sem coleta | 5 | 0 | 0 | 7 | 11 |
| Adaptativo automático, com coleta | 7 | 0 | 0 | 6 | 10 |

Leitura: efeito pequeno e dentro do ruído de 30 sementes (+2 em H2, −1 em
H5/H6 por mudanças em cadeia de fome/fadiga/equipe). Fome no fim praticamente
não muda (H3 30/30, H4 29/30). Duas porções por dia contra 5–13 consumidores
não compensam a perda das expedições: o gargalo segue sendo o controlador
tático na Estação. A coleta foi incluída também nos grupos adaptativos 1–30
(Estação primeiro em H6 passou de 8 para 9).

O artefato `replays/cistern_to_transmission_seed22_clue_returned.json` foi
regenerado: o estado da Cisterna ganhou `collection_plan`, mudando apenas o
digest/id da migração. Saves migrados antes continuam válidos, porque o digest é
conferido contra o arquivo de origem gravado junto.

## Estratégia adaptativa 2026-10-27

## Controlador adaptativo da Cisterna (`CampaignPlayer02.adaptive=True`)

No amanhecer, sem informação oculta: reserva cada etapa assim que a peça chegou
em dia anterior; escolhe o destino pelas peças faltantes (nova tentativa na
Estação/Oficina, inclusive recuperando peça deixada no chão por emergência,
§34) e depois por déficit projetado de comida/água (Mercado, Hospital,
Condomínio, Posto — só lotes ainda não retirados); adultos civis trabalham no
filtro (inclusive etapa A no dia 3); vigias (até 3) saem de quem fica no abrigo.
O modo fixo continua padrão e preserva o replay certificado da seed 22.

Vitórias certificadas (`replays/cistern_sweep_h2_h6.json`, schema 2, 750 tentativas):

| Controlador | Sementes | H2 | H3 | H4 | H5 | H6 |
|---|---|---|---|---|---|---|
| Fixo | 1–30 | 2 | 1 | 1 | 0 | 0 |
| Adaptativo, Oficina primeiro | 1–30 | 3 | 0 | 0 | 0 | 0 |
| Adaptativo, Estação primeiro | 1–30 | 0 | 0 | 1 | 7 | 8 |
| Fixo | 31–60 (reservadas) | 2 | 0 | 0 | 0 | 0 |
| Adaptativo automático (H≤4 Oficina, H≥5 Estação) | 31–60 (reservadas) | **5** | 0 | 0 | **7** | **11** |

A regra "ordem por tamanho" foi escolhida olhando só as sementes 1–30 e medida
uma única vez em 31–60. Leitura: o adaptativo melhora H2 e H5–H6; H3–H4 seguem
em 0 porque a Estação falha repetidamente (retirada de emergência no mapa) e as
novas tentativas consomem os dias que seriam de comida — no fim, 29–30 das 30
partidas H3/H4 têm alguém com Fome. O gargalo agora é o **controlador tático na
Estação**, não o planejamento. Continua não sendo evidência de equilíbrio.

Defeitos corrigidos nesta rodada:
- **Motor** (`cistern_tactics02.py`): ao 25º inimigo o mapa marcava expedição
  perdida e depois recusava a emergência que §39 manda oferecer; a campanha
  travava. Agora a emergência é aceita uma vez após `overrun` (mesma semântica já
  testada na emboscada). Formato de save inalterado.
- **Controlador**: vigias planejados nunca rolavam dados (`guard_rolls` virava
  lista vazia); herói sem ferramenta tentava forçar porta bloqueada; equipamento
  declarado para quem não viajava; nova rodada após invasão.

Lacuna de regra registrada, sem alteração: `ZC-VIA-0010` (Ferragens) manda, na
ida, deixar 1 Material levado no chão, mas não define o caso sem Material
levado. O motor recusa; o controlador encerra a tentativa como
`blocked_expedition_rule_gap` (1–2 por grupo de 30). Precisa de decisão.

Não implementado no motor: Coleta de emergência (§26, adultos geram até 2
porções/dia). Seria a resposta natural à fome observada em H3–H4.

## Varredura inicial 2026-10-27

## Varredura da Cisterna H2–H6 (controlador heurístico, 150 tentativas)

`edicao-integral/simulate_cistern_sweep.py` executa `CampaignPlayer02` em H2–H6,
sementes 1–30, só por ações públicas; o artefato
`edicao-integral/replays/cistern_sweep_h2_h6.json` é verificado por igualdade
(16 684 decisões registradas no total).

| Tamanho | C inicial | Cartas por lote | Vitórias certificadas | Causa dominante |
|---|---|---|---|---|
| H2 | 3–5 | 1–2 | 2/30 (seeds 20, 22) | Estação: retirada de emergência (11); filtro sem material/peça (6); derrota parcial por fome (5); Bomba falhou (4) |
| H3 | 4–7 | 1–2 | 1/30 (seed 22) | Estação: retirada de emergência (27) |
| H4 | 5–9 | 2–3 | 1/30 (seed 22) | Estação: retirada de emergência (27) |
| H5 | 7–11 | 2–3 | 0/30 | Estação: retirada de emergência (29) |
| H6 | 9–13 | 3–4 | 0/30 | Estação: retirada de emergência (29) |

Leitura correta: mede o **plano fixo** Mercado → Oficina → Estação, sem
expedições nos dias 4–5, sem vigias e sem busca de comida extra. Limitar a
equipe por destino (grade 2–4 heróis) não alterou a taxa (≈1/30). Isso é
evidência de fraqueza do controlador e de pressão crescente na Estação com
grupos grandes, **não** taxa de vitória do jogo nem prova de equilíbrio.

Correções do controlador nesta rodada (sem mudar regras nem o replay seed 22,
que segue com 98 decisões idênticas): redistribuição quando a carga de
estrada ocupa espaço; descarte registrado de lotes de mantimento que não cabem
(peças/equipamento nunca); substituto de peça precisa ter espaço; Machado sai
com quem o retirou; heróis inaptos ficam no abrigo; filtro com até 2
trabalhadores aptos; escolha de `ZC-VIA-0004` preserva material necessário ao
filtro.

Observação de design para aprovação (nenhuma regra alterada): o lote local tem
`ceil(C/4)` cartas e é indivisível no motor. Em H6 com C 13 o lote ocupa 4
cartas — exige herói sem nenhum equipamento, e todos começam com Pé de cabra.
Se `RULES.md`/`CAMPAIGN.md` pretende permitir dividir o lote entre heróis, isso
precisa ser escrito; hoje o motor segue a leitura de lote inteiro.

## Atualização 2026-10-26

## Tentativa narrativa/combustível desta retomada

| Execução | Resultado | Leitura correta |
|---|---|---|
| `verify_continuous_campaign.py`, seed 22, schema 3 | `local_defeat_clock_blocked`; 27 decisões regionais | Cisterna legal e migração; expedição legal à Estação; Célia investigada e uma pista copiada por ações físicas; extração não coube no clock e ocorreu retirada no 7/10. Não recrutou Célia, não decifrou rádio, não visitou Posto ou instalação. |
| Oficina `EXP-FUEL-CACHE-WORKSHOP-01`, seed 22, 8 perfis | 8/8 retornaram e depositaram 8 combustíveis | Uma expedição experimental isolada; perfis são políticas programáticas determinísticas compartilhando o mesmo motor, não jogadores cognitivos nem provas de equilíbrio. Não prova Posto/van ou campanha completa. |
| Regressão completa | 314 testes passaram nesta árvore | Inclui recibos, identidade, custos, PA de companheiro, saída, save/load, cache/rota da Oficina, Cisterna e bloqueio regional. Fixtures isoladas não comprovam rota integral. |

## Provas reproduzidas

| Execução | Resultado | O que prova | O que não prova |
| --- | --- | --- | --- |
| `verify_campaign_player02.py`, seed 22 | `verified_victory`, 5 dias/noites, 3 expedições, 98 decisões | Uma trajetória legal da Cisterna desde a preparação, mantendo seu certificado como regressão. | Equilíbrio, outras sementes/tamanhos, ou sucesso no arco 2. |
| `verify_continuous_campaign.py`, seed 22 | ver atualização ativa acima | Uma pista regional obtida legalmente e retirada porque a extração não cabe no clock/PA atual. | Prova de recrutamento, rádio, combustível da missão, transmissor ou vitória. |
| `verify_regional_player.py`, seed 22 | `regional_agent_round_trip_verified` | Cisterna → migração → Mercado; porta comum, movimento, busca, save/load, saída/retorno, entrega de 2 comida e 1 água, consumo do dia sem déficit, sem criar combustível. | Célia, cartas de Viagem regionais, Posto, transmissor, veículo, gate militar, defesa final ou vitória do arco 2. |

## Método e limite

`AdaptiveRegionalPlayer` é uma política programática determinística, com
prioridades observáveis e chamadas às APIs públicas do motor. Os nomes de
perfil variam a preferência de combate de forma limitada; não representam oito
agentes cognitivos independentes e não recebem informação futura/oculta.
Os oito perfis foram comparados somente na expedição experimental da Oficina,
na mesma seed. A tentativa da Estação usou `balanced`. Testes de safe-zone e
recibos ainda incluem fixtures isoladas.

Não foram calculadas taxas de vitória nem avaliação de equilíbrio. Não houve
playtest humano, impressão física ou teste de montagem. Nenhum tempo de mesa foi
estimado por tempo computacional.

Comando de reprodução:

```bash
python3 edicao-integral/verify_campaign_player02.py
python3 edicao-integral/verify_continuous_campaign.py
python3 edicao-integral/verify_regional_player.py
```

## Jogadores virtuais (simulação, não playtest) — 2026-10-29

| Grupo | Mesas | Vitórias | Roteiro fixo | Noites médias | Conflitos/mesa |
|---|---|---|---|---|---|
| A | 150 | 4 | 125 | 3,46 | 11,8 |
| B | 150 | 34 | 0 | 4,99 | 34,1 |
| C | 150 | 34 | 11 | 4,87 | 17,1 |
| mista | 150 | 26 | 38 | 4,53 | 32,1 |

Resultados refletem traços escolhidos para as personas; hipóteses em `edicao-integral/ESCRITORIO_DEV.md`.
