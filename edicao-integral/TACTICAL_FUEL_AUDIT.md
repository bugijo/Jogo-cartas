# Auditoria independente: expedição 0.2, Posto e transição

## Auditoria regional de combustível e veículo — 2026-10-29

Sem alteração de custos, sem abastecimento novo. Estado do motor no HEAD
`144144f`; medição sobre as 52 vitórias da Cisterna (H2–H6, sementes 1–30).

### Cadeia até a Instalação militar (`EXP-LOC-06`)

| Passo | Motor regional | Situação |
|---|---|---|
| Migração: combustível | `fuel = nº de cartas físicas da Cisterna` | **0 em 52/52** (o controlador da Cisterna não visita o Posto). |
| Migração: van | `vehicle_archived = van_state`; `world.vehicles` fica vazio | `abandoned` em 52/52. **Lacuna:** uma van 0.2 operacional seria só arquivada (não vira veículo regional). |
| Bateria | Oficina `medium=2`, `pickup_unique_item` 1 PA na zona 7 | Volta como carga única; Emboscada com emergência e carga única → `NotImplementedError` (não modelado). |
| Posto: combustível | 8 cartas, 1 PA cada, zona 7 (O1), finitas | Única fonte canônica: **8**. |
| Posto: van | inspeção 1 PA; reparo 2 PA + Bateria + d6+Técnica ≥ 6, uma tentativa por herói/visita | 11 PA no total com as cartas; cabe em ~4 rodadas com 3 PA/herói, sujeito ao relógio. |
| Retorno de van | cobra `segment_cost × 2 = 4` da carga | **Diverge** de CAMPAIGN (voltar do Posto custa 2). |
| Militar | `open_expedition` cobra `2 × 3 × 2 = 12` do estoque; exige rádio, cartão, acesso | `far=3` e 12 são hipóteses experimentais (`EXP-MIS-104`). |
| Controlador | recusa `vehicle_id` na ida; aceita voltar de van do Posto | Ida de veículo + cartas de Viagem com veículo não modeladas (emergência de estrada recusa). |
| Furgão `EXP-VEI-01` | `recover_vehicle` na Oficina, 1 por trecho | Sem fonte canônica (dado experimental). Não usar sem aprovação. |
| Reserva da Oficina (+8) | `salvage_fuel_cache` | Conteúdo **criado nesta branch**, não canônico. Tratado aqui como abastecimento artificial: fora do saldo legal. |

### Saldo com fontes canônicas apenas (sem reserva da Oficina)

| Leitura do retorno do Posto | Sobra após voltar | Militar 12 (`far=3`) | Militar 8 (rota longa §5) |
|---|---:|---:|---:|
| Motor atual (`medium=2` → 4) | 4 | falta 8 | falta 4 |
| CAMPAIGN (voltar custa 2) | 6 | falta 6 | falta 2 |

Conclusão: **sem a reserva experimental, nenhuma leitura documentada alcança a
Instalação militar.** Com a reserva, o motor fecha em exatamente 12 (margem 0).

### Decisões pendentes (não decididas aqui)
1. Custo do retorno de van do Posto no regional: 4 (motor) ou 2 (CAMPAIGN).
2. Distância/custo militar: `far=3` → 12, ou rota longa §5 → 8.
3. Manter, retirar ou aprovar a reserva experimental da Oficina (+8).
4. Projeção da van 0.2 operacional na migração (hoje se perde).
5. Emergência de estrada com veículo ou carga única (Bateria, cartão).
6. Ida de veículo com cartas de Viagem regionais.

## Estado corrigido do texto canônico (2026-10-26)

`RULES.md §11, linha 64` define a van a **2 combustíveis por trecho**;
`RULES.md §5, linha 29` define rota curta como 1 trecho por sentido e longa
como 2 por sentido. A menção “ir a pé ao Posto e voltar na van custa dois” em
`CAMPAIGN.md` é a rota curta explicitamente descrita. “§64” usado em mensagens
anteriores é uma referência de linha, não o número da seção. Corrigem-se abaixo
as citações anteriores que diziam que §64 não existia ou atribuíam a regra a
§11 sem o número de linha.

