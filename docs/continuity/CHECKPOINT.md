# Estado ativo — emboscada regional, 2026-10-27

- Ponte de Emboscada regional no M1 0.2 (`start_regional_ambush`/`finish_regional_ambush`): relógio real, Horda regional, ferimentos/fadiga/Fome-Sede, sem armas ou Munição inventadas, save/load, emergência de estrada §34. Documentada em `edicao-integral/MANUAL_EXPERIMENTAL.md`.
- Pendente de aprovação: durabilidade regional não é consumida na emboscada. Não modelado: emergência de estrada com carga única ou veículo.
- Próximo bloqueio: controlador regional (`AdaptiveRegionalPlayer`) resolver cartas e emboscadas e ligar `regional_travel_cards` num replay contínuo novo, sem alterar os registrados.
- 386 testes; verificadores, `compileall`, `git diff --check` passaram.

# Estado ativo — ponte de Viagem regional, 2026-10-27

- `World.regional_travel_cards` (opcional, desligado por padrão): uma carta de Viagem por trecho pago no transporte regional, extra noturna sem segmento, Placa, escolhas apenas sem carga levada, Pressão/Material sem equivalente arquivados (não gastáveis), save/load sem repetir carta. Documentado em `edicao-integral/MANUAL_EXPERIMENTAL.md`.
- Emboscada regional (`ZC-VIA-0005`) fica pendente e bloqueia: **próximo bloqueio** (`P1-REGIONAL-AMBUSH`).
- Replays regionais registrados inalterados; 382 testes; verificadores, `compileall`, `git diff --check` passaram.
- Pendências documentadas sem regra aprovada: combustível regional, carga levada regional, Material de Ferragens no chão, narrativa de Célia/pistas.

# Estado ativo — validação 61–90 e decisões aprovadas, 2026-10-27

- Decisões aprovadas e aplicadas (registradas em `edicao-integral/MANUAL_EXPERIMENTAL.md`): escolta 1 PA para iniciar; Ferragens sem Material levado não perde recurso.
- Validação cega 61–90 (antes de ajustes): adaptativo 56/150, anterior 9, fixo 0. Após a regra de Ferragens: 66/150.
- H2 continua fraco (4–6/30): rota cautelosa não é a causa; dupla e rota longa pioram; correção de carga evita abortar campanha.
- Auditoria: apoio é a alavanca de H3–H4; escolta marginal; custo 1 PA de escolta quase sem efeito nas vitórias.
- Próximas medições do controlador da Cisterna devem usar sementes novas (91–120).
- Próximo bloco: Última Transmissão — cartas de Viagem regionais (`P1-REGIONAL-TRAVEL-SHOE`).

# Estado ativo — tática da Estação, 2026-10-27

- Motor: escolta de incapacitado (§31/§43) implementada; custo de ligação 1 PA é leitura conservadora **pendente de aprovação**.
- Controlador adaptativo ganhou táticas `escort`, `late_retreat`, `cautious`, `support` (padrão) e política Oficina primeiro; modo fixo e seed 22 (98 decisões) inalterados; `tactics=()` reproduz exatamente o adaptativo anterior.
- Sementes reservadas 31–60: 66/150 vitórias (H2 5, H3 15, H4 19, H5 9, H6 18) contra 23 do adaptativo anterior e 2 do fixo. Emergências na Estação caíram muito em H3+; H2 piorou levemente.
- Verificação: 368 testes; todos os verificadores; varredura reproduzível; `compileall`; `git diff --check`.
- Próximos passos: H2 (sem herói livre para apoio); decisões pendentes `ZC-VIA-0010` e custo da escolta; depois retomar o segundo arco (cartas de Viagem regionais).

# Estado ativo — Coleta de emergência §26, 2026-10-27

