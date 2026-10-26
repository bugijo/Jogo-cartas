# Estado ativo — retomada 2026-10-26

- Base verificada por `git fetch`: branch `evolucao/zona-zero-sistema-v1`, HEAD local/remoto `081048f`; o código/replay foi publicado e restam alterações documentais locais para checkpoint. `main` e kit físico 0.2 não foram alterados.
- Regra de combustível: `RULES.md §11, linha 64` = 2 por trecho; §5, linha 29 define curta 1+1 e longa 2+2. Posto O1 tem oito cartas. O2 “um lote de cada provisão” refere-se a alimento e água e não autoriza combustível. `EXP-MIS-104=12` e cache experimental de 8 na Oficina não são regras aprovadas; equivalência regional `far=3` e retorno `medium=2` continuam pendentes.
- A Cisterna H2 seed22 segue `verified_victory`: cinco dias/noites, três expedições, 98 decisões. Com política `stealth` (evita combate opcional fora das zonas de objetivo/saída), uma viagem regional à Estação investigou Célia, copiou uma pista, saiu normalmente e retornou no segmento 10. Não recrutou Célia nem ativou o rádio. O perfil balanced, que gasta PA em combates opcionais, ainda termina em emergência; isso é diferença de estratégia, não prova de impossibilidade.
- Há só duas fontes experimentais de pista. Célia como fundadora ou Vicente acolhido pode tornar uma delas indisponível. Uma trajetória `stealth` de equipe já extraiu uma pista, então o cálculo individual de 13 PA não prova impossibilidade do grupo. A segunda pista/contato ainda não está resolvida.
- O snapshot do baralho de Viagem migra e sobrevive a save/load. Cartas regionais ainda não são reveladas/resolvidas. O controlador testa retirada do Posto após falha de reparo e retorno a pé; é teste de integração do controlador, não campanha canônica. O motor regional ainda não aplica Fome/Sede e lesões por escassez aos moradores.
- Correção de bug: o controlador não declara extração concluída enquanto o encontro permanece aberto por inimigo. Corrigido o texto da fonte canônica no catálogo gerado e na missão experimental.
- Verificações concluídas: 321 testes; validador, compilação, JSON e `git diff --check`; Cisterna seed22; replay `stealth` de uma pista retornada e comparação `balanced` de emergência. O artefato foi regenerado e reproduzido bit a bit.
- Próxima tarefa: executar a segunda pista/contato físico com estado alimentar canônico e implementar refeições/Fome/Sede com distribuição auditável; depois desenhar a ponte de cartas de Viagem para recursos carregados e Ambush02. Não atribuir custos/efeitos não previstos nem tratar as hipóteses de combustível como regra final. Impressão e playtest humano seguem pendentes.

Os blocos de checkpoint seguintes são históricos; quando divergirem deste estado ativo, prevalece este cabeçalho.

# Checkpoint — campanha contínua Cisterna → Última Transmissão

## Estado ativo desta retomada — commit funcional `3e65893`

Árvore local iniciou limpa no ancestral `86a53ffe57b26cdd33fcc1be0d961c0f7d8a7226`.
O commit funcional `3e65893` foi publicado por fast-forward normal na branch
experimental; falta publicar este checkpoint documental. `main` e o kit físico
0.2 não foram alterados.

- Preservada a regressão oficial da Cisterna: H2 seed 22, vitória certificada,
  5 dias/noites, 3 expedições, 98 decisões.
- Geração de pista agora exige investigação física pré-rádio, zona segura,
  custo de PA e receipt único; contato/recrutamento exige receipt de descoberta,
  mas a busca física não exige que a comunidade já tenha cama/ração disponíveis
  para acolher. Vicente é a identidade condicional original `ZC-MOR-0003`.
- Controlador regional corrigido para gastar PA de outro herói antes de avançar
  relógio; a extração não tenta uma ação inexistente quando um inimigo ocupa a
  saída. Saves conferem os recibos de evidência contra fonte, ação anterior,
  missão, valor, local e custo; JSON editável não é autenticado.
- Hipóteses em `data/regional_campaign.json`: oito unidades no cache finito da
  Oficina (2 PA, ruído 3, carga, única, emergência perde) e combustível da
  missão militar = 12 (`2/trecho × 3 far × ida/volta`). Ambas experimentais,
  sem alteração dos manuais oficiais. O retorno Posto regional (4) diverge do
  retorno por van 0.2 (2); consultar `TACTICAL_FUEL_AUDIT.md`.
- Prova atual do segundo arco: 27 decisões, Estação, Célia investigada e 1
  pista copiada; retirada de emergência no clock 7. Sem recrutamento, rádio,
  cartão, van, transmissor, defesa ou vitória do segundo arco. Replay em
  `replays/cistern_to_transmission_seed22_blocked.json` (schema 3).