`data/last_transmission.json` mantém, como hipótese **experimental**, o custo
militar 12: distância regional `far=3` × ida/volta × 2 por trecho. Isso aplica
o custo canônico à distância regional do protótipo, cuja equivalência com rota
curta/longa de 0.2 ainda não está definida. O O2 do Posto continua sem
combustível explícito.

## Atualização ativa — hipótese experimental da branch em 2026-10-26

As fontes canônicas continuam inalteradas: a regra real é `RULES.md` §11,
linha 64 (2 combustíveis por trecho), e a edição 0.2 diz que ir a pé ao Posto
e voltar na van curta custa 2. O O2 do Posto continua sem quantidade de
combustível: “um lote de cada provisão” não cria combustível.

A configuração de teste adiciona **uma única reserva experimental de 8 unidades**
no O1 da Oficina, zona 14, custo de 2 PA, ruído 3, uma retirada, carregada na
expedição; só entra no estoque depois de retorno normal e é perdida em retirada
de emergência. Não é regra canônica nem componente aprovado para o kit 0.2.
H2 seed 22 e oito políticas determinísticas retornaram essa expedição pela API
pública e entregaram 8 ao estoque regional (um teste de viabilidade dessa rota,
sem campanha contínua completa).

A conta regional experimental para esse combustível é:

| Etapa | Unidades | Base |
|---|---:|---|
| Reserva experimental Oficina | +8 | conteúdo de teste criado nesta branch; não existe na fonte canônica |
| Posto O1 | +8 | oito cartas físicas, 1 PA cada, finitas |
| Retorno Posto em van | −4 | mapa regional `medium=2` × 2 unidades/trecho; **diverge** do texto 0.2 que fixa 2 para voltar do Posto |
| Total para a rota militar | 12 | 8+8−4 |
| Acesso militar regional `far=3` | −12 | 3 segmentos por sentido × 2 sentidos × 2 unidades/trecho |

O número 12 está agora em `EXP-MIS-104`/`regional_fuel_rule` somente como
**conciliação experimental** que respeita 2/segmento e o mapa regional; não
substitui regra oficial. A premissa de −4 depende da interpretação `medium=2`;
com o custo canônico explícito de retorno 2, seriam 14 disponíveis e sobrariam
2 após pagar 12. Não existe resultado de replay que já prove essa sequência
integral: pistas/Estação bloqueiam a campanha primeiro. Bônus de viagem e
motorista também podem reduzir segmentos reais debitados pelo motor; `12` é o
requisito-base sem esses bônus, não afirma que todo trajeto modificado debita
12.

Fontes renováveis/alternativas: nenhuma regra canônica encontrada. A reserva da
Oficina é a única fonte nova deste experimento, deliberadamente identificada e
limitada. O segundo arco ainda não tem custo de combustível aprovado para
impressão/distribuição.

## Matriz documental atualizada — checkout verificado em `438beb9`

