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

## Ainda sem regra aprovada (não decidir silenciosamente)



- Economia de comida regional: só o Mercado tem mapa tático e comida (4 buscas
  × 2). Horta H1 implementada, mas dois bloqueios dependem de decisão
  (`HORTA_CONTINUITY.md`): (1) os 3 acolhidos excedem as camas regionais e a
  migração é recusada (opções em `HORTA_CONTINUITY.md`); (2) depósito cheio:
  resolvido pelo descarte voluntário acima.
- Fome em rodízio (balanceamento, não bug): pela RULES l.49 o ferimento só vem
  na 2ª noite seguida de privação; comendo em noites alternadas a sequência fica
  em 1. Assim 4 comida/dia sustentam 10–11 consumidores por 15 dias com 6–7
  porções faltando toda noite. Avaliar se a sobrevivência regional deve exigir
  mais que isso.
- Pista coletada antes de emergência local/de estrada é mantida (comportamento
  atual do motor: pista não é carga). Confirmar se as anotações físicas deveriam
  ser perdidas como carga.

- Combustível regional: `far=3` com 2/trecho exige 12; `EXP-MIS-104` cobra 6;
  Posto O2 não declara combustível. Ver `TACTICAL_FUEL_AUDIT.md`.
- Ferragens na ida diz que o Material fica no chão de Z1 e pode ser coletado por
  1 PA; o motor hoje só descarta. Pendente de implementação/decisão.
- Narrativa do segundo arco: local/contato de Célia e ordem das pistas são
  provisórios (`NARRATIVE_DEPENDENCIES.md`).
