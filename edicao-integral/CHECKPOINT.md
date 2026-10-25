# Checkpoint de retomada — campanha contínua (25/10/2026)

Branch: `evolucao/zona-zero-sistema-v1`
Base recebida: `81a61e05f1cca494a32f961c2048c6d0927b6908`
Último remoto confirmado no início do lote: `5d83b3760edbf36b44ba821e14e50af8af9c896d`.
Commits funcionais publicados: `359ec46`, `cdc5b27`.
Main e kit físico 0.2 permanecem intactos.

## Estado corrente

- Cisterna H2 seed22 certificada: cinco dias/noites, três expedições, 98 decisões.
- Migração preserva arquivo integral com digest, estados sem equivalência em arquivo, e quantidades com equivalência no modelo regional. Idempotência e save/load cobertos.
- Bateria não coletada na Cisterna continua no O1 da Oficina; a coleta regional exige mapa, movimento, passagem pela porta e 1 PA.
- Posto ativo, oito cartas de combustível finitas; van canônica 6/12 com inspeção, Bateria e teste Técnica 6 por 2 PA. API antiga não recupera essa van.
- Busca regional migrada cobra 1 PA e exige encontro/área de busca. Cartão de acesso tem identidade única e só autoriza a missão quando volta ao abrigo.
- Replay parcial tem 62 registros resumidos após A Cisterna. Recupera Bateria, pega oito cartas, repara a van, volta gastando quatro cartas e fica com combustível 7. O percurso militar exige 12 pelo modelo canônico regional e falha sem mutação (déficit 5). `verified_victory` só foi emitido na Cisterna.
- Isso ainda não é campanha integral legal segundo todas as regras físicas: contato/recrutamento, relógio compartilhado, eventos e encontros do arco 2 seguem incompletos. Sem transmissor, defesa final, impressão física ou playtest humano.

## Bloqueio atual

A oferta modelada alcança no máximo 11 combustíveis (3 Oficina + 8 Posto) antes de retorno, menor que as 12 unidades da viagem `far=3` com van (2 por segmento, ida e volta). `data/last_transmission.json` ainda diz 6, em conflito com `RULES.md` §64. Nenhum valor foi mudado nem recurso injetado. Próxima tarefa: decidir/documentar a equivalência entre os arcos antes de prosseguir.

## Verificação e retomada

Os testes direcionados de Posto, migração, arco 2 e busca passaram antes da regressão final. Repetir tudo depois das mudanças: `python -m unittest discover -s edicao-integral/tests -q`, `python edicao-integral/verify_campaign_player02.py`, `python edicao-integral/verify_continuous_campaign.py`, `python edicao-integral/validate_data.py`, `python -m compileall -q edicao-integral`, `git diff --check`.

O restante deste documento é histórico de unidades anteriores e pode conter estados obsoletos. O estado atual é o resumo acima e `CAMPAIGN_INTEGRATION.md`.

---

## Unidade 30 — auditoria do avanço remoto e fechamento de atalhos

O remoto avançou de `0a0ab0d` para `8700073` e foi incorporado por
fast-forward. A camada `integrated_campaign.py` nova permitia criar Conexões,
Bomba e Membrana por chamada direta de `collect_part()` gastando apenas dois
segmentos, sem presença em destino, PA, teste, carga ou retorno. Também
aceitava `candidate_victory` para transição, descartava estado e concedia duas
pistas, enquanto `Arc2` seguia exigindo `cistern_record` verificado. A API agora
recusa coleta e transição até haver prova tática e migração completa; os IDs de
local das missões foram corrigidos para Oficina/Estação. Testes novos reproduzem
os atalhos antigos e confirmam o bloqueio. `TACTICAL_FUEL_AUDIT.md` registra
paridade canônica e decisões pendentes. Uma implementação isolada de expedição
0.2 está em andamento em `cistern_tactics02.py`; ainda não certifica vitória.

## Unidade 31 — expedição tática parcial e entrega comprovada