| Fonte / autoridade | Regra ou dado explícito | Consequência de combustível |
| --- | --- | --- |
| `RULES.md` §5, regra canônica 0.2 | Rota curta: 1 trecho de ida e 1 de volta; longa: 2+2. Cada trecho ocupa um segmento; combustível de veículo é adicional. | Ida e volta completas: 2 segmentos curtos ou 4 longos. |
| `RULES.md` §11, linha 64, regra canônica 0.2 | Van `EXP-VEI-02` consome 2 Combustíveis por trecho; é permitido ir ao Posto a pé e voltar na van por 2. | O retorno explícito do Posto em van curta custa 2; viagem completa curta custa 4 e longa canônica custa 8. |
| `CAMPAIGN.md`, Dia 4 | Posto O1 oferece oito cartas únicas de Combustível, 1 PA cada, sem reposição. | Máximo explícito O1 = 8 unidades. Se todas forem retiradas e trazidas, o retorno curto autorizado consome 2 e deixa até 6. |
| `content/catalog.json`, missão `ZC-MIS-0004` | O1: oito Combustíveis; O2: “um lote de cada provisão”. | Confirma O1=8; O2 contém um lote de cada tipo de provisão definido no capítulo, não combustível. |
| `CAMPAIGN.md`, definição geral de lote | Lote de provisão é recompensa única em carta com quatro porções; os tipos são Conserva e Água, organizados em O1/O2 salvo exceção explícita. | O2 significa um lote de comida e um de água; não autoriza combustível. |
| `data/last_transmission.json`, missão experimental `EXP-MIS-104` | Exige e cobra `fuel_round_trip: 12`, com base `2 × 3 × 2`. | Hipótese experimental explícita; o texto oficial §11, linha 64, permanece 2 por trecho e a equivalência regional `far=3` não foi aprovada para edição final. |
| `data/system.json`, geografia regional experimental | `EXP-LOC-06` é `far=3`; `EXP-VEI-02` custa 2 por segmento. | Leitura do motor: 3 segmentos por sentido × 2 sentidos × 2 = 12. Não existe equivalência aprovada entre `far=3` e rota longa canônica de 2 trechos. |
| `data/system.json`, Posto e conteúdo regional | Posto `medium=2`; oito cartas de combustível finitas. | Retorno regional de van custa 4 no protótipo se percorrer os 2 segmentos; `CAMPAIGN.md` especifica um retorno curto de 1 trecho e custo 2. O mapeamento do local à rota canônica não foi definido. |
| Catálogo de Saque, campanha e estruturas | Nenhuma carta de Saque ou estrutura produz combustível; reservatório consome combustível. | Nenhuma fonte renovável ou alternativa legal foi localizada. |

### Contas verificáveis e propostas ainda não aprovadas

| Interpretação | Retorno do Posto em van | Posto O1 restante (não inclui Oficina) | Custo militar | Déficit sem cache Oficina | Saldo após cache experimental + missão |
| --- | ---: | ---: | ---: | ---: | ---: |
| Regra explícita `CAMPAIGN.md`: volta curta | 2 | 6 | 12 (`far=3` experimental) | 6 | 2 |
| Retorno regional `medium=2` no protótipo | 4 | 4 | 12 (`far=3` experimental) | 8 | 0 |
| Regra explícita `CAMPAIGN.md`: volta curta | 2 | 6 | 8 (se militar mapear a rota longa §5) | 2 | 6 |
| Retorno regional `medium=2` no protótipo | 4 | 4 | 8 (se militar mapear a rota longa §5) | 4 | 4 |
| Regra explícita `CAMPAIGN.md`: volta curta | 2 | 6 | 6 (custo fixo experimental) | 0 | 8 |
| Retorno regional `medium=2` no protótipo | 4 | 4 | 6 (custo fixo experimental) | 2 | 6 |

“Déficit sem cache Oficina” compara somente as oito unidades explícitas do
Posto O1 com o custo da missão; “saldo após cache” inclui as oito unidades
experimentais da Oficina e o retorno indicado. Esses saldos são aritmética de
hipóteses, não uma rota já executada.

O2 tem comida e água, não combustível. A regra canônica explícita deixa até 6 unidades após voltar ao Posto por van na rota curta; o protótipo regional `medium=2` debita 4 e deixa 4. A reserva experimental da Oficina (8) produz 12 após esse retorno médio e paga o custo experimental 12 exatamente; se aplicar a volta curta de 2, o saldo seria 14. Decisões de produto continuam pendentes: (a) mapear `perto/médio/longe` às rotas curtas/longas; (b) aprovar ou rejeitar a reserva experimental de 8; (c) definir se requisito 12 é fixo ou varia com bônus legais de motorista/viagem. Essa hipótese não foi declarada definitiva, e a Estação/rádio bloqueia a campanha antes do Posto.

### Propostas para decisão do proprietário (nenhuma aplicada)

