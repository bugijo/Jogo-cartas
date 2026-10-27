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
- Emboscada (`ZC-VIA-0005`) fica pendente e bloqueia a viagem: **o combate de
  emboscada regional ainda não está ligado** (próximo bloqueio).

## Ainda sem regra aprovada (não decidir silenciosamente)

- Combustível regional: `far=3` com 2/trecho exige 12; `EXP-MIS-104` cobra 6;
  Posto O2 não declara combustível. Ver `TACTICAL_FUEL_AUDIT.md`.
- Ferragens na ida diz que o Material fica no chão de Z1 e pode ser coletado por
  1 PA; o motor hoje só descarta. Pendente de implementação/decisão.
- Narrativa do segundo arco: local/contato de Célia e ordem das pistas são
  provisórios (`NARRATIVE_DEPENDENCIES.md`).
