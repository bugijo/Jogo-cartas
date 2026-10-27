# Zona Zero — instruções para o Claude Code

Regras permanentes: `docs/continuity/AGENTS.md` (ler uma vez por sessão).

## Antes de trabalhar
- Ler só o bloco "Estado ativo" do topo de `docs/continuity/CHECKPOINT.md` e a
  tarefa em `docs/continuity/TASK_QUEUE.json`. Os blocos antigos são histórico:
  consultar apenas quando o estado ativo apontar para eles.
- Não refazer auditorias já registradas; confiar nos números do checkpoint e
  re-medir só o que a tarefa atual muda.
- Confirmar `git rev-parse HEAD` igual ao remoto da branch.

## Escopo e leitura
- Branch: `evolucao/zona-zero-sistema-v1`. Nunca alterar `main`, o kit físico
  0.2, `RULES.md`, `CAMPAIGN.md` nem `content/`. Sem force push.
- Código do motor e testes: `edicao-integral/` (`*.py`, `tests/`).
- `samples/`, `output/`, `dist/`, `assets/` e `kit-final-prova/` são artefatos
  grandes (GB) e ficam fora das buscas (`.ignore`). Para trabalho físico, passe
  o caminho explicitamente.
- Buscar símbolo (`grep -n "def nome"`) e ler só o trecho necessário; não ler
  arquivos inteiros grandes. `edicao-integral/replays/*.json` são grandes:
  consultar com Python (`json.load` + campos), nunca ler inteiros.

## Testes
- Durante o desenvolvimento: `edicao-integral/tools/check.sh quick tests.test_x`.
- Antes de commit/push: `edicao-integral/tools/check.sh full` (suíte completa,
  verificadores, compileall, diff check). Saída é uma linha por etapa; detalhes
  só em falha. Não trocar a verificação completa por uma parcial.
- A seed 22 da Cisterna deve continuar `verified_victory` com 98 decisões.
- Sementes do controlador: ajuste em 1–30; 31–60 e 61–90 já foram vistas;
  próxima validação cega em 91–120 (medir uma vez antes de ajustar).

## Registro
- Decisões de regra aprovadas: `edicao-integral/MANUAL_EXPERIMENTAL.md`.
  Regra ambígua: registrar e pedir aprovação, não decidir em silêncio.
- Progresso: bloco novo no topo de `CHECKPOINT.md` (curto), `TASK_QUEUE.json`,
  `PROGRESS.md`, `PLAYTEST_REPORT.md` quando houver medição.
- Commits pequenos: código e documentação separados; push por fast-forward.

## Estilo
- Respostas em pt-BR, objetivas; resultados em tabelas curtas.
- Não inventar vitórias, recursos ou porcentagens de economia.
- Tarefas independentes: concluir, registrar no checkpoint e só então seguir.