| Proposta | Resultado matemático no conteúdo conhecido | Consequência |
| --- | --- | --- |
| Manter 2/unidade por trecho e `far=3` (3 trechos por sentido) | 12 para ida/volta; cenário experimental de retorno médio deixa 4 das 8 unidades do Posto | O estoque regional conhecido no replay é 7 (3 da Oficina + 4 após retorno); déficit 5. Não é um replay integral nem resolve o mapeamento canônico de rota. |
| Mapear a viagem militar a rota longa canônica (2 trechos/sentido) e manter 2/unidade/trecho | 8; o replay após retorno regional médio tem 7 e fica 1 curto. Pela regra explícita de retorno curto do Posto a pé/van, as 8 do Posto deixariam 6; somadas às 3 unidades que o catálogo experimental oferece na Oficina, seriam 9, se legalmente obtidas e preservadas. | Exige definir equivalência de distâncias e rota de retorno, não só trocar o número em uma missão. |
| Tratar os 6 de `EXP-MIS-104` como custo total especial | 6; o saldo de replay 7 paga e sobra 1. | Fecha a missão experimental, mas contradiz 2 por trecho em `RULES.md` §11 quando aplicada à viagem `far=3`. |
| Acrescentar combustível explícito a O2 | Quantidade ainda precisaria ser escolhida. Para a rota `far=3`, o estoque após o retorno médio é 7; seriam necessárias pelo menos 5 unidades adicionais, sem outros gastos. | Cria uma recompensa de combustível que não está no texto atual e precisa alterar campanha, catálogo, componentes e testes. |
| Reserva de Oficina experimental (configuração de teste atual) | 8+8−4=12 sob retorno regional `medium=2`; se a regra 0.2 de retorno custa 2, então 14−12=2 restantes. | Testa uma fonte limitada por risco/tempo, mas exige aprovação explícita e não resolve a expedição da Estação nem comprova campanha integral. |
| Não alterar regras nem oferta; manter gate fechado | Nenhuma concessão. | Honestidade atual: não há campanha completa certificável. |

> **Snapshot histórico da branch `8700073`.** Esta auditoria antecede a
> migração do baralho de Viagem para o estado regional e o replay H2
> `verified_victory`. A revelação/resolução das cartas ainda não está integrada
> em expedições regionais.
> Use `CAMPAIGN_INTEGRATION.md` para o estado atual. As diferenças de Posto,
> combustível e migração entre modelos continuam pertinentes; alegações abaixo
> de que nenhuma expedição ou certificado legal existe estão supersedidas.

Base examinada: `RULES.md`, `CAMPAIGN.md`, `content/catalog.json`, `cistern02.py`, `integrated_campaign.py`, `system.py`, `arc2.py`, `data/tactics.json` e `data/system.json`, com a branch em `8700073`. Este relatório descreve paridade de regras; não certifica uma campanha jogada.

## Contrato canônico que a expedição precisa demonstrar

