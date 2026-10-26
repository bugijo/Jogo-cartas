# Integração de campanhas — estado atualizado

## Atualização ativa — pista e combustível regionais (2026-10-26)

**Referência confirmada:** `RULES.md §11, linha 64` (Veículo) define 2
Combustíveis por trecho; `RULES.md §5, linha 29` define as rotas curta (1
trecho por sentido) e longa (2 por sentido). A referência “§64” na solicitação
é a linha 64, não uma seção numerada 64. O `far=3` regional e o custo 12 de
`EXP-MIS-104` permanecem experimentais.

- `NARRATIVE_DEPENDENCIES.md` contém o grafo e a matriz de desbloqueio. A
  hipótese experimental separa descoberta física, cópia de evidência e
  recrutamento. Nenhuma pista é automática.
- `verify_continuous_campaign.py` agora reproduz a tentativa real H2 seed 22:
  Cisterna `verified_victory` → migração → expedição legal à Estação → 1 PA
  para investigar Célia → 1 PA para copiar uma evidência → falha de extração e
  retirada de emergência no relógio 7. Célia não retorna, não é recrutada,
  `radio_code` permanece falso e só há uma pista. O save/load após a retirada
  reproduz o estado.
- Na rota testada, o agente que atravessou até a zona 14 precisa de 13 PA para
  investigar, copiar e voltar, contra 9 PA individuais em três ativações far.
  Isso explica a derrota do controlador seed 22, mas não prova impossibilidade
  universal: ações podem ser divididas entre heróis, combinação ainda não
  validada em replay completo.
- Reserva de 8 Combustíveis na Oficina é uma regra **experimental de teste**,
  não parte do kit 0.2. Cada ação custa 2 PA, ruído 3, uma vez; só retorna ao
  estoque em extração normal. Oito políticas programáticas retornaram a reserva
  legalmente em seed 22. O mapa experimental torna o Posto `medium=2`, cujo
  retorno na van cobra 4; `CAMPAIGN.md` descreve ida a pé e retorno curto por 2.
  O mapeamento medium↔rota canônica não foi decidido; detalhes em
  `TACTICAL_FUEL_AUDIT.md`.
- O gate `EXP-MIS-104` candidato é 12 (`2 × far 3 × ida/volta`), sob status
  experimental. Nenhuma campanha alcançou o Posto/van depois da origem,
  instalação, transmissor ou defesa final nesta prova.
- Validação nova impede contato/evidência sem recibos físicos, evidencia única
  duplicada e recibos de pista que não batem com dados, investigação prévia e
  expedição real. O JSON ainda é editável; isto é validação estrutural, não
  autenticação.
- Um teste adversarial encontrou status falso de “objetivo concluído e saiu”
  quando o inimigo ainda ocupava a saída e o limite de tentativas acabava. O
  controlador agora retorna `step_limit` enquanto o encontro seguir aberto.

## Histórico de implementação regional em `709c48f` — supersedido pelo estado ativo acima

- A suíte de ações táticas foi alinhada ao texto que existe em `RULES.md`: movimento sob inimigo, porta comum e porta bloqueada. Confira a fonte de veículo em §11, linha 64, no relatório de combustível.
- O despacho regional garante ida + uma rodada local + retorno no relógio. O jogador regional usa ações públicas e não injeta recursos; o teste reproduz Cisterna H2 seed 22, migra, busca 2 comida/1 água no Mercado, salva/restaura, retorna e fecha o dia.
- O controlador não prova Célia: `contact_npc` exige presença na zona, PA, espaço e sustento, mas a prova isolada usa configuração de teste com inimigos removidos. A rota de campanha seed 22 termina em derrota local anterior; nenhum recrutamento é alegado.
- Não existe uma partida completa de Última Transmissão. Baralho de Viagem/emboscadas no relógio regional, múltiplas rodadas por mapas regionais, rota ao Posto e retorno militar ainda não estão integrados.
- Nova inconsistência narrativa: após migração seed 22 há zero pistas; só Célia e Vicente produzem `research`. Célia está localizada provisoriamente após `post_cistern_radio_signal`, enquanto o código de rádio exige duas pistas. O acesso pré-sinal a Célia não deve ser inferido sem atualizar o conteúdo/progressão.
- Em `TACTICAL_FUEL_AUDIT.md`, custo e oferta estão separados por fonte. O2 não recebeu combustível por inferência; não foi escolhido custo diferente de 12 nem mapeamento físico para `far=3`.

Fontes oficiais da primeira campanha: `../RULES.md`, `../CAMPAIGN.md` e `../content/catalog.json`. O motor em `edicao-integral/` continua experimental e não substitui esses arquivos. O kit físico 0.2 permanece intacto.

