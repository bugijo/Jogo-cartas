# Auditoria inicial da prova pós-apocalíptica

Matriz gerada por `python src/audit_final_proof.py` a partir do catálogo, seleção de impressão e verificações de lotes; consulte [CSV](COVERAGE_MATRIX.csv) e [resumo JSON](COVERAGE_SUMMARY.json). Os estados READY indicam arte/PDF de prova presente, não impressão física nem aprovação artística global.

Há 114 cartas selecionadas: 75 IDs com arte revista nos lotes 04, 06 e 07 e 39 ainda com arte anterior. Os 39 são VIN 12, VIA 12, HOR 9 e CER 6. Há cinco provas temáticas novas em seis destinos; condomínio só tem versão 0.6. Os quatro módulos comuns também ainda usam 0.6. Personagens: 24 fichas existentes, 18 retratos atualizados no lote 03. Existem 198 tokens no catálogo; a matriz exige revisão visual global deles, não os declara ausentes.

**Dependência de fabricação:** as 114 cartas não são todo o kit. A seleção omite intencionalmente REC e PRO: a edição Comece Aqui representa recursos por saldos numerados nos registros, e os projetos pela campanha/manual/painel. Os PDFs de `ABRIGO_MORADORES_ESTOQUE`, `REGISTRO_ADICIONAL`, `MORADORES_ADICIONAL`, guia, manual e campanha precisam entrar no pacote consolidado. Equipamentos iniciais embutidos nas fichas também não são cartas duplicadas. Esses componentes existem na edição 0.6, mas o pacote pós-apocalíptico ainda não está consolidado.

Gates abertos: condomínio, módulos comuns, 39 IDs de arte, QA visual global, conferência de PDF/contagem do pacote consolidado, auditoria lógica profunda e simulação reprodutível. Nenhuma nota 10/10 é justificada agora. A edição 0.6 e provas anteriores permanecem como fontes, sem alteração de regras ou equilíbrio nesta auditoria. Impressão física e playtest humano pendentes.
