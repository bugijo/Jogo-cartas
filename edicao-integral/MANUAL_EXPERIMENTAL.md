# Manual experimental — branch `evolucao/zona-zero-sistema-v1`

Regras e leituras usadas pelo motor experimental. **Não substituem** `RULES.md`,
`CAMPAIGN.md` nem o kit físico 0.2, que permanecem intactos. Cada item diz se é
decisão aprovada pelo responsável do projeto ou leitura do motor ainda sem
aprovação.

## Decisões aprovadas (2026-10-27)

### Escolta de incapacitado (RULES §31/§43)
- Iniciar a escolta custa **1 PA**; o herói apto e o incapacitado precisam estar
  na mesma zona.
- Depois, cada deslocamento paga o custo normal de movimento (inclusive +1 ao
  sair de zona com inimigo), **sem PA adicional pela escolta**; o incapacitado
  acompanha o escoltante.
- O incapacitado ocupa duas cargas do escoltante; cada herói escolta um só. Se
  o escoltante também ficar incapacitado, outro herói pode iniciar nova escolta.
- Motor: `Tactical02.escort()`, constante `ESCORT_LINK_AP = 1`.

### Ferragens `ZC-VIA-0010` sem Material levado
- Na ida, se a equipe **não transporta Material**, a carta **não causa perda**
  e não bloqueia a viagem; o recibo registra `no_material_carried`.
- Com Material levado, a ida descarta 1 Material, como antes. Na volta, a carta
  continua acrescentando 1 Material ao estoque.
- Motor: `Travel02.apply()`; testes em `tests/test_travel02.py`.

### Durabilidade na emboscada regional (aprovada em 2026-10-29)
- Nas emboscadas regionais jogadas no mapa M1 da 0.2, **não se consome
  durabilidade** dos equipamentos: essa mecânica não faz parte do combate 0.2.
- Vale só para a ponte regional experimental; `RULES.md` e o kit físico 0.2 não
  mudam. Motor: `World.regional_ambush_attack` não altera durabilidade; teste em
  `tests/test_regional_travel_controller.py`.

### Excedente de estoque na migração (aprovada em 2026-10-29)
- Ao migrar da Cisterna, o que passar do depósito regional (30 na base) é
  **descartado** e registrado no recibo da migração (`storage_discarded`, com
  capacidade e quantidades).
- Ordem do descarte (leitura do motor): água primeiro, depois comida, remédio,
  Munição e combustível. Na prática só a água excede (até 46 em H6).
- Migrações dentro do limite não mudam (seed 22 sem campo novo). Motor:
  `IntegratedCampaign.transition_to_last_transmission`; testes em
  `tests/test_regional_campaign.py`.

### Filtro da Cisterna no regional (aprovada em 2026-10-29)
- Se a Cisterna termina com o filtro funcional e o abrigo é o mesmo, a migração
  registra `continuity_filter` (produção = C inicial). A cada amanhecer regional,
  depois da refeição, o filtro deposita essa água **respeitando o depósito**; o
  que não cabe não é criado (`filter_water.not_stored`). Sem produção após
  Colapso (o abrigo deixa de ser o mesmo).
- Ligado por `World.regional_filter_production` (padrão desligado, como a ponte
  de Viagem) para não alterar os replays regionais certificados; a campanha
  contínua e a medição ligam. Testes: `tests/test_continuity_filter.py`.
- Não modelado: dano ao filtro no regional (crises/cercos regionais não o atingem).

### Horta §61 construída na Cisterna e migrada — H1 (aprovada em 2026-10-29)
- Acolher `ZC-MOR-0006` no O2 do Condomínio entrega 1 Sementes como carga 1 do
  herói, se houver espaço (texto da carta); a carga só chega com retorno legal.
