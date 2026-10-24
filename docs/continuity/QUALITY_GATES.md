# Quality gates

| Gate | Aprovação objetiva |
|---|---|
| Git | branch correta, working tree limpo, push fast-forward |
| Motor | suíte experimental sem falhas, compileall e diff check |
| Campanha | todas as peças por ações/retorno legais, sem flags sintéticas |
| Estado | save/load durante abrigo, expedição e transição; recompensas idempotentes |
| Economia | nenhum combustível, carta, equipamento ou pista criado fora de regra |
| Integração | certificado `verified_victory` derivado do estado canônico completo |
| Simulação | oito políticas, H2–H6, sementes e decisões registradas |
| Física | PDFs gerados e inspecionados; dimensões, cortes e frente/verso verificados |
| Humano | playtest registrado antes de declarar equilíbrio ou prontidão física |

Um gate falho mantém a campanha bloqueada e gera uma tarefa reproduzível em
`TASK_QUEUE.json`.
