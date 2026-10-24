# Retomada

Estado conhecido: branch `evolucao/zona-zero-sistema-v1`, HEAD remoto observado
`9773da5` antes do trabalho desta sessão. Esse commit reverteu explicitamente
alterações posteriores ao checkpoint `690a597`; o histórico anterior foi
preservado e a unidade de baralho de Hordas abaixo foi implementada sobre a
base remota atual. Nunca reaplicar automaticamente arquivos removidos por essa
reversão.

Unidade desta sessão: sapato de Hordas único por campanha, com seed, snapshot,
validação e migração determinística de saves sem esse campo. Expedições táticas
consomem o baralho compartilhado, salvo quando um teste injeta explicitamente
uma ordem fixa. Isso não completa viagens, cercos ou a campanha.

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

Próximo passo concreto: integrar viagens de ida/volta e recibos de expedição
com transições legais de segmentos e cobranças canônicas; manter o certificado
de vitória fechado até provar o ciclo completo.
