# Integração de campanhas — estado atual (25/10/2026)

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

## Replay contínuo parcial

> **Estado atual, checkpoint de 25/10/2026 (HEAD local `3b59661` antes dos
> commits deste lote):** o replay histórico abaixo, que alcançava o bloqueio de
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

O motor agora cobra no relógio regional os trechos e rodadas táticas, limita a
uma expedição por dia, persiste a pressão/baralho de Horda e aplica o surgimento
inicial da campanha na primeira visita. O baralho usa as nove cartas canônicas
Horda já portadas. A retirada de emergência está implementada para o arco
regional com conservação de itens únicos, carga, pessoas escoltadas e veículo.
Cartas de Viagem por trecho e frequência própria das Hordas exclusivas de
Última Transmissão continuam pendentes; os dados não definem frequência nova e
ela não foi inventada.

O restante desta seção descreve um replay histórico anterior ao relógio
compartilhado; não use seus resultados como estado atual.

`python edicao-integral/verify_continuous_campaign.py` parte da preparação e vitória seed 22. O replay salva 62 registros resumidos (não equivalem a 62 ações atômicas: caminhos agregam múltiplos movimentos). Ele conserva o estado migrado e chega a rádio/código, cartão de acesso, recupera a Bateria única no O1 da Oficina por movimento/porta/1 PA, e depois visita o Posto. No Posto, cada uma das oito cartas de combustível é retirada por ação de 1 PA no O1. A inspeção custa 1 PA; o reparo custa 2 PA e faz teste determinístico de Técnica 6. Na seed 22, Lia falha com 1 e Mara passa com 5 + Técnica 3; a Bateria só é consumida no sucesso. A equipe volta na van e consome quatro unidades da carga no retorno regional médio, ficando com sete no abrigo (três da Oficina, quatro trazidas do Posto).

A tentativa de autorização militar é feita pela API pública e falha com `Combustível insuficiente para ida e volta`, sem deixar `military_access`. A van canônica em `EXP-VEI-02` exige 12 unidades no percurso regional `far` de três segmentos por sentido: 3 × 2 sentidos × 2 unidades por segmento. O estado tem 7 após o retorno do Posto, déficit 5. O máximo atualmente modelado antes de custo de retorno é 11 unidades: três buscas da Oficina e oito cartas do Posto. Não se reduz custo nem se cria combustível para continuar.

> **Ressalva de fonte:** `CAMPAIGN.md` também chama o conteúdo de Posto O2 de “um lote de cada provisão”, mas não define se combustível está incluído nem quantas unidades seriam. O catálogo atual não atribui combustível a esse lote; as cartas físicas genéricas de reserva não provam aquisição. Portanto, o déficit é reproduzível no modelo implementado, mas a suficiência canônica total depende de esclarecer documentalmente esse lote antes de declarar um soft-lock definitivo.

## Limite da evidência

O Posto agora consta em `LOCATIONS` como `EXP-LOC-07`, e `gas_station_02` está ativo com a ligação desse destino. As oito cartas são finitas, identificadas e custam ação; a recuperação canônica da van exige inspeção, Bateria carregada, PA e teste. A API antiga `recover_vehicle()` não pode recuperar `EXP-VEI-02`, e uma campanha migrada não pode autorizar instalação com o furgão regional experimental `EXP-VEI-01`.

Mesmo com essa ponte, o replay **não é uma campanha integral legal conforme todas as regras físicas**. O motor regional ainda usa buscas e recrutamento abstratos; não modela o contato narrativo para recrutar Célia, o consumo de PA/relógio por toda expedição, nem o disparo automático de encontros e hordas nesses locais. A pesquisa que abre o rádio também é uma regra do protótipo. A restauração de PA no replay foi ajustada para passar pela ativação tática (`TacticalGame.activate()`), não pelo atalho administrativo `World.begin_round()`. Os movimentos e a retirada de Bateria/combustível/van são operações táticas efetivas, mas os demais trechos não devem ser confundidos com paridade completa do manual.

A divergência de unidade está documentada: `RULES.md` §64 cobra dois combustíveis por trecho, enquanto `data/last_transmission.json` fixa seis unidades para a viagem militar `far=3`. Aplicar a regra canônica ao trajeto regional dá 12; usar as seis do protótipo é uma incompatibilidade ainda não aprovada. Nenhum valor foi alterado nesta entrega.

## Estado e próximo bloqueio

- Cisterna: `verified_victory` H2 seed 22 preservada e reproduzível.
- Migração: preserva origem, identidade, quantidades equivalentes e save/load; não duplica a Bateria.
- Posto/Bateria/van: ponte implementada e testada por ações de mapa.
- Última Transmissão: não certificada; falta resolver a insuficiência estrutural de combustível e a paridade de expedição regional.
- Rádio e cartão: obtidos pela rota experimental atual; recrutamento sem contato narrativo permanece ressalvado.
- Transmissor, retorno militar, defesa final e vitória do arco: não executados; `final_defense()` não foi chamado.
- Não houve impressão física nem playtest humano.

Antes de continuar, uma decisão de regra precisa resolver como a economia regional pode pagar a rota militar sem contrariar o custo canônico. A menor evidência atual é: oferta máxima de 11 combustível conhecida versus custo de 12, sem contar retornos. Ajustar esse valor seria uma proposta mecânica explícita, não correção técnica automática.