`cistern_tactics02.py` usa as seis plantas canônicas (16 zonas, 21 conectores,
cinco portas), cobra viagem e rodadas no relógio 0.2 e executa PA, movimento,
portas, ataque, ativação inimiga, Horda e saída. Oficina/Estação exigem presença
em O1/O2, PA, carga e teste da Bomba para retirar as peças. A camada integrada
salva/resta a expedição e só registra a peça após retorno legal; emergência não
entrega carga e limita a uma expedição por dia. `collect_part()` segue fechado.
Este lote **não** inclui ainda Saque, provisões, resgates, cartas de Viagem,
van/Posto ou estado persistente do mapa em revisitas; não permite campanha
completa nem `verified_victory`. Os testes experimentais cobrem o núcleo e
regressões de salvamento/entrega; suíte legada permanece sem alteração.

## Unidade 32 — provisões, Posto e oito políticas iniciais

`Tactical02.pickup_supply()` cobra PA em O1/O2, carga física por carta e os
lotes finitos da campanha; o integrador só acrescenta porções ao abrigo no
retorno e registra cartas perdidas na emergência. O Posto agora permite
inspecionar van, retirar até oito cartas únicas de Combustível, tentar reparo
com Bateria carregada e pagar duas cartas por trecho ao voltar com a van.
Combustível gasto não reaparece em revisitas. Um teste isolado do retorno com
van usa Bateria sintética **apenas para verificar contabilidade**; não é
campanha completa. A Bateria obtida legalmente na Oficina pode ser entregue e
alocada na expedição seguinte; isso ainda precisa de replay contínuo.

`player_policies02.py` contém oito **políticas programáticas**, com prioridades
de destino/equipe/rota, memória curta e escolha local pública básica. O agente
delegado que iniciou os testes de políticas atingiu limite de uso antes de
produzir o módulo; a implementação foi concluída pelo agente principal. Os
testes cobrem 40 escolhas iniciais reproduzíveis (oito perfis × H2–H6), não
partidas de cinco dias. Não houve simulação de campanha nem playtest humano.

Bloqueios para vitória certificada: busca de Saque, cartas Viagem e emboscadas,
resgates, encontros, estados de mapas em revisitas, promessas/eventos e fila
completa do abrigo; migração sem perda de 12 fundadores/civis/cães ao novo
motor; economia e veículo entre os dois arcos. Não iniciar produção de PDFs da
edição experimental com base neste checkpoint.

Um teste adicional percorre **ações no mapa**, sem teleporte, da Oficina no
dia 1 até a entrega da Bateria e do Posto no dia 2 até a volta com a van:
porta, movimento, inspeção, reparo com dado 6, quatro cartas de Combustível
retiradas por PA e pagas por dois trechos de rota longa. É uma trajetória fixa
favorável de duas expedições, não uma campanha de cinco dias nem estimativa de
equilíbrio. Outro teste isolado usa Bateria sintética apenas para exercer a
contabilidade de combustível. Fadiga 3 da emergência agora pertence à pessoa
e reduz uma unidade no amanhecer após refeição completa. A saída após a fase
de refeição foi bloqueada.

## Unidade 33 — Saque finito e estado de revisita

As seis cartas canônicas de Saque por destino são embaralhadas com semente
reproduzível. `search()` exige B1/B2, cobra 1 PA, um dos três usos do ponto e
no máximo uma busca do grupo por ponto/visita. A recompensa usa os dados de
`content/catalog.json`; se não couber na carga, fica registrada no chão e
pode ser recolhida por 1 PA. Saque, usos, chão, portas, inimigos e estado da van
persistem entre visitas e no salvamento. O abrigo só recebe cartas carregadas
após retorno legal; emergência perde carga comum sem repor o monte. Um teste
reproduz a busca no Mercado por ações de mapa e confere o delta exato de
Conserva, Água, Carne, Material, Munição ou Medicamento conforme a carta.

Isso ainda não fecha os cinco dias: faltam eventos de Viagem e emboscadas,
resgates/acolhimento ligados ao mapa, equipamentos achados, trabalho civil,
promessas e ordem completa de cercos, além da migração ao segundo arco.

Verificação desta unidade: 124 testes experimentais, 51 testes legados e
`validate_data.py` passaram; o aviso antigo de imagem não fechada em
`tests/test_boards06.py:64` permanece. O catálogo experimental tem 125 IDs,
sete cartas do novo motor e oito plantas táticas; as 36 cartas de Saque 0.2
são lidas do catálogo legado e **não** se tornam 36 novas cartas da edição
experimental. Nenhum PDF novo foi gerado. Os PDFs de referência enviados em
conversas anteriores não estão disponíveis em `/tmp/codex-remote-attachments`
nesta sessão; o acabamento físico não começou porque a campanha legal ainda
não foi comprovada.


