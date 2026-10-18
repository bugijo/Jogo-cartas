# Retomada atual — edição 0.2 — 18/10/2026

Base auditada: db67f42, limpa, sem commits posteriores. Tag preservado/prototipo-0.1-db67f42. O ZIP antigo e PDFs 0.1 foram preservados.

Tarefa concluída nesta rodada: revisão focada dos cinco dias; dez profissões consolidadas; kit Comece Aqui — Duas Pessoas. Nenhum conteúdo de jogo novo. Fonte do kit: src/build_starter.py e content/starter/01_guia.json. Índice e contagem: output/comece-aqui-duas-pessoas/LEIA-ME.md e manifesto.json. Inicial 25 folhas, complemento 33, total 58.

Referências correntes: RULES.md, CAMPAIGN.md, PROFISSOES.md, REVISAO_0.2.md; catálogo 0.2 com mesmos IDs. PDFs completos revisados em output/revisao-0.2, sem substituir os PDFs 0.1.

Reproduzir: python src/make_content.py; ZC_OUTPUT_DIR=/workspace/zona-zero-comunidade/output/revisao-0.2 python src/build.py; python src/build_starter.py; python -m unittest discover -s tests -v; python src/review_five_days.py; python src/validate_starter.py; python src/render_starter.py. O replay é uma trajetória de dados conhecidos, não equilíbrio ou playtest.

Sem impressão física ou teste humano nesta rodada. Próxima atividade recomendada é imprimir o inicial, medir calibração e jogar o primeiro dia com duas pessoas, anotando dificuldades. Não gerar novas cartas, regras ou arte sem nova instrução. Novo hash em COMMIT_0.2.txt dentro dos ZIPs ou git log -1.

---

## Checkpoint anterior preservado

# Checkpoint de retomada — 17/10/2026
Workspace independente: /workspace/zona-zero-comunidade
Branch: fisico/antes-que-a-agua-acabe. Repositório local novo; nenhum jogo digital foi alterado. Sem push.

## Estado por ciclo
1. Auditoria concluída: PDF principal lido, 17 páginas; cópia e extração em sources/. Kit antigo não fornecido, opcional. Decisões D01–D10 em GAME_DESIGN.md.
2. Protótipo editorial produzido: manual, capítulo completo, catálogo com 324 cartas, 24 heróis e regras próprias de combate. Mutirão inicialmente proposto foi removido; todos podem permanecer trabalhando, dois trabalhos por projeto/dia.
3. Arte parcial produzida e integrada: capa +24 retratos +4 ameaças +9 objetos +9 construções +8 encontros, sete pranchas PNG; manifesto JSON. Faltam seis artes de peças/estruturas e ambientação final dos mapas. Dez profissões são propostas marcadas.
4. Abrigo, mapa geral, quatro módulos locais e seis diagramas funcionais produzidos. Portas fora de emendas; conectividade verificada. Todas as montagens usam rotação 0°.
5. PDFs gerados: cartas completas/econômicas; fichas; painéis; mapas; tokens; organização; calibração; galeria. Regimes de impressão em PRINT_GUIDE. Fontes editáveis no repositório.
6. Verificação digital concluída nesta versão: nove testes, 37 verificações, páginas renderizadas, inspeção de contatos/amostras e revisão independente. Impressão e playtest humano não executados. Relatório em VALIDATION_REPORT.md. Não é caixa final.

## Retomar sem repetir
1. Abra README.md, VALIDATION_REPORT.md e consulte git log --oneline. Não gere arte já existente.
2. Se conteúdo mudar, edite src/make_content.py (fonte central de dados), RULES.md e CAMPAIGN.md; regenere catálogo e PDFs. Não edite somente JSON gerado, pois make_content o sobrescreve.
3. Execute comandos de regeneração do README; compare output/validation.json e unittest. Arte não exige credenciais.
4. Prioridade seguinte: imprimir calibração, montar mapa e jogar campanha solo com dois heróis sem acompanhantes. Depois casal, quatro e seis participantes. Registrar problemas em PLAYTEST_PLAN.
5. Rever profissões propostas somente se nova fonte for fornecida. Não substituir automaticamente regras por kit antigo.
6. Após testes, revisar curva econômica/tática e progressões; concluir ambientações e artes listadas no manifesto; gerar nova versão e nova inspeção. Não afirmar validação humana antes de ocorrer.

