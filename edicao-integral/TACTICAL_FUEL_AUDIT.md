# Auditoria independente: expedição 0.2, Posto e transição

## Matriz documental atualizada — base remota `d3d6137` e rechecagem nesta execução

**Referência §64 não existe na cópia atual de `RULES.md`.** O manual contém
§§1–14; o custo da van está em §11 (“Veículo”), e os comprimentos de rota em §5.
Quando o pedido cita §64, esta auditoria registra a divergência e usa o texto
real de §11, sem inferir um documento ausente.

| Fonte / autoridade | Regra ou dado explícito | Consequência de combustível |
| --- | --- | --- |
| `RULES.md` §5, regra canônica 0.2 | Rota curta: 1 trecho de ida e 1 de volta; longa: 2+2. Cada trecho ocupa um segmento; combustível de veículo é adicional. | Ida e volta completas: 2 segmentos curtos ou 4 longos. |
| `RULES.md` §11, regra canônica 0.2 | Van `EXP-VEI-02` consome 2 Combustíveis por trecho; é permitido ir ao Posto a pé e voltar na van por 2. | O retorno explícito do Posto em van curta custa 2; viagem completa curta custa 4 e longa canônica custa 8. |
| `CAMPAIGN.md`, Dia 4 | Posto O1 oferece oito cartas únicas de Combustível, 1 PA cada, sem reposição. | Máximo explícito O1 = 8 unidades. Se todas forem retiradas e trazidas, o retorno curto autorizado consome 2 e deixa até 6. |
| `content/catalog.json`, missão `ZC-MIS-0004` | O1: oito Combustíveis; O2: “um lote de cada provisão”. | Confirma O1=8; não declara combustível ou quantidade em O2. |
| `CAMPAIGN.md`, definição geral de lote | Lote de provisão é recompensa única em carta com quatro porções; os tipos são Conserva e Água, organizados em O1/O2 salvo exceção explícita. | O2 significa provisões de comida e água; não autoriza combustível. |
| `data/last_transmission.json`, missão experimental `EXP-MIS-104` | Requer e cobra `fuel_round_trip: 6`. | Custo fixo experimental 6; não revoga a regra canônica nem define sua relação com segmentos. |
| `data/system.json`, geografia regional experimental | `EXP-LOC-06` é `far=3`; `EXP-VEI-02` custa 2 por segmento. | Leitura implementada: 3 segmentos por sentido × 2 sentidos × 2 = 12. Não existe equivalência aprovada entre `far=3` e rota longa canônica de 2 trechos. |
| `data/system.json`, Posto e conteúdo regional | Posto `medium=2`; oito usos para combustível e nenhum saque genérico. | O retorno experimental de 2 segmentos na van custa 4 e deixa 4 das oito unidades; essa equivalência ainda depende de decisão de produto. |
| Catálogo de Saque, campanha e estruturas | Nenhuma carta de Saque ou estrutura produz combustível; reservatório consome combustível. | Nenhuma fonte renovável ou alternativa legal foi localizada. |

### Contas verificáveis e propostas ainda não aprovadas

| Interpretação | Retorno do Posto em van | Máximo que sobra das 8 unidades | Ida e volta militar | Saldo após missão |
| --- | ---: | ---: | ---: | ---: |
| Regra canônica explícita: Posto a pé, retorno curto em van | 2 | 6 | — | — |
| Equivalência experimental Posto `medium=2` | 4 | 4 | — | — |
| Região `far=3` + custo §11 | — | 4 ou 6 conforme retorno adotado | 12 | déficit 6 ou 8 |
| Rota longa canônica §5 + custo §11 | — | 4 ou 6 conforme retorno adotado | 8 | déficit 2 ou 4 |
| Custo fixo experimental `EXP-MIS-104` | — | 4 ou 6 conforme retorno adotado | 6 | déficit 0 ou 2 |

Nenhuma fonte define O2 como combustível nem define quantidade adicional. A regra canônica explícita deixa até 6 unidades após retornar do Posto a pé/van em rota curta; o protótipo regional `medium=2` deixa 4. Isso torna `EXP-MIS-104` (custo 6) possível ou impossível antes de outras viagens, e `far=3` custa 12. Não foi escolhida interpretação nem adicionada oferta. Decisões de produto pendentes: (a) mapear as distâncias regionais perto/médio/longe às rotas curtas/longas canônicas; (b) definir se `EXP-MIS-104` é exceção de custo fixo e sua relação com consumo por trecho; (c) caso se pretenda combustível extra em O2, escrever quantidade e regra de retirada. O replay falha fechado até a aprovação dessa interpretação. A única alteração de dados feita anteriormente foi retirar a concessão experimental não respaldada da Oficina.

### Propostas para decisão do proprietário (nenhuma aplicada)

| Proposta | Resultado matemático no conteúdo conhecido | Consequência |
| --- | --- | --- |
| Manter 2/unidade por trecho e `far=3` (3 trechos por sentido) | 12 para ida/volta; o replay regional atual termina o Posto com 7 (3 da Oficina + 4 após retorno médio) | Campanha fica bloqueada por déficit 5; mantém literalmente o motor atual. |
| Mapear a viagem militar a rota longa canônica (2 trechos/sentido) e manter 2/unidade/trecho | 8; o replay após retorno regional médio tem 7 e fica 1 curto. Pela regra explícita de retorno curto do Posto a pé/van, as 8 do Posto deixariam 6; somadas às 3 unidades que o catálogo experimental oferece na Oficina, seriam 9, se legalmente obtidas e preservadas. | Exige definir equivalência de distâncias e rota de retorno, não só trocar o número em uma missão. |
| Tratar os 6 de `EXP-MIS-104` como custo total especial | 6; o saldo de replay 7 paga e sobra 1. | Fecha a missão experimental, mas contradiz 2 por trecho em `RULES.md` §11 quando aplicada à viagem `far=3`. |
| Acrescentar combustível explícito a O2 | Quantidade ainda precisaria ser escolhida. Para a rota `far=3`, o estoque após o retorno médio é 7; seriam necessárias pelo menos 5 unidades adicionais, sem outros gastos. | Cria uma recompensa de combustível que não está no texto atual e precisa alterar campanha, catálogo, componentes e testes. |
| Não alterar regras nem oferta; manter gate fechado | Nenhuma concessão. | Honestidade atual: não há campanha completa certificável. |

> **Snapshot histórico da branch `8700073`.** Esta auditoria antecede a
> integração subsequente de Viagem/expedição e o replay H2 `verified_victory`.
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
