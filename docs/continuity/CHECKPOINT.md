# Retomada

Estado conhecido: branch `evolucao/zona-zero-sistema-v1`, HEAD esperado
`41ee603` ou descendente fast-forward.

Comando idempotente:

```bash
git fetch origin evolucao/zona-zero-sistema-v1
git merge --ff-only origin/evolucao/zona-zero-sistema-v1
git status --short
python3 -m unittest discover -s edicao-integral/tests -q
python3 -m compileall -q edicao-integral src
git diff --check
```

Próxima tarefa desbloqueável: `P0-EXPEDITION-COMPLETE`, mas somente nas áreas
que não dependem de decisão sobre a migração de personagens. Não executar Meta,
publicação, impressão final ou emitir `verified_victory` enquanto a fila marca
P0/P1 como bloqueada.
