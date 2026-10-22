# Auditoria inicial da prova pós-apocalíptica

**Histórico anterior aos lotes 10/11 e à revisão de campanha.** Para o estado vigente, leia [CAMPANHA_REPLAY_RELATORIO.md](CAMPANHA_REPLAY_RELATORIO.md), [COVERAGE_SUMMARY.json](COVERAGE_SUMMARY.json) e o [índice de impressão](../INDICE_IMPRESSAO_CONSOLIDADO.md). Os 39 IDs e módulos comuns apontados abaixo como pendentes já foram produzidos; mantenha este texto apenas para rastrear a auditoria inicial.

Matriz gerada por `python src/audit_final_proof.py` a partir do catálogo, seleção de impressão e verificações de lotes; consulte [CSV](COVERAGE_MATRIX.csv) e [resumo JSON](COVERAGE_SUMMARY.json). Os estados READY indicam arte/PDF de prova presente, não impressão física nem aprovação artística global.

Há 114 cartas selecionadas: 75 IDs com arte revista nos lotes 04, 06 e 07 e 39 ainda com arte anterior. Os 39 são VIN 12, VIA 12, HOR 9 e CER 6. Há cinco provas temáticas novas em seis destinos; condomínio só tem versão 0.6. Os quatro módulos comuns também ainda usam 0.6. Personagens: 24 fichas existentes, 18 retratos atualizados no lote 03. Existem 198 tokens no catálogo; a matriz exige revisão visual global deles, não os declara ausentes.

**Dependência de fabricação:** as 114 cartas não são todo o kit. A seleção omite intencionalmente REC e PRO: a edição Comece Aqui representa recursos por saldos numerados nos registros, e os projetos pela campanha/manual/painel. Os PDFs de `ABRIGO_MORADORES_ESTOQUE`, `REGISTRO_ADICIONAL`, `MORADORES_ADICIONAL`, guia, manual e campanha precisam entrar no pacote consolidado. Equipamentos iniciais embutidos nas fichas também não são cartas duplicadas. Esses componentes existem na edição 0.6, mas o pacote pós-apocalíptico ainda não está consolidado.

Gates abertos: condomínio, módulos comuns, 39 IDs de arte, QA visual global, conferência de PDF/contagem do pacote consolidado, auditoria lógica profunda e simulação reprodutível. Nenhuma nota 10/10 é justificada agora. A edição 0.6 e provas anteriores permanecem como fontes, sem alteração de regras ou equilíbrio nesta auditoria. Impressão física e playtest humano pendentes.

## Achados da revisão independente e correção localizada

- **HIGH:** os PDFs iniciais avaliam `ceil(H/2)` como 1, correto somente para H=2. A seleção inclui `ZC-VIA-0005`, `ZC-HOR-0007` e `0008`. Duas folhas substitutas, derivadas do texto canônico, agora fornecem 2 para H3–4 e 3 para H5–6. Ver [uso condicionado](../componentes-condicionais/LEIA.md). A edição anterior não foi modificada.
- **HIGH:** as 114 cartas não incluem os quatro Pés de cabra `ZC-EQU-0003..0006`, necessários para fundadores adicionais. Uma folha duplex com os IDs e efeitos canônicos foi gerada; a indexação para escolha livre de fundadores ainda precisa ser finalizada.
- **MEDIUM:** inventários anteriores registram pendências já resolvidas e sugestões de lote obsoletas. Esta matriz passa a ser a referência quantitativa; texto antigo permanece como histórico.
- **MEDIUM:** o `src/rules_engine.py` não simula expedições nem Monte Carlo. Nenhum número de partidas é alegado nesta fase.
