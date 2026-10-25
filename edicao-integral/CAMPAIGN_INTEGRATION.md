# Integração de campanhas — estado atual (25/10/2026)

Fontes oficiais do capítulo inicial: `../RULES.md`, `../CAMPAIGN.md` e `../content/catalog.json`. O motor de `edicao-integral/` não substitui esses arquivos. A primeira caixa ainda pode ser jogada com seus PDFs existentes. `cistern02.py` porta preparação, porções, relógio, filtro, privação, acolhimento e cercos/intenções em um estado separado.

Em 24/10/2026 foi concluído e reproduzido um replay legal H2 da Cisterna, seed 22. Ele parte de preparação normal (`IntegratedCampaign.new`), escolhe dois fundadores, sorteia vínculos pelo baralho embaralhado, executa expedições públicas ao Mercado, Oficina e Estação, transporta e entrega Conexões, Bomba e Membrana, processa os cinco eventos, refeições, os cercos dos dias 3 e 5, conclui as etapas A/B/C e recebe `verified_victory` do validador do motor. O replay e o verificador estão em `replays/cisterna_h2_seed22.json` e `verify_campaign_player02.py`.

Esta evidência comprova uma trajetória H2 específica, não a campanha sob todas as sementes, uma taxa de vitória ou equilíbrio. Nenhum resgate foi necessário na rota escolhida; nenhuma promessa foi assumida. Isso satisfaz a condição oficial “sem pessoa abandonada por promessa” porque `CAMPAIGN.md` condiciona a promessa à escolha explícita do grupo e não exige um resgate para vencer. A rota processou dois cercos (missão no dia 3 e Pressão no dia 5), ambos com recibo; o cerco final causou perda de comida e dano ao portão, mas o grupo continuou abastecido naquela refeição.

Diferenças materiais que impedem ligar os arcos por uma flag sem perder regras:

| Aspecto | Capítulo 0.2 | Motor experimental |
| --- | --- | --- |
| Elenco | 24 fichas, 12 iniciais, vínculos sorteados | dez protagonistas fixos e 15 NPCs de outro catálogo |
| Economia | cartas de quatro porções; C inclui cães; validade e lotes locais | contadores food/water por herói/NPC, sem cães ou abertura de carta |
| Abrigo | Moral, Saúde, Pressão, cercos, acolhimento temporário | estruturas, crises e estoque, sem aqueles três indicadores |
| Tempo | dez segmentos compartilhados por viagem e combate | segmentos regionais, rodadas táticas independentes |
| Objetivo | filtro em etapas A/B/C até dia 5, peças Conexões/Bomba/Membrana | flag `cistern_complete`, sem ficha de projeto ou peças |
| Lugares | seis destinos e quatro módulos impressos por destino | seis locais regionais diferentes, oito plantas funcionais, incluindo as seis geometrias canônicas; Posto e Condomínio ainda sem destino regional |

## Transição implementada e reproduzida

`IntegratedCampaign.transition_to_last_transmission()` agora aceita somente um
save com `verified_victory` certificado, capítulo validado, quinta refeição e
noites/eventos encerrados, objetivos entregues por recibos legais e nenhuma
expedição ou resolução pendente. A projeção é montada em um `World` temporário,
validada e só então anexada à campanha. Repetir a chamada retorna o mesmo
recibo sem adicionar recursos; save/load mantém fase e proveniência.

O recibo guarda hash SHA-256 determinístico de um arquivo integral da campanha
de origem, mais arquivo de continuidade não gastável. O hash detecta divergência
acidental e permite replay; saves JSON editáveis não são assinados e isso não é
proteção criptográfica contra adulteração manual.