- Na Cisterna: reserva no amanhecer de terreno (8 + barracas extras), 2 Materiais
  e Sementes recebidas em dia anterior; 2 trabalhos concluem; a partir do dia
  seguinte um trabalhador (herói ou adulto apto) colhe 4 comida na fase de
  trabalhos. Cerco que danifica a Horta a desativa.
- Migra como `continuity_garden` só pronta e ativa; no regional, um herói ou
  adulto designado no amanhecer colhe 4 comida antes da refeição, pelo depósito
  (o que não cabe não é criado). Herói designado não sai em expedição.
- Leituras do motor: limite de 2 trabalhos/dia **por projeto** (RULES l.24), à
  parte do filtro; "Material encontrado hoje só reservável amanhã" não é checado
  (mesma leitura já usada nas etapas do filtro); reparo da Horta não modelado.
- Controlador: `CampaignPlayer02.garden` (desligado por padrão). Testes:
  `tests/test_garden_continuity.py`. Resultado e bloqueios em `HORTA_CONTINUITY.md`.

## Decisões anteriores do responsável

- Lote de mantimentos indivisível: `ceil(C/4)` cartas por lote, retirado
  inteiro por um herói (pode exigir herói sem equipamento em H6).

## Leituras do motor (texto escrito, implementação sem ambiguidade relevante)

- Coleta de emergência (§26): até 2 porções avulsas por dia para a comunidade,
  uma por adulto/herói alocado; não acumula com filtro, vigia ou expedição.
- 25º inimigo (§39): a expedição é perdida e a emergência continua oferecida.

## Ponte de Viagem regional (Última Transmissão) — opcional

`World.regional_travel_cards = True` liga o baralho persistente de Viagem ao
transporte regional. Desligado por padrão para preservar os replays registrados.

- Uma carta por trecho pago (§29), na ida e na volta, do baralho regional
  persistente; nenhuma conversão de perto/médio/longe para rota curta/longa: o
  número de trechos continua o do local regional.
- Trecho noturno (relógio 9–10) revela uma carta extra sem segmento adicional.
- Placa (`ZC-VIA-0003`) ignora a próxima carta normal da volta.
- O motor regional ainda não tem ação de levar comida/água/Material na viagem;
  por isso só as opções sem carga levada ficam disponíveis: Água → fadiga,
  Barricada → Pressão, Ajuda → recusar, Cão → recusar. Leitura do motor, não
  regra nova; muda quando houver carga levada regional.
- Efeitos sem equivalente regional ficam em `regional_travel_archive`
  (Pressão externa, Material de Ferragens na volta), não gastáveis, mesma
  política da migração da Cisterna.
- Emboscada (`ZC-VIA-0005`) fica pendente até ser resolvida no M1 da regra 0.2
  (§30) por `start_regional_ambush` / `finish_regional_ambush`:
  - armas: só itens do gabarito regional cujo nome é arma 0.2 (hoje Pé de
    cabra); sem arma, o herói luta desarmado — nenhum equipamento é criado;
  - Munição levada: 0 (o motor regional não leva carga na viagem);
  - ferimentos, fadiga, Fome/Sede (penalidade de PA), Horda regional e relógio
    real vêm do estado regional e voltam a ele; NPCs da equipe recebem a fadiga
    noturna das rodadas;
  - emergência na estrada (§34): +1 ferimento, fadiga 3, perde a carga obtida e
    todos voltam ao abrigo. Com carga única (cartão/bateria) ou veículo, o motor
    recusa (`NotImplementedError`), porque o destino dessas peças na estrada não
    está modelado.
  - dados dos ataques vêm do RNG persistido do mundo
    (`World.regional_ambush_attack`), nunca do jogador;
  - a durabilidade do equipamento regional não é consumida na emboscada
    (decisão aprovada em 2026-10-29, abaixo).

### Descarte voluntário de água para a colheita da Horta (aprovada em 2026-10-29)
- Ao designar o trabalhador da Horta no amanhecer regional, o abrigo pode
  aceitar o descarte (`World.assign_continuity_garden(pessoa, discard_water=True)`).
