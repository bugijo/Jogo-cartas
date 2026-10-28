# Claude Code CLI via OmniRoute (launcher isolado)

`tools/claude-omniroute.sh` inicia o Claude Code CLI apontado ao OmniRoute local
**só no processo iniciado**. Não altera `~/.claude`, o OAuth, o
`ANTHROPIC_BASE_URL` global nem o Claude Desktop.

## Verificado em 2026-10-28 (sem chamada a modelo)
- Endpoint compatível com a API de Mensagens da Anthropic, pela spec do próprio
  OmniRoute: `POST http://127.0.0.1:20128/api/v1/messages` (e
  `/api/v1/messages/count_tokens`). O CLI acrescenta `/v1/messages` à base, por
  isso `ANTHROPIC_BASE_URL=http://127.0.0.1:20128/api`.
- Autenticação: `Authorization: Bearer` e `x-api-key` são reconhecidos (chave
  falsa → 401 `Invalid API key`). O launcher usa `ANTHROPIC_AUTH_TOKEN` (Bearer).
- Portas 20131/20132 não servem essa API.
- Não usar `omniroute config set claude`: ele escreve em `~/.claude/settings.json`,
  que o Desktop também usa.

## Binário
O launcher usa, nesta ordem: `CLAUDE_BIN`, `claude` no PATH, ou o binário
oficial embutido no Desktop (`~/.config/Claude/claude-code/<versão>/…/claude`),
apenas para leitura e sem autoatualização. Instalação oficial independente
(exige aprovação, é global): instalador nativo `curl -fsSL https://claude.ai/install.sh | bash`
ou `npm install -g @anthropic-ai/claude-code`.

## Uso
```bash
mkdir -p ~/.config/claude-omniroute && chmod 700 ~/.config/claude-omniroute
# grave a chave do OmniRoute você mesmo (não vai para o git nem para logs):
install -m 600 /dev/null ~/.config/claude-omniroute/omniroute.key && nano ~/.config/claude-omniroute/omniroute.key
tools/claude-omniroute.sh --check     # sem chamar modelo
tools/claude-omniroute.sh --dry-run   # ambiente com chave mascarada
tools/claude-omniroute.sh             # abre o CLI
```
Variáveis opcionais: `OMNIROUTE_API_KEY`, `OMNIROUTE_KEY_FILE`,
`OMNIROUTE_BASE_URL`, `CLAUDE_OMNI_MODEL` (padrão `auto`),
`CLAUDE_OMNI_CONFIG_DIR` (padrão `~/.config/claude-omniroute/claude`).

## Reverter
```bash
rm -rf ~/.config/claude-omniroute
git rm tools/claude-omniroute.sh tools/CLAUDE_OMNIROUTE.md
```

## Fallback do OmniRoute (diagnóstico, não alterado)
`omniroute simulate --explain "ping"` (dry-run) mostra o pool automático:
groq `gpt-oss-120b` → uncloseai `Qwen3.8-27B` → veoaifree-web `seedance`.
`seedance` é modelo de **geração de vídeo** (ByteDance, servido pelo Veo AI
Free) e não serve para programação. Proposta, a aprovar: desativar/rebaixar a
conexão `veoaifree-web` para que a conexão já validada `Gemini-Free` (modelos
de texto, p.ex. `gemini-2.5-flash`) cubra o terceiro elo. Disponibilidade real
do Gemini-Free não foi testada para não gerar chamada.