| Operação | Regra 0.2 e efeito verificável |
| --- | --- |
| Escolha e relógio | Uma expedição por dia; rota curta 1+1 segmentos, longa 2+2; cada trecho compra Viagem. Cada rodada local, inclusive a primeira e uma emboscada, custa um segmento de um relógio **comum de dez**. Segmentos 9–10 causam fadiga; noite acrescenta Horda, viagem noturna acrescenta Viagem sem segmento. `RULES.md`, seção 5. |
| Ações | Cada herói recebe em geral 3 PA por rodada, reduzidos por Fome, Sede e fadiga. Mover por conector 1 PA; abrir porta comum 1; bloqueada 2 com ferramenta; atacar, buscar, transferir e interagir em geral 1. Saída de zona ocupada custa +1. Testes usam d6+atributo, 1 natural falha, 6 natural vence. `RULES.md`, seções 3, 5 e 6. |
| Mapa | Cada um dos seis destinos usa 16 zonas e 21 conectores; entrada/saída Z1, surgimento Z16, B1 Z5, B2 Z12, O1 Z7, O2 Z14. Há cinco portas. O bloqueio varia: Mercado/Hospital 7–8; Oficina 3–7; Posto nenhum; Condomínio 9–13; Estação 7–8 e 13–14. `CAMPAIGN.md`, Preparação; `data/tactics.json` mantém essas plantas e marca Posto/Condomínio somente `reference_only`. |
| Busca e carga | B1/B2 têm 3 usos cada durante toda a campanha; Saque não se repõe. Cada herói leva 4 cargas, incluindo arma/cartas; transferir custa 1 PA por item. Peças, lotes e equipamentos dos objetivos são retirados separadamente, não são gerados por Saque. Só o que volta fisicamente pela saída entra no abrigo; emergência perde carga obtida e deixa as quatro peças únicas no chão para outra visita. `RULES.md`, seções 5 e 7; `CAMPAIGN.md`, Preparação. |
| Peças do filtro | Oficina O1: Conexões 1 carga, 1 PA sem teste; Estação O1: Bomba 2 cargas, 2 PA + Técnica 6, uma tentativa/herói/visita e falha +1 Pressão externa; Estação O2: Membrana 1 carga, 1 PA. Cada peça precisa ser transportada e entregue. Custos e trabalho A/B/C só podem reservar achado do dia seguinte. `CAMPAIGN.md`, Dias 2–4 e Construção. |
| Resgate | Contato em zona do encontro custa 1 PA; acolher e transportar grupo inteiro, respeitando vagas/duas temporárias, antecede intenção. Crianças acompanham responsáveis; nenhuma pessoa aparece no abrigo só por passar tempo. `RULES.md`, seção 9; `CAMPAIGN.md`, Preparação e destinos. |
| Combate e saída | Ataque paga PA/munição e testa atributo contra Defesa; inimigos atacam ou movem depois dos heróis e surgem em S. Saída só após rodada terminada, todos os humanos/escoltas em Z1 e nenhum inimigo ali; retorno exige segmentos restantes. `RULES.md`, seções 5–6. |

O JSON de geometria preserva os pares de zonas acima, mas sua propriedade `resistance` 2/3 pertence ao motor **experimental**. O texto canônico mede abertura em PA e ferramenta, não por pontos de resistência. Porta comum/porta bloqueada não devem ganhar durabilidade por conversão implícita.

## Posto e combustível

`CAMPAIGN.md`, Dia 4, oferece **oito cartas de Combustível, cada uma retirada por 1 PA em O1**, estoque finito, e van no mesmo objetivo. Inspecionar a van custa 1 PA. `RULES.md`, seção 11, exige Bateria da Oficina e recuperação no Posto por **2 PA + Técnica 6**; peça e custo só se consomem no sucesso. A van tem seis lugares humanos, doze cargas e reserva para um cão; custa **2 Combustíveis por trecho**. Ir a pé até o Posto não gasta combustível; voltar na van custa dois. Excedentes caminham, sem criar lugares. Recuperação da van não é requisito de vitória da Cisterna. O capítulo não define automaticamente o combustível da instalação militar experimental.

No motor experimental, `data/system.json` só concede até 3 combustíveis em buscas urbanas da Oficina (3 buscas × 1); não há local regional Posto. `data/tactics.json` inclui `gas_station_02`, mas `reference_only`, sem expedição correspondente. `system.py::recover_vehicle` limita recuperação a `EXP-LOC-03`/Oficina e debita combustível do **estoque do abrigo**, apesar de o herói estar fora. `EXP-VEI-01` tem 4 lugares e custa 1 por segmento, não a especificação da van 0.2. A rota militar pede 6 unidades ida+volta nas constantes atuais. Essas diferenças precisam de migração explícita; simplesmente somar oito ao `stock` equivaleria a injeção.

## Lacunas e falso positivo atual