## A Cisterna certificada

O replay H2 seed 22 parte de preparação normal e conclui cinco dias/noites, três expedições, 98 decisões, os eventos e cercos obrigatórios, além das etapas A/B/C do filtro. `verify_campaign_player02.py` recebe `verified_victory` depois de validar os recibos. Isso prova uma trajetória específica, não todas as sementes, equilíbrio ou o arco seguinte. A rota não escolhe resgates nem promessas; as regras não os tornam requisito universal da vitória.

## Migração reproduzível

`IntegratedCampaign.transition_to_last_transmission()` exige certificado, quinta refeição, eventos/noites fechados, três objetivos com recibos e nenhuma expedição/resolução pendente. Projeta o estado em um `World` temporário, valida e anexa uma única vez. A repetição é idempotente. O save preserva o arquivo integral de origem e seu digest SHA-256 determinístico; o digest não é assinatura e não impede adulteração manual de JSON.

| Estado de origem | Projeção ou preservação | Limite conhecido |
| --- | --- | --- |
| Fundadores ativos, ferimentos e pessoas (adultos, crianças, cães) | IDs e ferimentos dos fundadores, `continuity_people`, consumidores e capacidades | Habilidades antigas de Téo/Célia ainda não são operacionais no segundo motor |
| Comida e água por lotes | Contadores regionais com soma exata; lotes permanecem no arquivo de origem | Validade/consumo por cartas não foi portado ao modelo regional |
| Munição e medicamento | Contadores exatos | — |
| Vínculos, promessas, Moral, Saúde, Pressão, carne, materiais e estruturas | Arquivo de continuidade não gastável | Não têm equivalência operacional completa |
| Pé de cabra | Instância `EXP-EQU-002` | Correspondência pelo modelo equivalente |
| Bateria da Oficina | Estoque único se já retirada; objetivo único em `EXP-LOC-03` se ainda estava no local; perdida não reaparece | Item identificado como `battery` no motor regional |
| Van de manutenção | Mapa Posto / `EXP-VEI-02` (6 lugares, 12 cargas, 2 combustível/segmento) | Se não recuperada na origem, continua abandonada no Posto |
| Machado, faca e ferramentas sem modelo equivalente | Arquivo de continuidade | Não convertidos sem regra/modelo compatível |

## Replay contínuo parcial — documentação histórica, replay atual no topo

> **Estado atual, HEAD `fb48fda`:** o replay histórico abaixo, que alcançava o bloqueio de
> combustível, foi substituído após ativar o relógio compartilhado e o limite
> canônico de uma expedição por dia. A execução reproduzível atual conclui a
> Cisterna seed 22 e a expedição do Mercado, fecha o dia, inicia a expedição
> regional à Estação e registra contato físico provisório com Célia. A rota
> termina em derrota local e usa a retirada de emergência canônica: perde a
> carga obtida, recebe ferimento/fadiga e deixa Célia na Estação. O relógio era
> 7/10. Não há campanha contínua até Posto/instalação nesse replay. O combustível
> continua uma decisão posterior e independente.

O contato de Célia em `data/regional_campaign.json` é uma adaptação experimental
para tornar o requisito físico executável; a campanha 0.2 não define encontro,
local, custo de acolhimento ou momento regional para ela. O teste de contato
isolado que limpa inimigos do mapa é uma fixture de unidade, não evidência de
que a ação seja alcançável nem de que Célia retorne em uma partida legal.

Desde o checkpoint, o motor aplica descanso do §25, preserva fadiga na migração,
impede trabalho e expedição no mesmo dia nos dois sentidos (§4) e não executa
automação de abrigo para NPCs que saíram naquele dia. Isso não completa o
registro diário de trabalho dos civis genéricos arquivados.

O motor agora cobra no relógio regional os trechos e rodadas táticas, limita a
uma expedição por dia, persiste a pressão/baralho de Horda e aplica o surgimento
inicial da campanha na primeira visita. O baralho usa as nove cartas canônicas
Horda já portadas. A retirada de emergência está implementada para o arco
regional com conservação de itens únicos, carga, pessoas escoltadas e veículo.
Cartas de Viagem por trecho e encontros/emboscadas regionais ainda não estão
integrados ao ciclo compartilhado; frequências próprias de Hordas exclusivas de
Última Transmissão também continuam pendentes, sem dado aprovado para inventá-las.
O motor agora registra quem trabalhou ou saiu no dia para aplicar o descanso do
§25 sem curar ferimento de expedicionário/trabalhador. Cartão de acesso ou transmissor perdidos ficam registrados
no destino e não podem ser criados novamente; a ação para recuperá-los do chão
ainda não foi definida, então o motor falha fechado.