- Na colheita (antes da refeição) descarta-se só o que falta de espaço para as
  4 comida, e só a água acima do consumo previsto da refeição desta noite
  (1 por consumidor). Com espaço livre ou água no limite, nada é descartado.
- O depósito regional segue 30; o que ainda não couber não é criado.
- Registro: `garden_food.water_discarded` no resultado do dia (`World.log`).
  Sem o aceite, o recibo da colheita não muda.
- Cisterna e replays certificados não mudam. O controlador regional
  (`RegionalCampaignPlayer(discard_water=True)`) aceita o descarte só na medição
  com Horta. Testes: `tests/test_garden_continuity.py` (`WaterDiscardTests`).

## Acampamento regional (2026-10-30)

**F — prioridade de comida no depósito (aprovada).** Decisão do grupo, registrada
no histórico (`storage_priority`): enquanto ligada, toda comida que chega
(entrega, colheita, coleta, ração) descarta só a água que falta de espaço e só a
acima do consumo previsto da noite; cada descarte vira `storage_discard` no
histórico. Depósito continua 30; nada é criado. Desligada por padrão
(`World.set_storage_priority`). Sucata e madeira não descartam água.

**Protótipos (aprovados só para teste; não são regra definitiva).** Ligados por
mundo com `World.enable_regional_prototypes`; desligados, saves e replays antigos
ficam idênticos (`regional_camp = None`).

- G — ração-ponte: uma vez, antes da primeira noite regional, 1 comida por
  consumidor, pelo depósito. Origem: a Ponte acolhe o grupo evacuado (CAMPAIGN,
  Evacuação) e entrega a ração de viagem. Nunca de novo (`bridge_claimed`).
- C2 — coleta no entorno: no amanhecer, antes da expedição, adulto ou herói
  apto coleta 1 comida (fase de trabalhos). Limites: ceil(consumidores/2)
  coletores por dia; o entorno tem reserva `pool` (padrão 2 × consumidores na
  chegada) que repõe ceil(consumidores/4) por amanhecer. Coletar é o trabalho
  do dia: sem recuperação §25 e sem outra tarefa (Horta, obra, expedição).
  Precedente: trabalho local da Ponte (CAMPAIGN, Recuperar Santa Aurora).
- D — Horta §61 regional: 1 Sementes transportadas da Cisterna (arquivadas na
  migração) + 2 sucata (no lugar dos 2 Materiais, sem equivalente regional) +
  2 trabalhos de adulto ou herói (máximo 2 por dia). Produz 4 comida por dia
  com um trabalhador, a partir do amanhecer seguinte à conclusão. Uma só por
  campanha (as Sementes se gastam).

Testes: `tests/test_regional_camp.py`. Medição: `ECONOMY_EXPERIMENTS.md`
(ciclos 10–13) e `CAMP_GROWTH.md`.

## Comunidade (Missão Mestre, aprovada em princípio em 2026-10-30)

Princípios aprovados pelo criador; números provisórios em `data/community.json`
(`COMUNIDADE_BALANCEAMENTO.md`). Liga por campanha na migração
(`transition_to_last_transmission(community=True)`); desligada, nada muda.
Código `community.py`; testes `tests/test_community.py`.

- **Trabalhadores**: adultos migrados e especialistas sem trabalho fixo
  trabalham sem supervisão; uma função por dia (cozinhar, obra, cuidar,
  vigiar, armadilha, Horta ou viagem). Heróis podem pegar trabalhos do
  acampamento quando não saem na expedição tática.
- **Profissões** (11, baralho de profissões; especialistas EXP-NPC usam a
  sua): +1 no D6 da atividade compatível; agricultor +1 comida na Horta;
  cozinheiro +1 carne por cozimento; carpinteiro +1 trabalho de obra;
  enfermeiro cuida de 2; guarda evita a crise com 3+ (demais 4+). Profissão
  não impede outra atividade, só não dá o bônus.