Histórico completo acompanha history.bundle; restaurar em uma pasta nova com git clone history.bundle zona-zero-retomada. COMMIT_LOG.txt lista hashes finais. Nenhuma tarefa fica rodando após a entrega.

## Produção artística 0.3 — ciclo 1
Branch arte/pnp-edicao-ilustrada-v0-3 criada de 9c38aa5, árvore limpa e origem conferida. Nenhum trabalho posterior remoto na base. Leitura dos geradores, catálogo, regras, campanha, guia e manifesto; sete pranchas auditadas visualmente. Capturas anteriores em output/edicao-ilustrada-v0.3/evidencias/antes_*.png; hashes da base em baseline.json. Amostras reais em amostras/ (mapa, abrigo e cartas), revisadas: trocar ícones das estruturas por ilustrações preservadas; ampliar arte em cartas curtas. Sem alteração de regras. Próximo: concluir mapas e montagem digital, integrar demais componentes e conferir ambas edições.

### Ciclo 2 — mapas
Quatro módulos comuns e seis montagens ilustradas gerados nas duas edições; seis variantes temáticas opcionais em extras/. Prancha nova com 16 objetos ortográficos integrada. Arte por zona mantém os eixos de passagem livres. Geometria separada conserva 14 mm nas aberturas, paredes, 16 zonas e posições de entrada/buscas/objetivos/surgimento. Mapas montados e junções em evidencias/; revisão ampliou números dos diagramas para 8 pt, diferenciou portas/bloqueios e manteve todos fora de emendas. Versão econômica já usa arte em cinza, sem recontar ou excluir componentes. Próximo: substituir o painel por cena contínua do abrigo e terminar fichas.

### Ciclo 3 — abrigo e fichas
Cena contínua original do abrigo integrada, com quatro barracas, cozinha, depósito, cisterna danificada, portão e expansão; etiquetas e todos os indicadores ficam em vetor e campos brancos para lápis. A planta é ilustrativa e não cria adjacências. Quatorze fichas do kit refeitas com os mesmos retratos, atributos, habilidades e evolução; 24 fichas existentes disponíveis como extra de 12 folhas. Quatro espaços de carga e estados individuais preservados; pés de cabra únicos continuam nas duas fichas iniciais. Inspeção corrigiu largura de etiquetas das barracas. Nenhum estouro de parágrafo no build. Próximo: finalizar cartas, marcadores e edição econômica.

### Ciclo 4 — cartas e marcadores
As 114 cartas selecionadas receberam nova composição, com títulos e arte maiores quando o texto é curto. Todos os efeitos foram comparados por ID ao catálogo; a seleção de dois heróis mantém a avaliação original ceil(H/2)=1. Vínculos, Intenções, armas, peças, saque e encontros têm arte; cartas de viagem agora têm cenas/sinais próprios em vez de repetir uma van. Versos por família e Intenções sem qualquer ID externo. Os 45+12 marcadores e as 12 divisórias preservam quantidades; funções usam símbolos próprios. 14 testes existentes passaram; 1422 verificações digitais passaram (conteúdo, A4, fontes usadas incorporadas, geometria e dimensões, texto preservado e seleção). Não houve impressão física. Próximo: acabamento econômico, contato de todas as páginas, sobreposição duplex, inventário, ZIPs e push.

### Ciclo 5 — PDFs, prova e entrega 0.3
Concluídos os cinco ciclos. Regras/catálogo/guia/seleção 0.2 e geradores antigos sem diferenças em relação a 9c38aa5. Edições em output/edicao-ilustrada-v0.3/ilustrada e economica: cada uma 18 PDFs, 72 páginas e 58 folhas (25+33). Extras separados: 24 folhas de mapas temáticos e 12 de fichas por edição, todos opcionais.

1423 verificações digitais passaram; 14 testes existentes passaram. Renderizadas 216 páginas, conferidos os 10 contatos, montagens e junções, ficha, maior texto, versos mistos, marcador, divisórias e calibração. As 108 páginas econômicas são cinza. Versos de Intenção comparados por imagem em posição normalizada: mesmos sinais, sem identificação externa. Não houve impressão física ou playtest humano. Não houve reequilíbrio nem expansão.

Fontes: src/build_illustrated.py + src/illustrated_art.py, catálogo/seleção 0.2, assets originais e assets/v0.3. Três pranchas novas (23 regiões) e derivação transparente dos objetos, SVGs auxiliares. Recortes de pranchas antigas corrigidos por coordenadas, sem editar originais. Inventário em content/asset_manifest_0.3.json, relatório em VISUAL_QA.md. Referência Drive foi listada, mas atalho ZOMBICIDE não pôde ser lido (403); nenhuma imagem dessa pasta foi copiada.

