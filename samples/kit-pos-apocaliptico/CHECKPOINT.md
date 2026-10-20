# Provas de direção pós-apocalíptica
Base: 48f5794. Branch: arte/kit-pos-apocaliptico-provas. Sem publicação autorizada.

Lote 1: três edições nativas produzidas com image_gen integrado: seis retratos, suprimentos e atlas da oficina. Arquivos anteriores preservados. Rostos comparados visualmente; pequenas diferenças de traço persistem, portanto provas, ainda não substituição do kit.

Próximo passo: integrar em fichas, cartas duplex e oficina usando geradores existentes; folha de inimigos com arte preservada; renderizar e conferir texto, geometria e resolução. Nenhuma impressão física realizada.

Lote 2: quatro provas integradas e renderizadas (6 retratos + 6 fichas, três inimigos preservados, nove cartas duplex, oficina em quatro A4). Água ganhou fonte isolada para remover fragmento do atlas. 39 testes existentes aprovados. Textos das fichas/cartas e vetores da oficina iguais aos anteriores. Oficina ainda não atinge a continuidade arquitetônica do Mercado; não aprovada como acabamento global. Próximo lote: hospital, identificado como excessivamente limpo no inventário visual.

Lote 3: hospital integrado em quatro A4. Primeira saída com fundo opaco rejeitada e preservada para rastreio; segunda corrigida. Todos os PDFs e comparações renderizados. Validação direcionada concluiu igualdade de texto/geometria, verso idêntico, fontes incorporadas, A4 e remontagem. Fontes de jogo continuam byte a byte iguais a 48f5794. Fetch confirmou origin/arte/mercado-amostra-ilustrada em 48f5794, sem sucessor naquele ramo.

Estado de entrega: 7 PDFs de prova, 17 páginas, 16 folhas se imprimir tudo (incluindo duas folhas comparativas). As quatro provas iniciais precisam de 7 folhas. Não é uma nova edição do jogo. Apenas 6/24 retratos tratados; inimigos preservados; 9/114 cartas na prova; dois cenários com materiais revisados. Composição arquitetônica desses cenários ainda abaixo do Mercado B e hospital com sobreposição decorativa herdada. Peões e demais componentes não substituídos.

Retomada exata:
1. Ler README.md, ASSET_MANIFEST.md e VISUAL_QA.md desta pasta; não refazer as gerações aprovadas neste lote.
2. Executar `python samples/kit-pos-apocaliptico/fontes/build.py` e depois `python samples/kit-pos-apocaliptico/fontes/validate.py` somente quando houver alteração de fontes.
3. Próximo lote: recepção do hospital e condomínio. Congelar geometria canônica; a sobreposição das cadeiras com a mesa é decoração, não porta nem zona. Corrigir na fonte artística isolada, sem mudar regras ou espaços funcionais.
4. Prosseguir aos 18 retratos restantes e aos peões correspondentes, comparando faces; não aplicar este atlas de seis retratos às outras pessoas.
5. Atualizar resolução e páginas de prova após cada lote. Sem push/publicação/merge: instrução vigente do proprietário.

Sem impressão física ou playtest. Não há execução em segundo plano após esta entrega.