- **Bagagem** (D6 ao resgatar): nada / 1 comida / 1 comida + 1 água /
  2 comida / 1 madeira + 1 sucata / 1 remédio + 1 comida.
- **Viagem automática** (trabalhadores e heróis que não saem na expedição
  tática do dia; herói em viagem não entra em expedição): escolhe pessoa, atividade e 1–3
  dias; leva até 1 comida + 1 água por dia (é a refeição dela: fora, não come
  no abrigo); volta no amanhecer de partida + dias. Rendimento = (D6 + bônus)
  × dias − 1 por dia sem ração; unidades = pontos ÷ fator, até 6 de carga e
  até a reserva do entorno. Fatores: caça 4 (carne), pesca 1 (comida),
  lenha 2 (madeira), coleta 1 (frutas), sucata 3, água 1 (bruta). Cartas
  (baralho de 12): 1 por viagem, +1 com 3 dias, +1 em caça/sucata. Tranquila
  ×3, abundância (+D6 pontos), descoberta (+1 sucata), chuva (−2 pontos),
  atraso (volta 1 dia depois, sem ração), ferimento, perda (metade da carga),
  equipamento (−1 sucata do abrigo ou −1 unidade), zumbis (D6: 1–2 ferimento e
  metade; 3–4 −1 unidade), pista (+1 pista, uma vez por campanha).
- **Entorno finito**: caça 6 (+1/dia), peixe 8 de início, máx. 12 (+3),
  madeira 12 (+1), frutas 10 de início, máx. 12 (+3), sucata das ruínas 6
  (sem reposição). Horta EXP-BLD-01 com Comunidade: 4 comida/dia (era 2). Floresta, rio e
  ruínas são zonas de trabalho automático, não mapas táticos.
- **Comida**: carne crua dura 2 noites; cozinhar (1 carne por trabalho) dá
  **4 porções** com 1 madeira ou com a Cozinha, 2 porções improvisadas.
  Frutas: 1 comida cada e +1 água a cada 2. Água bruta precisa do filtro, do
  Reservatório ou de 1 madeira a cada 3.
- **Água em tanques**: 30 (+12 com Reservatório), fora do depósito seco
  (30): água não ocupa o lugar da comida.
- **Coletor de chuva** (1 madeira + 1 sucata, 1 trabalho): D6 no amanhecer,
  4–5 = 2 água, 6 = 4 água, máximo 4. **Cozinha** (2 madeira + 1 sucata,
  2 trabalhos). **Armadilhas** (1 madeira, até 2): D6 no amanhecer, 5–6 = 1
  carne da reserva de caça, 1 = quebra. Obras EXP-BLD também aceitam
  trabalhadores.
- **Cão na viagem** (decisão do diretor, D-16): um cão apto pode acompanhar
  uma viagem automática: +1 no D6, −1 ponto por noite (come da viagem) e não
  come no abrigo enquanto estiver fora.
- **Travessia** (decisão do diretor, D-17): na chegada ao regional, todo
  herói com 3 de Vida fica com 2 (ninguém chega descansado). Ferimentos piores
  ficam como estão.
- **Moral da escassez** (decisão do diretor, D-17): depois da refeição, se
  algum humano ficou sem comida ou sem água, o Moral do abrigo cai 1; se todos
  comeram e beberam, sobe 1 (máximo 5). Cão sem porção não conta. Moral 0 é
  derrota parcial (regra já existente do abrigo).
- **Abrigo nunca vazio** (D-17): uma viagem automática que deixaria o abrigo
  sem nenhum humano é recusada.