Reproduzir: python src/build_illustrated.py --cycle 5; python src/document_illustrated.py; python src/export_vectors.py; python src/validate_illustrated.py; python src/check_duplex_visual.py; python src/visual_qa.py; python src/package_illustrated.py. Não executar geradores antigos sobre os PDFs 0.3. Não precisa chamar geração de imagem: assets estão incluídos. Arte econômica é derivada pelo gerador.

Retomada: conferir git log e git status, abrir índices IMPRIMA-ESTES.md e VISUAL_QA.md; imprimir calibração e uma folha de cada componente para prova doméstica. Depois ajustar apenas problemas observados. Branch própria arte/pnp-edicao-ilustrada-v0-3, sem merge na anterior. ZIPs básicos excluem fontes, extras, caches e relatórios. Fontes, extras e provas têm pacotes separados. Histórico anterior preservado. Nenhuma atividade fica em segundo plano após encerrar.

## Fabricação 0.4 — ciclo 1
Base ccff9c8 conferida e preservada. Branch arte/pnp-fabricacao-v0-4. Não existe candidata 0.4 anterior no checkout ou remotos. Cinco PDFs avulsos de referência recebidos (seis páginas), todos renderizados e visualizados. ZIP mencionado ausente. Observações e decisões em docs/PRODUCAO_0.4.md; hashes imutáveis em content/production/baseline_0.4.json. Referência privada fica fora do repo. Próximo: templates e cartas, peões, painel opcional e cenas contínuas.

### Fabricação 0.4 — ciclo 2
Template real gerado em output/edicao-fabricacao-v0.4/amostras; nove cartas representativas, sem estouros. Contratos de 58/72 folhas, pareamento manual sem espelhamento, quatro slots reais, base e limite de inimigos testados RED→GREEN; suíte 19/19. Pequenos valores vêm apenas de catálogo existente. Correção de enquadramento do encontro preserva o rosto inteiro. Próximo: aplicar à seleção e comparar conteúdo impresso.

### Fabricação 0.4 — ciclo 3
114 cartas diagramadas e alternativas manual/duplex geradas, com 456 comparações de efeitos aprovadas. Uma quebra de linha da Espingarda foi corrigida medindo a altura tipográfica, sem diminuir fonte. Peões e mapas estão em produção independente. Assets novos em assets/v0.4; originais não alterados. Próximo: integrar peões/painel e cenas, unificar índice e validar todas as saídas.


## Fabricação 0.4

Base ccff9c8; branch arte/pnp-fabricacao-v0-4. Ciclos 1–6 implementados. Referência disponível: cinco PDFs/seis páginas; zombecide.zip não recebido. Não copiar material privado /tmp/zz-referencia-privada. Gerar com python src/build_fabrication.py --step all; conferir com python src/validate_fabrication.py; provas com python src/proof_fabrication.py; pacotes com python src/package_fabrication.py. Finalização: rever branch inteira, corrigir achados importantes, registrar revisão, empacotar e fazer push sem merge.

Ciclo 7: revisão independente concluída, dois problemas de fabricação corrigidos com testes RED→GREEN; suíte 21/21. 1.922 verificações digitais e 300 páginas renderizadas sem falhas. Fontes sendo reconstruídas em /tmp/zz-fontes-reconstrucao-04; seguir DOWNLOADS_0.4.md. Pacotes em dist/ZZ_04_*; fontes completas locais acima do limite do GitHub são substituídas por cinco ZIPs extraíveis no mesmo diretório. A edição ilustrada completa já cabe num ZIP menor que 100 MB após exportar somente cenas opacas a JPEG 95, sem reamostragem.

Ciclo 7 concluído: cinco ZIPs de fontes extraídos em pasta limpa, build --step all, validação e provas executados na sequência documentada. Resultado: 1.922/1.922, 300 páginas e 23 evidências; suíte 21/21 no projeto. Índices de navegador por pacote, ZIPs testados sem erro, sem referência privada/cache Python. Reconstrução registrada em output/edicao-fabricacao-v0.4/reconstrucao.json. Entrega por DOWNLOADS_0.4.md; todas as opções completas de jogo cabem no GitHub. Não houve impressão física, montagem física ou playtest humano. Próxima ação após commit: push -u origin arte/pnp-fabricacao-v0-4 e conferir links remotos, sem merge.
