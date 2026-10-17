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