- **Crescimento do abrigo** (decisão do diretor, D-20):
  - *Chegadas*: no amanhecer dos dias 4 e 10 role 1 D6 — 1–2: 1 adulto;
    3–4: 1 adulto e 1 criança; 5: 2 adultos; 6: ninguém. O grupo acolhe todos
    (precisa de cama: camas + 2 de lotação) ou recusa (Moral −1). Sem decisão
    no amanhecer, o grupo segue caminho (= recusa). Adulto acolhido sorteia
    profissão e rola bagagem.
  - *Terreno*: obras da Comunidade ocupam 1 de terreno (coletor, cozinha, cada
    canteiro), as EXP-BLD 2. **Cerca ampliada** (2 madeira, 2 trabalhos, até 2):
    +3 de terreno.
  - *Níveis*: **Depósito nível 2** (exige Depósito; 2 madeira + 1 sucata,
    2 trabalhos): +12 no depósito seco. **Alojamento nível 2** (exige
    Alojamento; 3 madeira + 1 sucata, 2 trabalhos): +4 camas. Níveis não ocupam
    terreno novo.
  - *Esforço*: toda obra paga materiais na largada e trabalhos (1 por
    trabalhador por dia, construtor 2) até ficar pronta.
- **Horta abandonada** (decisão do diretor, D-15): EXP-LOC-01 ganha o mapa
  tático `garden_edge_01` (campo aberto 4×4, buscas nas zonas 6 e 11,
  surgimento na 16, duas cercas de resistência 1). 3 buscas de 2 comida; na
  edição integral renova 1 busca a cada 2 noites. É a fonte tática de comida
  depois do Mercado.
- **Preparação** (decisão do diretor, D-18): **Normal** (padrão) ou
  **Acolhedor** — o abrigo regional já tem 1 canteiro pronto e o suprimento de
  evacuação é 2 rações por consumidor. Recomendado para a primeira partida e
  mesas que preferem ação a planejamento.
- **Van e combustível** (decisão do diretor, D-21; edição integral): de van
  conta a rota, não a caminhada — perto e médio são rota curta (1 trecho por
  sentido), longe é rota longa (2 trechos; RULES.md §5 l.29), a 2 combustíveis
  por trecho (§11 l.64). Voltar do Posto de van: 2. Instalação militar ida e
  volta: 8. O O2 do Posto é o **tanque do caminhão**: 1 PA, 6 combustível, uma
  vez por campanha (D-22; era 4). Saldo: 8 cartas + 6 do tanque − 2 da volta =
  12 no abrigo para os 8 da Instalação. A reserva experimental da Oficina (+8)
  continua fora do saldo legal.
- **Fim de campanha** (decisões do diretor, D-22; edição integral):
  - *Combustível largado*: numa emergência no Posto, o combustível da carga
    fica no chão do Posto — volta como cartas (as que tinham sido tiradas) e o
    resto volta ao tanque do caminhão.
  - *Manutenção de armas*: no amanhecer, herói no abrigo gasta 1 sucata e uma
    arma de mão volta à durabilidade máxima (1 por herói por dia).
  - *Defesa final*: acontece uma vez (vencida ou perdida); abre com rodada
    nova; quem está em viagem automática não defende; as ondas dependem de
    quantos heróis defendem (2: lento / corredor / 2 lentos; 3: 2 lentos /
    corredor / brutamontes; 4: 2 lentos / corredor + lento / brutamontes;
    5: 3 lentos / corredor + 2 lentos / brutamontes; 6: 4 lentos / corredor +
    2 lentos / brutamontes + lento).
- **Canteiro** (decisão do diretor, D-14; 2 madeira + 1 sucata, 2 trabalhos,
  até 2 por abrigo): produz 2 comida no dia em que um trabalhador cuida dele
  (agricultor +1). Não gasta o entorno: transforma trabalho em comida no meio
  de jogo.
- **Camas**: até 2 moradores além das camas (inclusive na migração); com o
  abrigo lotado ninguém recupera Vida pelo descanso (§25), a fadiga sim.
- **Recursos iniciais dos heróis**: na chegada ao regional, cada herói rola
  a tabela de bagagem uma vez. *Leitura do motor* (a Cisterna não muda):
  confirmar se é isso que o criador quis.