- Bloqueio principal: via Estação `far=3`, só 3 ativações locais permanecem;
  alcançar Z14 + copiar a evidência + voltar exige mínimo 13 PA do explorador,
  máximo 9. Requer decisão de design sobre rota/tempo/local; não mudar
  equilíbrio silenciosamente. Grafo: `NARRATIVE_DEPENDENCIES.md`.
- A reserva experimental de combustível da Oficina foi retornada por 8/8
  políticas na mesma seed; isso não inclui rota Posto/van nem prova campanha
  completa. Baralho regional de Viagem/emboscadas continua pendente.
- Última verificação executada antes do commit funcional: suíte completa 314 passou; `validate_data.py`,
  `compileall`, JSON da fila e `git diff --check` passaram; replay da Cisterna
  e replay bloqueado passaram. O teste amplo foi executado antes do commit
  funcional; a mudança posterior foi documental apenas.

HEAD publicado: `3e65893` (`feat: validate regional clues and experimental fuel route`).
Próximo passo: publicar o commit documental; depois retomar a decisão de design
que permita a extração da Estação sem alterar silenciosamente o relógio nem a
geometria.

## Estado ativo desta retomada — HEAD remoto `1feacee581e04649bcbfd9f4e7f212f3ce21c534`

- O HEAD local/remoto confirmado antes da edição foi `d3d6137660cf0d3e4415e227fcf9b5edad13bccf`; branch `evolucao/zona-zero-sistema-v1`, árvore inicialmente limpa. O HEAD citado na solicitação (`3b5966…`) não é o estado disponível nesta cópia. O commit funcional `709c48f` e o commit documental `1feacee` foram publicados por fast-forward normal.
- Corrigida a matriz de combustível: `RULES.md` nesta cópia termina na §14 e não contém §64. A van e custo de 2 unidades/trecho estão em §11; segmentos de rota estão em §5. `CAMPAIGN.md`/`content/catalog.json` dizem 8 combustíveis únicos no Posto O1 e O2 “um lote de cada provisão”, sem declarar combustível nem quantidade adicional. `EXP-MIS-104` experimental cobra 6 fixos; `EXP-LOC-06 far=3` com custo canônico resulta em 12. Nenhuma regra foi escolhida nem combustível criado.
- A integração tática foi ajustada ao manual: mover custa 1 PA, mais 1 ao sair de zona ocupada; abrir porta comum custa 1 PA; porta bloqueada custa 2 PA com ferramenta, sem teste, desgaste ou ruído não escrito na regra. O baralho Horda existente permanece persistente.
- `World.open_expedition()` agora recusa, sem alterar o estado, despacho quando não há reserva para ida + ao menos uma rodada local + retorno dentro do relógio 10.
- Novo `AdaptiveRegionalPlayer` toma decisões observáveis pela API `World`/`TacticalGame`, inclui save/load de seu plano e uma viagem regional a pé. Rejeita veículo enquanto custo/rota de combustível não estiverem conciliados. A revisão adversarial corrigiu falso sucesso de contato indisponível, rota que ignorava desvio aberto sem ferramenta e validação tardia de mapa.
- Prova regional reproduzível adicionada: vitória Cisterna H2 seed 22 → migração → busca tática no Mercado → save/load → retorno → contabilização de 2 comida + 1 água e refeição. **Não** cobre Célia, viagem por cartas, Posto, transmissor ou defesa final.
- Novo bloqueio de narrativa/recursos identificado: a migração seed 22 produz `clues=0`; somente Célia e Vicente têm produção `research` no catálogo regional. Célia está marcada `post_cistern_radio_signal`, mas sua localização/contato é provisória e o código de rádio exige 2 pistas. A ordem para obter essas pistas antes de recrutar Célia precisa ser resolvida no design; não foi alterada.
- Próximo bloqueio integral permanece: paridade de viagem/emboscada regional e decisão de combustível. Campanha completa em Última Transmissão ainda não foi executada.
- Verificação final: 296 testes; validador (127 IDs, 10 protagonistas, 70 habilidades, 15 NPCs), `compileall`, JSON da fila e `git diff --check` passaram. Cisterna seed 22 = 5 dias/noites, 3 expedições, 98 decisões, `verified_victory`; replay regional parcial comprovado. O replay contínuo segue em derrota local na Estação.

Branch: `evolucao/zona-zero-sistema-v1`
HEAD remoto publicado: `1feacee581e04649bcbfd9f4e7f212f3ce21c534`
Commits funcionais/documentais publicados neste lote: `2e07b08`, `6d25b43`, `2a24cc7`, `60340c4`, `f205e55`, `0f1ce2a`, `fb48fda`, `709c48f`, `1feacee`.
Main e kit físico 0.2 intactos.

