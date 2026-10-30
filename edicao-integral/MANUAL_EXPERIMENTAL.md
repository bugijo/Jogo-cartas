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