### Decisões do diretor (autonomia delegada pelo proprietário, 2026-10-30)

| Decisão | Escolha | Evidência |
|---|---|---|
| Heróis em viagens automáticas | Permitido; o herói perde a expedição tática do dia e não come no abrigo | 1–30: 8 → 11 sobrevivem com G |
| Suprimento de evacuação | 1 ração por consumidor na migração, uma vez (a Ponte entrega) | chegada média com 0,4 dia de comida; Colapso na 3ª noite |
| Rendimento e entorno | pesca/coleta 1 ponto por unidade; peixe e frutas até 12, +3/dia; Horta EXP-BLD-01 4/dia | 1–30: 7/53 → 34/53 (ciclos 3–5) |
| Abrigo lotado | Mantido: ninguém recupera Vida pelo descanso | simples de jogar; zera recusas de migração |
| Serraria e bancadas | Eliminadas: a Oficina (EXP-BLD-02) é a bancada; lenha vem das viagens | não acrescentam decisão nova no jogo físico |
| Defumador | Ideia futura | carne já dura 2 noites e vira 4 porções |
| Mapa tático de comida além do Mercado | Fila D-08 (conteúdo) | dias de Mercado já caem para ~12% |
| Escala por tamanho (D-17) | Travessia (Vida máx. 2 na chegada) + Moral da escassez; abrigo nunca vazio | 31–90: H2–H6 57–77% (antes 29–95%); fome nas sobreviventes 7,8% |
| Ameaça noturna por tamanho e limite de colapso | Rejeitados (testados no ciclo 9) | H6 seguia 88–93%; mais dados e vigias na mesa sem ganho |
| Fim de campanha (D-22) | combustível largado volta ao Posto; tanque 6; manutenção de arma (1 sucata); defesa única, rodada nova, ondas por defensores | defesa isolada com Vida 2: 60–88% por tamanho (antes 5–100%); campanhas de 25 dias: 38 vitórias em 191 |
| Van e combustível (D-21) | rota curta/longa de RULES §5; volta do Posto 2, Instalação 8; O2 do Posto = tanque do caminhão (4) | só cartas do Posto (8) não alcançavam a Instalação por nenhuma leitura documentada; com o tanque sobram 2 |
| Cartão de acesso caído (D-19) | fica no chão do local onde a expedição falhou; nova expedição ao local o recolhe com 1 PA de herói vivo numa zona de busca (mesma carga); sem nova busca; nunca duplica | lacuna de regra travava o controlador; 0 erros em 10.800 partidas depois |
| Horta abandonada (D-15) | mapa tático novo; renova 1 busca a cada 2 noites | todas as noites: sobreviventes confortáveis demais (T2 41%); a cada 2: T2 58–67%, descanso 65% → 44% |
| Preparação Acolhedor (D-18) | canteiro pronto + 2 rações/consumidor, opcional | grupo A de personas 16 → 31/53; B/C ≤ 74%; como padrão tiraria a pressão (T2 32%) |
| Crescimento do abrigo (D-20) | 2 chegadas (dias 4 e 10), recusa Moral −1; terreno para obras da Comunidade; cerca; níveis 2 de Depósito e Alojamento | acolher, recusar ou lotar dão 61–64% (31–90): dilema sem estratégia dominante; 4 chegadas derrubavam H6 a 26% |
| Acampamento em lotes (D-24) | grade 2×2 → 3×3 → 4×4 com símbolos por lote; fogueira e estoque na borda; expansão = obra pesada | modelo anterior não tinha espaço físico; 2×2 com núcleo ocupando lote travava grupos de 12 (46/53 sem expandir) |
| Horta unificada (D-25) | EXP-BLD-01, §61, protótipo D e canteiro viram lotes de horta: 2 lotes por pessoa (agricultor 4), 2 porções por lote, água só em dia sem chuva | 1 porção/lote rendia menos que pescar (40%); 2 porções: fome 5–11% |
| Crise 0–10 (D-26) | substitui o Moral da escassez; +1 até metade sem porção, +2 acima; −1/−2 servidos | +1/+2 a 1/4 dos humanos: 50%; +1 fixo: fome 13%; adotada: 59%, fome 10,9% |
| Ração de obra (D-26) | obra pesada: 1 porção por pessoa no dia | custa ~13 pontos de sobrevivência; mantida por ser pedido do proprietário e pesar decisão |
| Conhecimento (D-27) | 5 cartas, 1ª busca de cada local; liberam composteira, defumador, bancada, ambulatório, filtro | substitui as decisões antigas "Serraria e bancadas eliminadas" e "Defumador ideia futura": agora vêm de exploração, não de compra |
| Clareira por tamanho (D-17/D-24) | 9+ humanos chegam com o 3×3 aberto | 31–90: H6 32% → 71%, H5 47% → 57%, total 54% → 70%; limite 10 dava 67% |
| Prazo e apoio na defesa (D-23) | dia 25; Vigia e até 2 guardas atiram 1 por rodada | 1–30×2, 25 dias: vitórias 36 → 39/106 (37%), defesas vencidas 70%; nenhum tamanho < 25%; a Vigia só aparece em 11/106 campanhas |
| Colapso único (D-26) | em lotes, a Crise substitui o Colapso §25 de 3 noites | as duas regras faziam o mesmo papel; o §25 derrubava grupos com Crise 5–6 no dia 5–7 |
| Acolhedor em lotes (D-18/D-26) | clareira 3×3 + 2 lotes plantados + 2 rações | o canteiro único virava 1 lote sem cuidado e ocupava o último lote livre (50% < Normal); redefinido: 88%, fome 3,5% |
| Profissões (D-27) | pescador → caçador, lenhador → coletor (mesmas posições no baralho) | funções repetidas; nenhuma atividade ficou sem especialista |

