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