- Motor: Coleta de emergência implementada (`plan_emergency_collection`, resolução na fase de trabalhos), com limites de 2 porções/dia, um trabalho por pessoa, aptidão, cerco antes, save/load e limpeza diária. Campo novo `collection_plan` com padrão vazio; saves antigos carregam.
- Controlador adaptativo usa a coleta com quem sobra no abrigo. Sementes reservadas 31–60: H2 7, H3 0, H4 0, H5 6, H6 10 (sem coleta: 5/0/0/7/11). Efeito dentro do ruído; gargalo continua a tática na Estação.
- Artefato contínuo seed 22 regenerado só pelo digest da migração (estado ganhou um campo).
- Verificação: 361 testes; todos os verificadores, varredura reproduzível, `compileall`, `git diff --check`.
- Próximo passo seguro: `P0-STATION-TACTICAL-AI`. Pendente de decisão: `ZC-VIA-0010` sem Material levado.

# Estado ativo — estratégia adaptativa da Cisterna, 2026-10-27

- Decisão do usuário: manter o lote de mantimentos indivisível (`ceil(C/4)` cartas). Nenhuma regra alterada.
- `CampaignPlayer02.adaptive` (padrão desligado) planeja no amanhecer: reservas, destino por peça faltante/déficit de comida, trabalho de adultos, vigias. Seed 22 fixa continua `verified_victory` com 98 decisões.
- Sementes reservadas 31–60, política escolhida antes em 1–30: adaptativo H2 5/30, H3 0, H4 0, H5 7/30, H6 11/30; fixo 2/0/0/0/0. Ver `PLAYTEST_REPORT.md`.
- Correção do motor: emergência após o 25º inimigo (§39) deixou de travar. Correções do controlador: dados de vigia, ferramenta em porta bloqueada, equipamento por equipe, rodada após invasão.
- Pendências de decisão: `ZC-VIA-0010` sem Material levado (lacuna). Pendência de implementação: Coleta de emergência §26.
- Verificação: 351 testes; todos os verificadores, `simulate_cistern_sweep.py` (reprodução idêntica), `compileall`, `git diff --check`.
- Próximo passo seguro: melhorar o controlador tático na Estação (gargalo de H3–H4) e implementar Coleta de emergência §26 com teste; depois retomar o segundo arco.

# Estado ativo — varredura H2–H6 da Cisterna, 2026-10-27

- Retomada no HEAD `2e1db33d8bf0a4ac732a19d87a3a8443bdc49b77`, igual ao remoto, árvore limpa (o HEAD `86a53ff` citado no pedido é ancestral). Suíte inicial: 340 testes OK.
- Nova tarefa independente das decisões pendentes: `CampaignPlayer02.new_hn(seed, size)` (H2–H6; `new_h2` delega com resultado idêntico) e `simulate_cistern_sweep.py` com artefato reproduzível `replays/cistern_sweep_h2_h6.json`.
- Resultado (150 tentativas, seeds 1–30): vitórias certificadas H2 2/30, H3 1/30, H4 1/30, H5 0/30, H6 0/30. Gargalo dominante em H3+: retirada de emergência na Estação; em H2 também fome e falta de material para as etapas B/C. É medida do controlador fixo, não do equilíbrio. Detalhes em `PLAYTEST_REPORT.md`.
- Observação de design pendente de aprovação: lote indivisível de `ceil(C/4)` cartas chega a 4 em H6 e só cabe em herói sem equipamento. Nenhuma regra mudou.
- Verificação: 347 testes, `verify_campaign_player02.py` (seed 22 = 98 decisões, `verified_victory`), `verify_continuous_campaign.py`, `verify_regional_player.py`, `verify_pre_radio_celia_route.py`, `validate_data.py`, `simulate_cistern_sweep.py`, `compileall` e `git diff --check` passaram.
- Bloqueios do segundo arco inalterados (ver bloco seguinte): cartas de Viagem regionais, segunda pista, combustível e Evacuação. Próximo passo seguro sugerido: estratégia adaptativa da Cisterna (expedição de comida nos dias 4–5 com fundadores extras, vigias em cerco) medida pela mesma varredura.