## Acampamento em lotes (D-24..D-27, edição integral, 2026-10-30)

Liga com a Comunidade (`data/community.json#camp`, `camp.py`). Substitui, no
regional, terreno abstrato, camas 8, depósito único, canteiro, Horta §61 e
Moral da escassez. Painel e tabuleiro: `PAINEL_ACAMPAMENTO.md`.

1. **Lotes.** Tabuleiro 4×4; nível 1 abre 2×2, nível 2 abre 3×3 (Expansão: 3
   madeira, 3 trabalhos), nível 3 abre 4×4 (5 madeira + 2 metal, 5 trabalhos,
   exige Depósito, Oficina ou Vigia). Cada lote mostra 1–2 categorias (barraca,
   horta, água, estoque, oficina, defesa) e recebe uma construção ou até 2
   barracas. Obra reserva o lote ao começar. Grupo que chega com 9 ou mais
   humanos já encontra a clareira 3×3 aberta (mais braços limpam mais terra).
2. **Barracas e camas.** Barraca 2 lugares (2 madeira, 1 trabalho), barraca
   familiar 4 (só trazida por quem chega ou encontrada), Alojamento 8 (+4 no
   nível 2). A evacuação chega com 1 barraca para cada 2 humanos. Pode haver
   mais moradores que camas: só quem tem cama recupera Vida (cama vai primeiro
   a ferido); mais de 2 sem cama: Crise +1 por noite.
3. **Chegadas (dias 4 e 10, D6).** 1–2 adulto; 3–4 adulto + criança com
   barraca; 5 dois adultos + criança com barraca familiar; 6 ninguém. Acolher
   não exige cama; recusar: Crise +1.
4. **Estoque.** Comida 24 (+12 Depósito, +12 Depósito nível 2), água 24
   (+12 Reservatório), madeira 20, metal 20, cada um na sua trilha. O excedente
   da chegada é descartado e registrado.
