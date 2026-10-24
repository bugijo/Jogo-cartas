# Retomada

Estado inicial da unidade: branch `evolucao/zona-zero-sistema-v1`, HEAD local e
remoto `94b6e7c7a397fb009d733d95af825c53a5728cee`. Veja os commits desta
recuperação abaixo e `RECOVERY_AUDIT.md`; as implementações foram integradas
seletivamente, não por cherry-pick cego.

O trabalho anterior de baralhos persistentes de Hordas e Viagem foi preservado.
Os novos módulos recuperados usam esses baralhos como fonte única; saves sem
cursores introduzidos depois são migrados de forma explícita e conservadora.

O estado recuperado agora inclui Viagem por trecho e Emboscada M1, tática de
expedição, liquidação do retorno, eventos diários, cercos e recibos da Cisterna.
Os baralhos recentes de Horda e Viagem permanecem a única fonte persistente.
Saves pré-eventos preservam recursos e estado, registram eventos passados como
lacuna não auditável, aplicam só o evento atual e ficam inelegíveis para
certificação canônica.

Comando idempotente:

```bash
git fetch origin evolucao/zona-zero-sistema-v1
git merge --ff-only origin/evolucao/zona-zero-sistema-v1
git status --short
python3 -m unittest discover -s edicao-integral/tests -q
python3 -m compileall -q edicao-integral src
git diff --check
```

Validação desta unidade: 220 testes experimentais passaram, junto com
`validate_data.py`, `compileall` e `git diff --check`. O replay roteirizado
H2–H6 cobre cinco dias, mas não usa apenas ações legais e não demonstra
`verified_victory`.

Próximo passo: criar um executor de campanha que use exclusivamente a API
pública Viagem → escolha/Emboscada → mapa → recibos táticos → retorno. Hoje
`collect_part()` continua bloqueado e o caminho completo não comprova a coleta
e entrega das três peças sem fixture. Manter `verified_victory` fechado até
esse replay passar desde preparação legítima.

Commits desta recuperação:

- `6f48cf7` — módulos de Viagem e Emboscada M1, com testes.
- `8318291` — eventos canônicos, cercos, tática e recibos da Cisterna.
- `37ff095` — integração da ida/volta, decks únicos e replay H2–H6 corrigido.
- `494d758` — expedição de oficina legal com ordem natural de Viagem seed 22.
- `8bae492` — relatório de recuperação e checkpoints atualizados.
- `1627890` — checkpoint atualizado após documentação.

Publicar somente por fast-forward em `origin/evolucao/zona-zero-sistema-v1`,
sem merge ou force.