1. `integrated_campaign.py::collect_part()` recebe o nome da peça como argumento, debita apenas 2 segmentos e chama `receive_part()`. Não exige expedição aberta, destino correto, entrada, posição O1/O2, PA, teste da Bomba, capacidade, saída nem transporte. Seus IDs `EXP-LOC-01/03/04` não correspondem respectivamente a Oficina/Estação/Estação no catálogo experimental; são Horta, Oficina e Hospital. Portanto `collect_part()` não prova coleta legal. A docstring “sem aceitar injeção” é enganosa.
2. `tests/test_integrated_campaign.py::prepared()` adiciona três cartas de quatro porções de comida e de água diretamente às listas antes de obter peças. Este teste é útil para a interface de salvamento, mas não prova economia nem partida completa.
3. `complete_cistern()` aceita `candidate_victory`, constrói `World.new()` com somente fundadores e comida/água truncadas por `min(...,30)`, define `cistern_complete` e duas pistas. Não transfere ferimentos, fadiga, XP, vínculos, civis, crianças, cães, moral, estruturas, equipamento, van nem peças. Os fundadores 0.2 incluem Téo/Célia, ausentes dos dez protagonistas experimentais. A capacidade experimental não torna legítimo descartar porções sem registro.
4. `arc2.py` e `system.py` requerem `cistern_record={status: verified_victory, source: cistern02}`; `complete_cistern()` não o emite. A transição superficial não abre realmente código/instalação. Não relaxar esse portão para corrigir o teste.
5. `cistern02.py::rescue()` e `receive_part()` são entradas administrativas ainda sem prova tática. As intenções/cercos parcialmente implementados não recebem todo o estado da expedição nem as decisões de planejamento. `Cistern02.close_chapter()` anuncia honestamente apenas `candidate_victory`.

## Provas mínimas reproduzíveis recomendadas

- **Peça:** iniciar dia 2 a pé; abrir uma única expedição à Oficina; gastar trecho e rodadas; alcançar Z7 por conectores e portas pagando PA; retirar Conexões 1 PA, alocar 1 carga; voltar a Z1, resolver inimigos, fazer trecho de retorno e só então marcar `parts['Conexões']=2`. Testes negativos: objetivo sem presença/PA; lotação; emergência; revisita com peça no chão; resgate ainda no mapa. Repetir na Estação para Bomba (teste falho e bem-sucedido com sementes fixas, custo 2 PA, 2 cargas, Pressão na falha) e Membrana.
- **Posto:** visitar a pé, inspecionar, buscar Bateria na Oficina e trazê-la antes, retirar legalmente cartas de Combustível no O1, testar falha/sucesso de Técnica, pagar 2 unidades **da carga presente** para voltar com van, registrar saldo conservado. Demonstrar que um recurso buscado mas abandonado na emergência não financia a recuperação.
- **Arcos:** uma campanha de cinco dias sem alterações diretas em `food`, `water`, `parts`, `stock`, flags ou certificado; fechar filtro com A/B/C, refeições/cercos/intenções em ordem; emitir certificado apenas de log completo auditável; migrar todo estado relevante; conseguir rádio/cartão/combustível, buscar transmissor e defender três ondas. Um teste que só cria fixture sintética deve ser rotulado como unitário, não campanha legal.

## Decisões de design ainda abertas

- Como reconciliar os doze fundadores da edição 0.2 (inclusive Téo/Célia) com dez protagonistas da nova edição, sem perda de identidade ou restrição oculta.
- Como mapear a van 0.2 (6 lugares, custo 2/trecho) à `EXP-VEI-01` experimental (4 lugares, custo 1/segmento), inclusive o combustível de ida/volta do segundo arco; Posto deve continuar um destino próprio.
- Como conservar porções acima da capacidade experimental sem criar nem apagar recurso e como migrar civis, cães, condições, projetos, promessas e danos.
- Se e quando uma vitória da Cisterna deve gerar pistas de rádio; o `clues=2` automático atual não está demonstrado por ação canônica.

Nenhuma dessas escolhas foi aplicada nesta auditoria. PDFs, cartas e regras oficiais não foram modificados; impressão física e playtest humano continuam não realizados.