O restante desta seção descreve um replay histórico anterior ao relógio
compartilhado; não use seus resultados como estado atual.

`python edicao-integral/verify_continuous_campaign.py` parte da preparação e vitória seed 22. O replay salva 62 registros resumidos (não equivalem a 62 ações atômicas: caminhos agregam múltiplos movimentos). Ele conserva o estado migrado e chega a rádio/código, cartão de acesso, recupera a Bateria única no O1 da Oficina por movimento/porta/1 PA, e depois visita o Posto. No Posto, cada uma das oito cartas de combustível é retirada por ação de 1 PA no O1. A inspeção custa 1 PA; o reparo custa 2 PA e faz teste determinístico de Técnica 6. Na seed 22, Lia falha com 1 e Mara passa com 5 + Técnica 3; a Bateria só é consumida no sucesso. A equipe volta na van e consome quatro unidades da carga no retorno regional médio, ficando com sete no abrigo (três da Oficina, quatro trazidas do Posto).

A tentativa de autorização militar é feita pela API pública e falha com `Combustível insuficiente para ida e volta`, sem deixar `military_access`. A van canônica em `EXP-VEI-02` exige 12 unidades no percurso regional `far` de três segmentos por sentido: 3 × 2 sentidos × 2 unidades por segmento. O estado tem 7 após o retorno do Posto, déficit 5. O máximo atualmente modelado antes de custo de retorno é 11 unidades: três buscas da Oficina e oito cartas do Posto. Não se reduz custo nem se cria combustível para continuar.

> **Ressalva de fonte:** `CAMPAIGN.md` define “lote de provisão” como carta de Conserva ou Água, quatro porções. Posto O2 recebe um lote de cada tipo, não combustível. O catálogo confirma oito cartas únicas de combustível em O1; não foi encontrada fonte de combustível em O2. Portanto, a oferta explícita é oito unidades no Posto, sem combustível extra interpretado por inferência.

## Limite da evidência

O Posto agora consta em `LOCATIONS` como `EXP-LOC-07`, e `gas_station_02` está ativo com a ligação desse destino. As oito cartas são finitas, identificadas e custam ação; a recuperação canônica da van exige inspeção, Bateria carregada, PA e teste. A API antiga `recover_vehicle()` não pode recuperar `EXP-VEI-02`, e uma campanha migrada não pode autorizar instalação com o furgão regional experimental `EXP-VEI-01`.

Mesmo com essa ponte, o replay **não é uma campanha integral legal conforme todas as regras físicas**. O motor regional ainda usa buscas e recrutamento abstratos; não modela o contato narrativo para recrutar Célia, o consumo de PA/relógio por toda expedição, nem o disparo automático de encontros e hordas nesses locais. A pesquisa que abre o rádio também é uma regra do protótipo. A restauração de PA no replay foi ajustada para passar pela ativação tática (`TacticalGame.activate()`), não pelo atalho administrativo `World.begin_round()`. Os movimentos e a retirada de Bateria/combustível/van são operações táticas efetivas, mas os demais trechos não devem ser confundidos com paridade completa do manual.

A referência canônica foi conferida: `RULES.md §11, linha 64` cobra dois
combustíveis por trecho. O custo experimental de `EXP-MIS-104` é 12, aplicado
à distância regional `far=3`; esse mapeamento ainda não está definido para a
edição física. A auditoria atual não escolhe outra quantidade nem interpreta
O2 como combustível.

## Estado e próximo bloqueio

- Cisterna: `verified_victory` H2 seed 22 preservada e reproduzível.
- Migração: preserva origem, identidade, quantidades equivalentes e save/load; não duplica a Bateria.
- Posto/Bateria/van: ponte implementada e testada por ações de mapa.
- Última Transmissão: não certificada; falta resolver a insuficiência estrutural de combustível e a paridade de expedição regional.
- Rádio e cartão: obtidos pela rota experimental atual; recrutamento sem contato narrativo permanece ressalvado.
- Transmissor, retorno militar, defesa final e vitória do arco: não executados; `final_defense()` não foi chamado.
- Não houve impressão física nem playtest humano.

Antes de continuar, uma decisão de regra precisa resolver como a economia regional pode pagar a rota militar sem contrariar o custo canônico. A menor evidência atual é: oferta máxima de 11 combustível conhecida versus custo de 12, sem contar retornos. Ajustar esse valor seria uma proposta mecânica explícita, não correção técnica automática.