Base preservada: `cebb76a` em `arte/kit-pos-apocaliptico-provas`. Nova branch: `evolucao/zona-zero-sistema-v1`. Branch padrão remota: `fisico/antes-que-a-agua-acabe`; nenhuma delas foi alterada por merge.

Estado: implementar e testar primeiro o núcleo determinístico independente. Fonte de dados em `data/core.json`, motor em `engine.py`, testes em `tests/`. A campanha, as habilidades individualizadas, os 15 NPCs completos, as 16 placas, os 12 interiores e a diagramação continuam pendentes. Não tratar as constantes desta pasta como regras aprovadas.

Próximo lote: revisar o design dos dez protagonistas e 15 NPCs com o proprietário após uma prova jogável; implementar cartas tipadas e validação de efeitos; conectar missões A Cisterna e Última Transmissão sem alterar a campanha 0.2. Só então construir a paginação A4.

## Unidade 2 — equipamento e espaço

Quatro instâncias-modelo de equipamento em `data/equipment.json`; bolsos, mãos, cabeça, tronco, pernas e grade de mochila testados. O motor impede sobreposição e uso sem mochila. O conteúdo continua experimental, sem cartas diagramadas ou distribuição de cópias. Oito testes próprios passaram; a suíte legada de 51 testes passou antes desta unidade (sem mudanças nos arquivos legados). Próximo passo: fechar regras de inventário e multiplicidade de cartas, antes da arte/impressão.

## Unidade 3 — catálogo e estado persistente

`data/system.json` é gerado de `data/build_system_data.py` e concentra 10 protagonistas com 70 habilidades tipadas, 15 NPCs nível 1–3, sete estruturas, cinco locais e cinco crises. `system.py` cobre capacidade de depósito e alojamento, recrutamento, projeto, trabalho, dano/reparo, busca com esgotamento, carga de expedição, viagens de equipes separadas, postos avançados, defesa com munição/visão, consumo/produção, crise com cooldown e salvamento com estado do PRNG. Dezoito testes novos passaram. Os textos de habilidade e custos ainda são hipótes de design da nova edição; nem cartas nem PDFs foram criados.

Lacunas da unidade: a maioria das tarefas de NPC sem saída de recurso ainda não possui efeito operacional; equipamentos de `engine.py` ainda não estão integrados ao estado de `system.py`; o gasto de PA/relógio tático, inimigos, eventos e campanha não estão implementados. A busca por localização é uma regra experimental que não modifica os seis mapas 0.2.

## Unidade 4 — integração e ensaio

Instâncias múltiplas de equipamento agora entram no `World` e no salvamento; mochila, slots e colisões são validados ao carregar. Recrutamento exige vaga e porções para a próxima refeição. Busca depende da expedição presente, carga tem limite de seis unidades por herói e só chega ao estoque no retorno. Postos avançados precisam de local esgotado, recursos e responsável. O ensaio `simulate_system.py` roda cinco dias para 2–6 heróis e grava resultado reproduzível em `ENSAIO_SISTEMA_20261023.json`; tabela e limites em `VALIDATION.md`. A preparação inicial H6 do ensaio excedia 30 unidades de armazenamento por uma unidade; reduzi materiais do **cenário de ensaio**, sem alterar capacidade/regra. Vinte e três testes próprios e 51 testes legados passaram. O bônus inicial de construção de Bento foi ligado a projetos; os demais bônus tipados ainda exigem integração.

Retomar por `python -m unittest discover -s edicao-integral/tests -q` e `python edicao-integral/simulate_system.py --seed 20261023 --seeds 100`. Não chamar esta evolução de edição jogável: faltam ações táticas, cartas/eventos, veículos, segundo arco, arte e impressão.

## Unidade 5 — veículos e ações das estruturas

O veículo recuperado na oficina volta com a equipe e requer combustível; viagens futuras reservam combustível de ida e volta. Oficina fabrica munição, enfermaria cura um ferimento e reservatório bombeia água, cada qual com custo e limite diário definidos no catálogo. Crises agora têm perdas e danos próprios, com cooldown e sem repetição enquanto ativas. Vinte e cinco testes experimentais passaram; o ensaio de 500 rotas foi regenerado e descrito em `VALIDATION.md`. Essas receitas e efeitos ainda são hipóteses da edição experimental.

