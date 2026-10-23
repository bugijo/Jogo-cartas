# Checkpoint — 23/10/2026

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
