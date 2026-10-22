# Retomada mais recente

## Atualização 2026-10-21 — lotes 10/11 e seleção digital

Lote 10 concluiu a revisão artística das 39 cartas pendentes e gerou os dois PDFs duplex/pares para recortar e colar. Lote 11 produziu os quatro módulos comuns contínuos em quatro A4. Ambos os lotes têm comparações, fontes e verificações próprias. A seleção sem duplicação de folhas está em `kit-final-prova/INDICE_IMPRESSAO_CONSOLIDADO.md`; a auditoria reproduzível fica em `src/final_kit_audit.py` e `kit-final-prova/auditoria/FINAL_KIT_AUDIT.json`. O relatório de limites fica em `kit-final-prova/RELATORIO_FINAL_PROVA.md`. Próxima tarefa: replay completo H=3–6 com resgates e componentes físicos, impressão e playtest humano. Não declarar a caixa final aprovada.

## Atualização 2026-10-22 — revisão da campanha

`src/build_campaign_report.py` reproduz 15 ensaios de fases de cinco dias com sementes H=2–6 e registra o replay tático antigo em `kit-final-prova/auditoria/CAMPANHA_REPLAY_RELATORIO.md`. Todos os vínculos de H=2–6 cabem; folhas condicionais e suporte impresso foram conferidos. O roteiro Lia/Ivo só é tático para H=2; com os inimigos iniciais de H=3–6, falta 1 PA a Lia no Mercado/rodada 4. Isso exige novo roteiro para os heróis adicionais, sem alterar dificuldade. Guia de preenchimento do registro H3–6 atualizado. Sem impressão física nem playtest.

Atualização do mesmo lote: `src/scaled_tactical_replay.py` acrescentou um roteiro novo com Caio para H3–6, Hordas `Aglomerado` escaladas, busca do Mercado e resgate de Bia em H2–5. Cinco trajetórias fixas de cinco dias chegaram à vitória sob dados/ordem favoráveis. O bloqueio acima pertence **somente ao roteiro antigo**, preservado como diagnóstico. Efeitos alternativos e equilíbrio permanecem sem validação.


Ver [LOTES_02_04.md](LOTES_02_04.md). Não repetir hospital, oficina, 18 retratos ou 24 peões. Próximos: estação, posto, condomínio, módulos comuns e 76 cartas ainda não revisadas. Publicação dos checkpoints novos deve ser conferida no remoto.

---

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

## Atualização vigente — auditoria final e lote 09

As restrições antigas de não publicar foram substituídas pela autorização posterior do proprietário para publicar esta branch. Últimos lotes em `lote-04-cartas/` até `lote-09-condominio/`; o condomínio está em quatro A4 com 16 zonas/21 conexões e sete correções localizadas de passagens. As seis localidades da campanha têm agora provas artísticas, mas os quatro módulos comuns ainda são da edição 0.6. A matriz em `kit-final-prova/auditoria/` registra 75/114 cartas selecionadas com arte revisada e 39 pendentes. Folhas condicionais H3–H6 e reposições VIA/HOR existem em `kit-final-prova/componentes-condicionais/`; uma folha universal agora contém os seis IDs de pé de cabra para qualquer escolha de fundadores, mas o índice completo por número de participantes ainda falta. Próximos lotes: módulos comuns, 39 cartas, consolidação do kit e simulação de regras. Não declarar caixa concluída. Impressão física e playtest humano não ocorreram.