Verificação final desta rodada: `git diff --check` limpo; 25 testes novos e 51 testes legados aprovados. Ensaio de 500 trajetórias reproduzido com semente inicial 20261023. O teste legado registrou apenas `ResourceWarning` de arquivo de imagem não fechado em `tests/test_boards06.py:64`; não há alteração no código antigo. Nenhuma impressão, partida humana ou campanha completa foi executada.

## Unidade 6 — validação cruzada

`validate_data.py` confirma 117 IDs globais únicos, atributos e 70 marcos, limites de NPC, referências de crises, custos, receitas e equipamento. Novo teste salva/restaura um estado combinado com dois heróis, NPC de defesa, equipamento na mochila, construção concluída, projeto em curso, crise ativa, posto avançado, busca, carga e veículo em retorno; o estado e o dia seguinte são idênticos após carregar. Total: 26 testes experimentais aprovados. O teste não transforma os perfis e missões pendentes em conteúdo jogável.

## Unidade 7 — equipamento em rodada

O estado experimental agora registra três ações por herói. Trocar equipamento durante combate custa uma ação; ataque com arma na mão rola D6 usando o PRNG persistente, retorna ruído, dano e durabilidade remanescente; armadura equipada absorve dano e perde durabilidade. Um teste salva/restaura no meio da rodada e confirma o mesmo dado seguinte. Vinte e sete testes experimentais passaram. Não há ainda alvo inimigo persistente, ativação de horda, portas, alcance ou consequência de ruído; portanto isto não é combate tático completo.

## Unidade 8 — equipe com NPCs

NPCs podem acompanhar expedição e deixam de produzir no abrigo enquanto viajam. Motorista reduz em um segmento a viagem com veículo (mínimo um); explorador acrescenta sua experiência a um achado existente, limitado pela carga, sem criar busca extra. Vagas de veículo incluem tripulação. O retorno restaura as posições de heróis e NPCs. Vinte e oito testes experimentais passaram. Permanecem a integração das 70 habilidades, as cartas imprimíveis, inimigos, missões e validação de equilíbrio.

## Unidade 9 — encontro tático de Mercado (experimental)

A geometria funcional de 16 zonas, 21 conexões, cinco portas, entrada, saída, surgimento e objetivos foi copiada do catálogo 0.2 para `data/tactics.json` sem mudar o kit anterior. `tactics.py` mantém posições, inimigos com vida, portas, ruído, hordas comuns/especiais/surpresa, perseguição por caminhos transitáveis, ataque e armadura; estado entra no salvamento do mundo. Retirada exige voltar à saída e fechar o encontro, registrando inimigos restantes. Seis testes táticos e 34 testes novos ao todo passaram. Isto é apenas um encontro experimental, sem campanha ou cartas prontas.

## Unidade 10 — ciclo de um dia e cartas estruturadas

`campaign.py` usa as duas cartas de `data/cycle_cards.json` para executar e salvar um dia completo no Mercado. A busca no encontro exige um herói vivo em zona marcada; retirada por quebra de equipamento não contabiliza busca. `simulate_cycle.py` executou 1.250 replays de um dia para H2–H6 e cinco estratégias, com zero divergências de restauração. Ver `CYCLE_REPORT.md` para resultados e limitações: ainda não é campanha completa ou balanceada. `validate_data.py` confirmou 119 IDs e conectividade da planta. Quarenta e dois testes experimentais passaram nesta unidade.

## Unidade 11 — 70 marcos ligados ao motor

Os 14 tipos de bônus presentes nos 70 marcos agora têm operação concreta em `system.py`/`tactics.py`: enfermaria, reservatório, resgate, guarda, ataque, ruído, infecção, viagem, busca, reparo, obra, fabricação, horta e depósito. Os textos do catálogo foram tornados específicos. O teste percorre todos os limiares de XP e os testes de contexto exercitam os principais efeitos. Quarenta e sete testes experimentais passaram; os 1.250 replays do cenário de um dia permaneceram byte a byte iguais. Ainda faltam escolhas ramificadas nas árvores e avaliação humana/balanceamento.

