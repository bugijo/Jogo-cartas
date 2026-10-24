# Retomada do desenvolvimento experimental

## Base e estado

- Branch: `evolucao/zona-zero-sistema-v1`.
- Base reconciliada em `e6af1f730289c80ae60f45535b9dd0be4ec3c68c`, com
  commits de Viagem (`ad297a9`) e integração de resgates (`afdc82c`). O commit
  `052ada0` de observações sem informação oculta também está na história.
- O kit físico 0.2 e seus PDFs não foram alterados.
- Trabalho local: recuperar peças únicas caídas após emergência, aplicar os
  recibos no integrador e cobrir save/load/duplicação. Documentos locais
  aguardam commit/push após completar a reconciliação.

## Evidência atual

- `python -m unittest discover -s edicao-integral/tests -q`: 135 testes passaram
  após integrar `afdc82c`.
- `python -m compileall -q edicao-integral src`, `git diff --check` e
  `python edicao-integral/validate_data.py` passaram.
- `python -m unittest discover -s tests -q`: 51 testes passaram nesta base;
  houve um `ResourceWarning` em `tests/test_boards06.py:64`.
- Falha corrigida localmente: uma peça única carregada numa retirada de
  emergência fica no objetivo canônico, bloqueia a cópia original, é recuperada
  por 1 PA e só chega ao abrigo com retorno legal; o teste faz save/load entre
  as visitas e verifica entrega única.
- `Travel02` e os recibos de resgate estão publicados, mas não completam ainda
  o fluxo da expedição.

## Bloqueios ativos

- `Travel02` não está integrado ao relógio/fluxo tático, não aplica efeitos ao
  abrigo, e M1 ainda não é uma emboscada jogável ligada ao trecho pago.
- Promessas, sequência completa dos cinco dias, rotina de cercos e certificação
  legal da vitória da Cisterna continuam incompletos.
- Migração para Última Transmissão e campanhas completas H2–H6 estão bloqueadas.
- PDFs novos, impressão física e playtest humano não ocorreram.

## Próxima retomada

1. Obter revisão independente final da recuperação de peças únicas; corrigir se
   houver reproducer.
2. Commit/push do lote de emergência e atualizações do escritório.
3. Integrar `Travel02` à expedição: um segmento e uma ocorrência por vez,
   efeitos canônicos aplicados e estado pendente persistente.
4. Integrar M1 ao trecho já pago com uma rodada obrigatória e salvar/restaurar
   durante a emboscada.

Comandos de retomada:

```bash
git fetch origin evolucao/zona-zero-sistema-v1
git merge --ff-only origin/evolucao/zona-zero-sistema-v1
python -m unittest discover -s edicao-integral/tests -q
python -m unittest discover -s tests -q
python -m compileall -q edicao-integral src
git diff --check
```