5. **Horta por lotes.** Lote de horta: 1 trabalho, sem material; produz 3
   amanheceres depois. Função "horta": a pessoa cuida de 2 lotes prontos
   (agricultor 4). Cada lote cuidado e regado dá 2 porções. Tempo: um D6 por
   amanhecer, 4–6 chove; dia sem chuva gasta 1 água a cada 2 lotes cuidados.
   D6 = 1 da pessoa: praga, −1 porção. A Horta da Cisterna chega como 2 lotes
   plantados. Preparação Acolhedor (opcional): clareira já 3×3, 2 lotes de
   horta plantados e 2 rações por consumidor.
6. **Crise 0–10.** Depois da refeição: humano sem comida ou água → +1 se
   falta para até metade dos humanos, +2 se mais; todos servidos → −1, ou −2
   se o estoque ainda cobre outra noite. 4–6 moderada: obras pesadas param.
   7–9 grave: ninguém recupera Vida; no amanhecer D6 ≤ 2 perde 1 madeira ou
   metal. 10: colapso (derrota parcial). Cão não conta. Em lotes, a Crise é o
   único colapso coletivo: o Colapso §25 (1/4 dos humanos 3 noites sem comer)
   não se aplica; a 2ª noite seguida sem porção ainda fere a pessoa.
7. **Ração de obra.** Obra pesada (expansões, Depósito, Oficina, Enfermaria,
   Vigia, Reservatório, Alojamento e níveis 2) consome 1 porção por pessoa
   trabalhando no dia; sem porção no estoque, não se trabalha nela.
8. **Conhecimento.** A primeira busca bem-sucedida em cada local dá a sua
   carta: Horta abandonada → composteira (+1 porção por pessoa na horta);
   Mercado → defumador (carne dura +3 noites, cozinha sem madeira); Oficina →
   bancada (+1 trabalho por pessoa em obra); Hospital → ambulatório (exige
   Enfermaria: +1 pessoa nos cuidados; função "remédio": 2 porções → 1 remédio,
   enfermeiro sempre, outros com D6 ≥ 4); Estação → filtro de areia (água bruta
   sem ferver).
9. **Prazo e defesa (D-23).** Depois do dia 25 a frequência cala: a defesa
   final deixa de estar disponível e a campanha não pode mais ser vencida. Na
   defesa final, antes dos inimigos andarem, a Vigia (se construída) e até 2
   guardas aptos que ficaram no acampamento causam 1 de dano cada no inimigo
   mais próximo.
10. **Profissões.** Caçador (caça e pesca), Agricultor, Coletor (coleta, água,
   lenha), Cozinheiro, Carpinteiro, Mecânico, Enfermeiro, Guarda, comum. Sem
   especialista, a função funciona com menos rendimento.

## Ainda sem regra aprovada (não decidir silenciosamente)



- *Resolvido na edição integral (Comunidade):* economia de comida regional
  (viagens, canteiro, Horta abandonada com mapa — D-15), camas na migração
  (lotação +2) e fome em rodízio (Moral da escassez — D-17). Sem a Comunidade o
  comportamento certificado continua o descrito em `HORTA_CONTINUITY.md`.
- Pista coletada antes de emergência local/de estrada é mantida (comportamento
  atual do motor: pista não é carga). Confirmar se as anotações físicas deveriam
  ser perdidas como carga.

- Combustível regional: *resolvido na edição integral* (D-21, acima). Sem a
  Comunidade o protótipo certificado mantém `far=3` → 12 (`TACTICAL_FUEL_AUDIT.md`).
- Ferragens na ida diz que o Material fica no chão de Z1 e pode ser coletado por
  1 PA; o motor hoje só descarta. Pendente de implementação/decisão.
- Narrativa do segundo arco: local/contato de Célia e ordem das pistas são
  provisórios (`NARRATIVE_DEPENDENCIES.md`).