## Unidade 12 — persistência de locais e XP por expedição

Retirada arquiva inimigos, portas e horda pendente por local; revisita restaura o mapa com entrada renovada dos heróis. Salvamento entre visitas preserva isso. O limite de 8 XP de combate agora persiste por toda a expedição, inclusive entre dias, e zera no retorno. `PROVA_CICLO_17.json` demonstra um ciclo com resultado de missão e hash idêntico após restaurar. Quarenta e nove testes experimentais passaram; os 1.250 ensaios agregados permaneceram iguais.

## Unidade 13 — portões do segundo arco

`arc2.py` executa código de rádio, cartão de acesso, entrada com furgão/combustível e transporte de transmissor único, com flags e carga salvas. `data/last_transmission.json` contém cinco cartas; a defesa final está marcada pendente e lança erro explícito. Um sexto destino regional abstrato foi adicionado, sem mapa local. `validate_data.py` confirma 125 IDs e sete cartas experimentais. Cinquenta e dois testes novos passaram; os 1.250 replays do cenário de um dia permaneceram iguais. O capítulo 0.2 continua intocado. `ARC2_STATUS.md` descreve limites.

## Unidade 14 — percepção dos inimigos e preparação física

A ativação zumbi agora persegue heróis apenas dentro de alcance e linha de visão, ou ruído médio/alto; um teste reproduz o zumbi parado sem pista e em movimento após ruído. Cinquenta e três testes experimentais passaram e os 1.250 replays agregados permaneceram byte a byte iguais. `PRINT_PREP.md` registra as medidas de cartas e a divisão preliminar das 16 placas de 20 × 20 cm em 32 metades A4; nenhum PDF, arte de placas ou molde de caixa foi produzido. O kit 0.2 segue intacto.

## Unidade 15 — gate militar sem atalho

`World.open_expedition` agora recusa ida direta à instalação militar sem código, cartão, autorização de missão e veículo. `Arc2.authorize_installation` abre o gate com rollback da flag se a viagem falhar. O teste do atalho falhou antes da correção e passou depois. Cinquenta e quatro testes experimentais e 51 testes legados passaram. A suíte legada registrou apenas `ResourceWarning` preexistente em `tests/test_boards06.py:64`. Os 1.250 replays de um dia permaneceram idênticos. O estado segue incompleto para campanha total e impressão.

## Unidade 16 — defesa final experimental

`Arc2.final_defense` abre defesa no abrigo apenas após os portões narrativos e retorno do transmissor. O mapa funcional `camp_final` tem quatro zonas; três ondas catalogadas, movimento, ataques, integridade do objetivo, vitória, derrota, retirada e salvamento foram implementados. Foram aprovados 57 testes experimentais e o validador confirmou 125 IDs, sete cartas e dois mapas táticos. A prova de vitória isolou a progressão das ondas e **não** equivale a uma vitória tática completa. Faltam mapa militar local, ligação canônica com A Cisterna e prova de viabilidade dos equipamentos contra todas as ondas. A edição 0.2 permanece intacta.

## Unidade 17 — instalação militar explorável

`military_installation` é uma planta funcional de 16 zonas, objetivo 6 e porta 2–6. O transmissor exige encontro ativo, herói vivo com PA no objetivo e zona livre, com custo de uma ação; o mapa militar não pode ser substituído pelo Mercado. O cartão da estação exige busca feita pela expedição atual, eliminando um atalho por busca anterior de outra equipe. Foram aprovados 59 testes experimentais; o validador confirma três mapas táticos e 125 IDs. Falta arte/PDF e prova completa de campanha.

## Unidade 18 — defesa, ensaio isolado e fronteira de compatibilidade

Inimigos da defesa agora ferem heróis ao alcançar qualquer zona ocupada, com armadura e possível infecção; o transmissor perde integridade apenas quando eles chegam à zona 1. Salvamentos rejeitam inimigos fora da planta. `simulate_defense.py` gerou 250 defesas reproduzíveis (H2–H6, 50 sementes). O relatório documenta resultados e pré-condições injetadas; nenhum equilíbrio foi alterado. `CAMPAIGN_INTEGRATION.md` registra diferenças materiais entre o capítulo 0.2 e o motor novo. Não marque A Cisterna como implementada nem use a flag externa como prova de vitória. Próxima unidade: portar preparação, porções, relógio e etapas do filtro com testes de paridade antes de ligar os arcos.