## Atualização ativa — relógio e primeiro replay regional

- Regressão Cisterna H2 seed 22 preservada: `verified_victory`, 5 dias/noites,
  3 expedições, 98 decisões.
- O motor regional agora cobra segmentos de viagem e rodadas táticas em um
  relógio compartilhado de 10; impõe uma expedição por dia; aplica fadiga nos
  segmentos 9–10; persiste deck/pressão de Horda e surgimento inicial do local.
- O replay atualizado fecha o dia do Mercado e começa a Estação no dia
  seguinte. A adaptação experimental de contato de Célia registra a ação; um
  herói é incapacitado e o controlador executa a retirada de emergência
  canônica. O resultado é derrota local no relógio 7/10: carga perdida, ferimento
  e fadiga, Célia permanece na Estação. Não declara recrutamento concluído nem
  vitória de Última Transmissão.
- Célia só está disponível por uma configuração provisória em
  `data/regional_campaign.json`; a edição 0.2 não define seu encontro/local no
  segundo arco. Não usar a fixture de teste que limpa inimigos como prova de
  campanha legal.
- Combustível permanece sem resolução: O1 do Posto = 8 unidades; O2 “um lote de
  cada provisão” não autoriza combustível; van = 2 por trecho (§11); `far=3`
  resulta em 12 na ida/volta e `EXP-MIS-104` fixa 6. A Oficina não concede mais
  combustível não autorizado. Ver `edicao-integral/TACTICAL_FUEL_AUDIT.md`.
- Retirada de emergência regional está implementada. Viagem regional por
  cartas, frequência de Hordas exclusivas do segundo arco e conclusão da
  campanha permanecem pendentes por lacunas documentais/implementação.
- §25 agora está aplicado aos heróis e NPCs: ferimento só recupera após refeição
  completa para pessoa no abrigo que não trabalhou nem saiu; fadiga reduz uma
  para todos os presentes após refeição completa. Trabalho/saída sobrevivem ao
  save/load. Validação rejeita fadiga fora de 0–3; Hordas anunciadas ficam
  pendentes sem avançar no primeiro turno protegido do Mercado.
- Migração agora preserva fadiga individual (0–3). O motor impede que um herói
  que trabalhou saia em expedição no mesmo dia e impede trabalho depois de uma
  saída, mesmo após o retorno; especialistas NPC que saíram não fazem sua
  automação de abrigo naquela noite.

## Verificação no HEAD `fb48fda`

- `python3 -m unittest discover -s edicao-integral/tests -q`: 282 testes passam.
- `verify_campaign_player02.py`: vitória Cisterna seed 22 reproduzível (5
  dias/noites, 3 expedições, 98 decisões).
- `verify_continuous_campaign.py --write` e verificação: reproduzíveis; a
  sequência registra derrota local, aplica emergência, e salva/restaura o estado.
- Ainda pendentes: campanha contínua, combustível aprovado, impressão e
  playtest humano.
- Um cartão/transmissor perdido permanece único no destino e não pode ser
  duplicado; a ação para recuperá-lo ainda não está definida.
- A suíte não valida recuperação de ferimentos de civis genéricos migrados,
  porque o ledger de continuidade não possui estado operacional de trabalho,
  fadiga e ferimento por pessoa.
- Trabalho exige herói apto (vida acima de zero e fadiga abaixo de 3); atribuir
  horta exige estrutura ativa. Testes cobrem essas proibições.
- O NPC médico não pode tratar herói que esteja fora do abrigo; a automação e o
  medicamento permanecem intactos se nenhum ferido estiver presente.
- A matriz de combustível não teve regra escolhida: não existe fonte documental
  explícita de combustível em O2. Propostas e déficit constam em
  `edicao-integral/TACTICAL_FUEL_AUDIT.md`.

## Histórico — antes do relógio regional e da retirada de emergência

