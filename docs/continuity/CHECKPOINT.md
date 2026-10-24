# Retomada

Estado conhecido: branch `evolucao/zona-zero-sistema-v1`, HEAD remoto observado
`c4c1911` antes desta unidade. Esse commit reverteu explicitamente
alterações posteriores ao checkpoint `690a597`; o histórico anterior foi
preservado e a unidade de baralho de Hordas abaixo foi implementada sobre a
base remota atual. Nunca reaplicar automaticamente arquivos removidos por essa
reversão.

Unidade desta sessão: sapato de Hordas único por campanha, com seed, snapshot,
validação e migração determinística de saves sem esse campo. Expedições táticas
consomem o baralho compartilhado, salvo quando um teste injeta explicitamente
uma ordem fixa. Isso não completa viagens, cercos ou a campanha.

Também foi persistido o sapato canônico de Viagem a partir dos IDs `VIA` do
catálogo (12 cartas na versão atual), com descarte, reembaralhamento, migração
de saves antigos e round-trip no save integrado. O código ainda não revela uma
carta por trecho nem aplica efeitos de rota; não confundir persistência do
baralho com sistema de viagem executável.

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

Próximo passo concreto: implementar o estado de trecho ida/volta que consome
cartas do sapato persistente, cobra o segmento canônico e encaminha escolhas,
ocorrências noturnas e emboscadas ao relógio compartilhado; manter o certificado
de vitória fechado até provar o ciclo completo.