| Estado da Cisterna | Projeção regional | Tratamento |
| --- | --- | --- |
| Fundadores ativos | Mesmo ID em `World.heroes` | Vida calculada pelos ferimentos; o registro de ferimento, fadiga, privação e vínculo também fica anexado ao estado de continuidade |
| Téo e Célia (fundadores 11/12) | Perfis-ponte por ID, derivados do catálogo canônico | Não são convertidos em NPCs nem duplicados; habilidades 0.2 ficam preservadas no arquivo, mas ainda não funcionam no segundo motor |
| Adultos, crianças e cães presentes | `World.continuity_people` | Identidade e estado preservados; continuam contando em capacidade humana e consumo diário (cães contam no consumo, não em leitos) |
| Lotes de comida/água | Contadores numéricos regionais | Quantidades são a soma exata dos lotes; o arquivo guarda a divisão original |
| Munição e medicamento | Contadores correspondentes | Quantidade exata |
| Cartas de combustível | Contador `fuel`, uma unidade por carta | Quantidade exata; seed 22 não tem nenhuma |
| Materiais, estruturas, Moral, Saúde, Pressão, carne, promessas, cercos e histórico | Arquivo de continuidade | Preservados sem efeito/gasto regional até portar regras equivalentes |
| Pé de cabra | Instância `EXP-EQU-002` na mão | Projeção por correspondência de nome/modelo; cada instância é identificada |
| Machado, faca, ferramentas, Bateria e van 0.2 | Arquivo de continuidade | Não convertidos para itens/veículos de regras diferentes; ficam sem uso no arco regional por enquanto |

O replay contínuo `replays/cistern_to_transmission_seed22_blocked.json` começa
na preparação legal seed 22, reproduz a vitória da Cisterna, migra e executa
11 chamadas de ação regional: viagem à Estação, busca, recuperação do cartão,
retorno e tentativa de decifrar o rádio. A carta de acesso é obtida e retorna
ao abrigo sem alterar combustível. O primeiro bloqueio real é `decode_radio()`:
requer duas pistas, mas a migração legítima tem zero.

## Bloqueios consecutivos confirmados

1. `Cistern02` não tem campo nem recibo de pista; a rota H2 seed 22 encerra sem
   pista. O catálogo regional contém uma carta `EXP-EVT-001` com uma opção que
   poderia dar uma pista, mas o motor não a sorteia nem a resolve em uma
   expedição. Célia e NPCs de pesquisa poderiam gerar pistas somente depois de
   recrutamento, mas o motor não tem encontro/acolhimento que autorize essa
   contratação. Não é legal chamar `recruit()` para contornar o requisito.
2. Se o rádio for resolvido por uma futura fonte legítima, ainda falta o Posto
   em `system.json`/`LOCATIONS`. A planta `gas_station_02` está marcada como
   referência e não é um destino regional. A Oficina oferece no máximo três
   buscas de combustível, com uma unidade cada; seed 22 transporta zero cartas
   de combustível. Isso não cobre a instalação militar (seis unidades na
   viagem de ida e volta no modelo regional).
3. A recuperação regional de veículo ocorre na Oficina com custo de combustível
   e não exige Bateria; a regra canônica 0.2 exige Bateria, 2 PA e teste de
   Técnica no Posto. O modelo regional de furgão também difere da van 0.2
   (quatro vs. seis assentos). Nenhuma conversão foi aplicada silenciosamente.
4. O modelo regional não contém encontros táticos conectados às expedições
   regionais abstratas. A obtenção do cartão acima prova apenas as operações
   presentes no motor, não uma expedição tática física completa.

Não foram adicionados pistas, combustível, Bateria, van, NPCs, resgates ou
recompensas. Não foi chamada `final_defense()`. Não há campanha contínua
completa nem `verified_victory` do segundo arco. A menor próxima entrega é
portar, com fontes oficiais e recibos, o encontro/evento que fornece pistas e
o destino Posto/Bateria/van; em seguida alinhar custos de transporte e tática
antes de tentar novamente a campanha integral.

O código da defesa final ainda é conteúdo experimental; o ensaio
`ENSAIO_DEFESA_20261023.json` injeta requisitos e equipamento e, portanto, não
é evidência de campanha contínua ou equilíbrio. A execução atual para antes de
decodificar o rádio.