## Unidade 19 — evento único e lacuna de combustível

A carta `EXP-EVT-001` agora é marcada globalmente no estado da campanha; criar outra expedição não repete o prêmio. Um teste reproduz o antigo atalho e confirma a correção. Sessenta e quatro testes experimentais passaram e os 1.250 replays de um dia ficaram byte a byte iguais. Inspeção do catálogo encontrou outro bloqueio para campanha sem recursos injetados: Oficina tem só três buscas renovação urbana, cada uma com um combustível; recuperar o furgão médio consome dois e a ida e volta militar exigem seis. O estoque inicial de combustível não está definido por uma preparação de campanha. Não foi criado combustível nem alterado custo em silêncio; a preparação e fontes legais precisam ser definidas antes de declarar o arco executável integralmente.

## Unidade 20 — gerador reproduzível e plantas canônicas

`data/build_tactics_data.py` agora reproduz os oito registros de `tactics.json`: seis plantas extraídas do catálogo 0.2 sem mudar zonas, 21 conexões, portas, bloqueios, buscas, objetivos, entradas ou saídas; mais perímetro e instalação militar experimentais. Mercado, Hospital, Oficina e Estação têm destino regional; Posto e Condomínio são apenas referências até existir conteúdo correspondente no motor e são recusados como encontros. O teste compara todas as seis plantas, inclusive bloqueios, com `content/catalog.json`. Sessenta e seis testes experimentais passaram. A geometria portada não equivale a missões, recursos ou regras do capítulo 0.2 portados.

## Fechamento da rodada

Após as unidades 16–20 e o bloqueio de avanço de dia durante defesa ativa: 66 testes experimentais e 51 testes legados aprovados. O único aviso legado é `ResourceWarning` preexistente em `tests/test_boards06.py:64`. `validate_data.py` confirma 125 IDs únicos, sete cartas experimentais e oito plantas funcionais (duas experimentais; duas do catálogo apenas como referência sem destino regional). Os 1.250 replays de um dia ficaram reproduzíveis; 250 defesas isoladas constam do relatório. Não houve replay de campanha completa, impressão, PDF novo ou playtest humano. Não alterar a flag de Cisterna para fingir integração; a próxima implementação deve portar as regras oficiais e fechar a economia do segundo arco.

## Unidade 21 — núcleo canônico parcial do capítulo 0.2

`cistern02.py` lê diretamente os IDs dos 12 heróis iniciais e dos 12 Vínculos do catálogo original. Um teste varre as 2.497 combinações H2–H6 e compara humanos, cães, consumidores, barracas e cartas iniciais de quatro porções. Há consumo por lotes, vencimento de carne, relógio de dez segmentos, reserva de peças apenas no dia seguinte, trabalho sequencial A/B/C com limite dois/dia, enchimento único de 2C, produção posterior de C e salvamento JSON. Os testes rejeitam refeição duplicada, dia sem refeição e trabalho parcialmente inválido. **Isto não constitui A Cisterna jogável:** faltam destinatários individuais de privação, expedição com custo de PA, obtenção comprovada das peças, resgates, cercos, resultado da noite e vínculo com `World`. `receive_part` é entrada de teste/registro, não prova de coleta. Não marcar `cistern_complete` por este estado parcial.

## Unidade 22 — refeição por pessoa e cerco parcial

Cada fundador, civil, criança e cão da preparação agora tem estado individual. `meal()` consome porções de carne, conserva e água em prioridades escolhidas pelo grupo, vence a carne, marca Fome/Sede, conta noites consecutivas, fere humanos desde a segunda privação e zera Saúde no limiar de Colapso; cães perdem/recuperam alerta. O abrigo registra Moral, Saúde, Pressão e fila; o modelo de Cerco valida vigias planejados, dados, no máximo duas munições, defesa, dano a estruturas e perda de porções. Estes cálculos têm testes específicos, mas **não há ainda fluxo completo de fases**: força de carta, alocação de civis, resgates, intenções, fila de Noite de segurança e expedição 0.2 continuam pendentes. Não transferir vitória à Última Transmissão com esse estado incompleto.

