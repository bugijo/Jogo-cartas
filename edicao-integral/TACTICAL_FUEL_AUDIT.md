# Auditoria independente: expedição 0.2, Posto e transição

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
