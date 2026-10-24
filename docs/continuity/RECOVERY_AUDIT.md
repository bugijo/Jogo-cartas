# Auditoria de recuperação histórica

Data: 2026-10-24  
Branch: `evolucao/zona-zero-sistema-v1`  
Base conferida local e remotamente: `94b6e7c7a397fb009d733d95af825c53a5728cee`

## História conferida

Os oito commits indicados existem e são ancestrais da base. O revert posterior
`9773da5` removeu suas implementações da árvore, mas não do histórico:

| Commit | Área histórica | Decisão de recuperação |
| --- | --- | --- |
| `1e7b81f` | Emboscada M1 | Recuperada e adaptada ao baralho atual de Hordas. |
| `2e7c725` | Viagem + M1 | Recuperada seletivamente; preservado um único estado persistente. |
| `d6acc24` | Movimento/portas e ferimentos persistentes | Recuperada em `Tactical02`; referências do baralho adaptadas. |
| `b399d41` | Persistência e correções de combate | Recuperada com save/load integrado e testes focados. |
| `06b03f4` | Validação/reembaralhamento | Recuperada para os baralhos únicos de campanha. |
| `9aeb935` | Liquidação do retorno | Recuperada; liquidação valida carga, recibos e carta efetivamente revelada. |
| `7787e48` | Certificado legal da Cisterna | Recuperado com recibos/objetivos e filtro; continua bloqueado sem prova tática integral. |
| `49cb7cc` | Checkpoints/quality gates | Conteúdo reconciliado nos arquivos de continuidade atuais, sem restaurar checkpoint obsoleto. |

Não foi feito cherry-pick em massa. A implementação histórica mantinha um
`TravelShoe02` independente e campos top-level de Horda/Viagem em paralelo aos
baralhos recentes de `Cistern02`; essas duplicações foram descartadas. A
Emboscada, viagem, tática e integração agora sincronizam os baralhos únicos de
campanha. O formato antigo de snapshot da Horda é migrado para o formato atual.

## Recuperado nesta unidade

- Cartas por trecho de Viagem, custos no relógio, ocorrências noturnas, efeitos
  de rota, escolhas e Emboscada M1 com movimento, portas, ataque, inimigos,
  hordas, munição, fadiga, ferimentos e retorno.
- Reaproveitamento tático de recursos/equipamentos, transporte e liquidação
  idempotente no retorno, além dos eventos diários, fila de cercos, ponte e
  recibos do capítulo.
- Migração de saves de Horda/Viagem e auditoria de saves antigos sem cursor de
  eventos. Saves sem eventos registram a lacuna histórica, aplicam apenas o
  evento do dia atual e não podem receber certificado canônico; efeitos
  passados não são inventados nem retroativamente afirmados.
- O replay fixo de cinco dias voltou a passar para H2–H6 ao parar de aplicar
  manualmente as pressões já causadas pelas cartas de evento e ao usar o cerco
  do terceiro dia vindo do próprio evento. É uma trajetória roteirizada, não
  uma campanha legal integral nem evidência de equilíbrio.

## Testes e limites observados

Na árvore desta recuperação: `python -m unittest discover -s
edicao-integral/tests -q` — 220 testes passaram; `validate_data.py`,
`compileall` e `git diff --check` passaram. Os conjuntos focados de viagem,
M1, tática e integração também passaram durante a implementação.

Isso não certifica campanha completa. A rota pública de expedição ainda exige
Viagem, mas a ligação de recibos a todos os objetivos, trabalho civil,
promessas/resgates em todos os casos e um replay legal completo de cinco dias
continuam pendentes. A emissão de `verified_victory` segue protegida e não foi
demonstrada nesta unidade. Migração para Última Transmissão e campanha contínua
também não foram demonstradas.

Impressão física, playtest humano e equilíbrio seguem pendentes. Saves JSON
editáveis pelo proprietário não têm proteção criptográfica: validação detecta
inconsistências, mas não autentica autoria.

## Próximo bloqueio concreto

Produzir um executor de expedições legais que atravesse Viagem, M1 quando
disparada, mapa tático, recibos de peça/suprimento/resgate e retorno, sem usar
`_start_tactical_fixture`, `receive_part`, mutação direta de recursos ou flags
de objetivo. Esse caminho deve alimentar o capítulo canônico de cinco dias e
ser a única origem dos recibos aceitos por `complete_cistern()`.