# Estado ativo — desbloqueio regional, 2026-10-26

- Branch `evolucao/zona-zero-sistema-v1`; a retomada começou no HEAD `794749acc15118fc08f2a08090a6f0e0e7b97cbf`, igual ao remoto, árvore limpa antes das alterações desta rodada. Main e kit físico 0.2 permanecem intactos.
- Commit funcional desta rodada: `d2181c5` (`feat: apply regional hunger and prove physical clue route`); os documentos desta atualização registram o resultado e permanecem separados do código.
- `RULES.md §5` define rota curta 1+1 e longa 2+2 segmentos; `§11` (linha 64 na cópia atual) define 2 combustíveis por trecho para `EXP-VEI-02`. Ida/volta custa 4 na curta ou 8 na longa. Posto O1 oferece 8 combustíveis únicos; Posto O2 “um lote de cada provisão” significa Conserva e Água, sem combustível. `far=3` e `EXP-MIS-104=12` são experimentais. Cache da Oficina de 8 unidades também é apenas experimento: ação única, 2 PA, ruído alto, carga e risco de perda em emergência. Nenhuma decisão de regra foi feita nesta rodada.
- Grafo narrativo: a investigação física pré-rádio de Célia/Vicente remove o ciclo de ordem apenas quando essas identidades estão disponíveis. Seed 22 conclui uma visita à Estação com ações físicas de investigação + cópia das anotações de Célia, extrai exatamente 1 pista e retorna no segmento 10. Isso é prova da camada tática local; cartas de Viagem ainda não foram resolvidas. Célia não foi recrutada e o rádio recusa legalmente uma pista.
- Tentativa determinística de obter também a evidência de Vicente na mesma visita: ambos foram investigados, mas a cópia não foi alcançada; após ataques e pressão de Horda, a reserva de retorno fechou no clock 7 e a equipe não conseguiu extrair. É uma trajetória malsucedida do controlador, não prova de impossibilidade para todos os estados/estratégias. Fundador Célia ou Vicente já acolhido pode deixar apenas uma das duas fontes experimentais.
- Consumo regional agora aplica §8/§18/§25: uma porção de comida e água por consumidor, distribuição explícita e integral quando há escassez, condições persistentes, penalidade de PA, ferimento após segunda noite consecutiva de privação, limiar de colapso e alerta de cão condicionado à refeição. Save schema 1 migra aditivamente para schema 2; saúde/ferimentos mantêm equivalência sem curar por privação. Civil migrado sem campo de saúde recupera ferimento após refeição completa se descansou. Derrota parcial encerra a campanha com “Evacuação pendente”; a operação de Evacuação ainda não foi portada.
- O bug `run_objective()` que podia consultar o mapa depois da extração e lançar `KeyError` foi corrigido; o resultado de objetivo é mantido pelo controlador. Há prova de uma pista física da Célia em `edicao-integral/replays/pre_radio_celia_seed22.json` e a regressão seed22 de `A Cisterna` permanece `verified_victory` (5 dias/noites, 3 expedições, 98 decisões).
- Verificação desta rodada antes do commit: 340 testes passam; `verify_campaign_player02.py`, `verify_continuous_campaign.py --write` + replay, `verify_regional_player.py --write`, `verify_pre_radio_celia_route.py --write`, `validate_data.py`, `compileall` e `git diff --check` passaram. Esses testes não equivalem a campanha integral, simulação de equilíbrio, impressão física ou playtest humano.
- Próximo bloqueio: integrar cartas de Viagem e seus efeitos ao transporte regional, com emboscada e save/load, sem mapear implicitamente perto/médio/longe para curta/longa. Em seguida, encontrar uma rota reproduzível que obtenha duas evidências disponíveis, retorne, decifre o rádio e prove recrutamento/estoque. Combustível regional e Evacuação continuam sem decisão/implementação completa.

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