- A Cisterna H2 seed 22 continua como regressão: 5 dias/noites, 3 expedições, 98 decisões e `verified_victory`.
- Migração atômica/idempotente por `transition_to_last_transmission()` preserva o arquivo integral, digest e quantidades com equivalência. Saves JSON são editáveis; o digest não é autenticação.
- Seed 22 migra Lia e Mara, o adulto R01, recursos e os recibos. A Bateria não foi retirada na Cisterna: segue como objetivo único na Oficina O1, não como recurso gratuito.
- O Posto está ativo em `EXP-LOC-07` ligado a `gas_station_02`. Cada uma das 8 cartas de combustível é retirada individualmente por 1 PA no O1. A van canônica tem 6 lugares/12 cargas, exige inspeção, Bateria e teste Técnica 6 por 2 PA. A falha não consome Bateria; sucesso consome. `EXP-VEI-01` não substitui a van na campanha migrada.
- O replay contínuo parcial `verify_continuous_campaign.py` realiza 62 registros resumidos após a Cisterna: rota de rádio e cartão, recuperação da Bateria por movimento/porta/PA, oito cartas do Posto, inspeção e reparo determinístico, retorno com a van e gate militar. Isso não equivale a 62 ações atômicas. O controlador renova PA por `TacticalGame.activate()`, nunca por `World.begin_round()`.
- Resultado seed 22: Lia falha no teste com 1; Mara passa com 5 + Técnica 3. Retorno médio com a van consome 4 das 8 cartas do Posto. Ficam 7 unidades no abrigo (3 Oficina + 4 Posto). O gate da instalação militar exige 12 na especificação canônica regional (`far=3`, dois sentidos, 2/segmento), rejeita sem mutação, e registra déficit 5.
- Busca regional em campanha migrada agora exige encontro tático, presença em zona de busca e 1 PA; cartão de acesso é carga única e precisa voltar ao abrigo. O replay salva/restaura o estado regional integral.

## Bloqueios antigos supersedidos pelo estado ativo acima

Não há campanha integral Cisterna → defesa final. O catálogo regional atualmente modelado fornece no máximo 11 combustíveis (3 Oficina + 8 Posto) antes de retorno, abaixo das 12 unidades do modelo regional `far=3`; a seed deixa 7 depois de voltar do Posto. `data/last_transmission.json` ainda codifica custo 6, divergente de `RULES.md` §11. `CAMPAIGN.md` não define se o “lote de cada provisão” do Posto O2 inclui combustível nem a quantidade; por isso, 11 é teto do modelo, mas não prova o soft-lock canônico enquanto essa frase estiver ambígua. Nenhum custo foi reduzido e nenhum combustível foi criado.

Outras limitações de paridade: recrutamento do pesquisador ainda não tem contato narrativo; a pesquisa/estação e algumas operações regionais continuam protótipos, sem ligar todo o relógio de dez segmentos, eventos/emboscadas/hordas da regra 0.2. A cena regional não é simulada como combate completo em todos destinos. Portanto, o replay de 62 registros demonstra a ponte de estado e ações implementadas, não campanha física integral legal.

Nenhum `verified_victory` foi emitido para Última Transmissão. Transmissor e defesa final não foram alcançados. Não ocorreu impressão física nem playtest humano.

## Próxima decisão registrada no checkpoint anterior

Antes de buscar a defesa final, resolver explicitamente a equivalência de combustível entre regional `far=3`, o custo experimental de seis e `RULES.md` §11 (2 por trecho), sem mudar números silenciosamente. O pedido anterior cita §64, mas essa seção não existe na cópia atual do manual. Alternativas a avaliar na fila: formalizar uma unidade regional diferente com regra escrita e impacto; ou identificar uma fonte/mecânica de combustível já autorizada pelo conteúdo atual. A oferta atual demonstra déficit, não prova isolada de equilíbrio global.

## Verificação histórica do lote de migração

- Regressão completa: 253 testes passaram, incluindo as duas regressões independentes.
- `validate_data.py`: passou (127 IDs únicos; 10 heróis; 70 habilidades; 15 NPCs; 7 locais; 8 mapas táticos).
- `verify_campaign_player02.py`: `verified_victory`, 5 dias/noites, 3 expedições, 98 decisões.
- `verify_continuous_campaign.py`: replay reproduzível chega ao gate militar e para sem mutação por falta de combustível; 62 registros resumidos após a Cisterna.
- `compileall` e `git diff --check`: passaram após as alterações de código e documentação.
- Auditoria adversarial encontrou e os testes confirmaram correção de dois erros: save/load de cartão de acesso em expedição militar e contagem de carga especial durante busca.
- Revisões independentes somente leitura nesta sessão: unidade/fontes de combustível e revisão de ponte/persistência. Confirmaram a divergência de custo, a ambiguidade do Posto O2 e que não se deve afirmar legalidade física completa.

Retomada:

```bash
git fetch origin evolucao/zona-zero-sistema-v1
git merge --ff-only origin/evolucao/zona-zero-sistema-v1
python edicao-integral/verify_campaign_player02.py
python edicao-integral/verify_continuous_campaign.py --write
python edicao-integral/verify_continuous_campaign.py
python edicao-integral/validate_data.py
python -m unittest discover -s edicao-integral/tests -q
```