## Unidade 23 — acolhimento e intenções, ainda sem contato tático

O estado canônico parcial registra grupos inteiros de oito encontros existentes, recusa acolhimento acima das duas vagas temporárias, cobra ajuda por humano, mantém recusa sem punição e sorteia Intenção por semente no acolhimento. A fase noturna revela na segunda noite ou após duas investigações, aplica roubo/Pressão somente sem Verificado atual, retira grupos que partem e cobra superlotação desde a terceira noite. Setenta e nove testes experimentais passaram. **Limite:** `rescue()` é chamada diretamente; não prova contato em O1/O2, custo de PA, carga/retorno ou trabalhador realmente disponível para investigar. O estado ainda não autoriza a transição entre campanhas.

## Unidade 24 — paridade independente da preparação

O teste das 2.497 combinações H2–H6 agora compara os resultados de `cistern02.py` com o oráculo legado `src/rules_engine.py` além das fórmulas do manual. A leitura do catálogo 0.2 segue direta e os PDFs/regras originais permanecem intocados. Próxima prioridade: ligar objetivos e carga ao relógio e ao mapa sem substituir PA, portas ou dados da edição 0.2 por valores experimentais.

## Unidade 25 — ordem mínima das fases noturnas

O estado 0.2 recusa avançar o dia sem refeição, com cerco ainda não resolvido naquela noite, ou com intenção/superlotação pendente de grupo ativo. Cerco precede trabalhos e refeição; trabalhos precedem a refeição. Isto fecha atalhos de consumo e revelação, mas não implementa o relógio de expedição inteiro nem os eventos fixos dos cinco dias. O teste experimental atual tem 80 casos aprovados.

## Unidade 26 — encerramento provisório e portão fail-closed

`Cistern02.close_chapter()` só calcula `candidate_victory` ou `partial_defeat` após a refeição do dia 5 e a resolução dos cercos pendentes, incluindo Noite de segurança sem nova produção. Uma vitória candidata não certifica a origem das peças, nem promessas. `Arc2.decode_radio`, acesso militar e defesa final agora rejeitam a antiga flag `cistern_complete`; exigem um certificado `verified_victory` que o motor parcial **não emite**. As provas isoladas de Última Transmissão e o ensaio de 250 defesas usam fixture sintética explícita. Isso impede declarar campanha completa por injeção de flag, mas deixa a transição normal bloqueada até implementar exploração/objetivos e prova integral do capítulo. O conjunto experimental tem 83 testes passando.

## Unidade 27 — bloqueio de combustível reproduzido

Novo teste percorre todas as três buscas de combustível da Oficina, retorna, recupera o furgão e confirma saldo de uma unidade, insuficiente para as seis exigidas na viagem militar. `CAMPAIGN_BLOCKERS.md` registra a evidência e a adaptação proposta do Posto canônico sem aplicar recurso extra. O sistema segue fail-closed: não há emissor de `verified_victory`, portanto nenhuma campanha completa sem injeção foi demonstrada. O conjunto experimental tem 84 testes aprovados; suíte legada final ainda em execução neste checkpoint.

## Unidade 28 — cinco dias reconciliados com replay legado

`replay_cistern02_fixed.py` importa o replay tático antigo e projeta as entregas realmente registradas por ele no estado novo. H2–H6 completam cinco dias com saldos idênticos de comida, água, Materiais, Pressão e filtro; o resultado fica em `REPLAY_CISTERNA_FIXO.json`. São cinco trajetórias **fixas**, todas sem acolher Bia e com dados favoráveis, que produzem apenas `candidate_victory`. Não emitem certificado da campanha nem desbloqueiam o arco seguinte. O conjunto experimental tem 85 testes aprovados. A expedição tática ainda não foi portada ao motor novo.

## Unidade 29 — dano e reparo do filtro

O filtro concluído agora pode ser alvo de cerco. Dano o desativa; reparo consome 2 Materiais e um trabalho antes da refeição, sem repetir o enchimento único. O novo teste cobre dano e reparo; os cinco replays fixos continuam byte a byte iguais. `CAMPAIGN_BLOCKERS.md` também explicita a contradição entre 12 fundadores possíveis no kit 0.2 e dez protagonistas no motor experimental. O conjunto experimental tem 86 testes aprovados.
