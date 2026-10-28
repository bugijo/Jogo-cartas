#!/usr/bin/env bash
# Inicia o Claude Code CLI apontado ao OmniRoute local, só neste processo.
#
# Não altera ~/.claude, o OAuth, o ANTHROPIC_BASE_URL global nem o Claude
# Desktop: o processo recebe um ambiente mínimo (env -i) e um diretório de
# configuração próprio.
#
#   tools/claude-omniroute.sh --check      # verifica sem chamar modelo
#   tools/claude-omniroute.sh --dry-run    # mostra ambiente (chave mascarada)
#   tools/claude-omniroute.sh [args...]    # inicia o CLI
#
# Chave do OmniRoute: OMNIROUTE_API_KEY no ambiente ou arquivo
# ${OMNIROUTE_KEY_FILE:-~/.config/claude-omniroute/omniroute.key} com modo 600.
# Remover: apague este arquivo e ~/.config/claude-omniroute/.
set -euo pipefail

BASE_URL=${OMNIROUTE_BASE_URL:-http://127.0.0.1:20128/api}
KEY_FILE=${OMNIROUTE_KEY_FILE:-$HOME/.config/claude-omniroute/omniroute.key}
CONFIG_DIR=${CLAUDE_OMNI_CONFIG_DIR:-$HOME/.config/claude-omniroute/claude}
MODEL=${CLAUDE_OMNI_MODEL:-auto}

find_bin() {
  if [ -n "${CLAUDE_BIN:-}" ]; then echo "$CLAUDE_BIN"; return; fi
  if command -v claude >/dev/null 2>&1; then command -v claude; return; fi
  # Binário oficial embutido no Claude Desktop (somente leitura; versão mais nova).
  ls -d "$HOME"/.config/Claude/claude-code/*/*/claude 2>/dev/null | sort -V | tail -1
}

read_key() {
  if [ -n "${OMNIROUTE_API_KEY:-}" ]; then printf '%s' "$OMNIROUTE_API_KEY"; return; fi
  [ -f "$KEY_FILE" ] || { echo "Chave ausente: defina OMNIROUTE_API_KEY ou crie $KEY_FILE (modo 600)" >&2; return 1; }
  local mode; mode=$(stat -c %a "$KEY_FILE")
  [ "$mode" = 600 ] || [ "$mode" = 400 ] || { echo "Permissão insegura em $KEY_FILE ($mode); use chmod 600" >&2; return 1; }
  head -n1 "$KEY_FILE" | tr -d '[:space:]'
}

BIN=$(find_bin)
[ -n "$BIN" ] && [ -x "$BIN" ] || { echo "Claude Code CLI não encontrado (defina CLAUDE_BIN)" >&2; exit 2; }

case "${1:-}" in
  --check)
    echo "binário:  $("$BIN" --version 2>/dev/null) ($BIN)"
    code=$(curl -s -m 5 -o /dev/null -w '%{http_code}' -X POST "$BASE_URL/v1/messages" \
           -H 'content-type: application/json' -d '{}' || true)
    if [ "$code" = 401 ]; then echo "endpoint: $BASE_URL/v1/messages responde e exige chave (401)"
    else echo "endpoint: resposta inesperada ($code) em $BASE_URL/v1/messages" >&2; exit 1; fi
    if read_key >/dev/null; then echo "chave:    encontrada (não exibida)"
    else echo "chave:    ausente — o CLI não iniciará até ser configurada"; fi
    echo "config:   $CONFIG_DIR (isolado de ~/.claude)"
    exit 0 ;;
esac

KEY=$(read_key)
ENVIRONMENT=(
  HOME="$HOME" USER="${USER:-}" PATH="$PATH" SHELL="${SHELL:-/bin/bash}"
  TERM="${TERM:-xterm-256color}" LANG="${LANG:-C.UTF-8}" COLORTERM="${COLORTERM:-}"
  CLAUDE_CONFIG_DIR="$CONFIG_DIR"
  ANTHROPIC_BASE_URL="$BASE_URL"
  ANTHROPIC_AUTH_TOKEN="$KEY"
  ANTHROPIC_MODEL="$MODEL"
  ANTHROPIC_DEFAULT_OPUS_MODEL="$MODEL"
  ANTHROPIC_DEFAULT_SONNET_MODEL="$MODEL"
  ANTHROPIC_DEFAULT_HAIKU_MODEL="$MODEL"
  CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
  DISABLE_AUTOUPDATER=1
)
if [ "${1:-}" = --dry-run ]; then
  printf '%s\n' "${ENVIRONMENT[@]}" | sed -E 's/^(ANTHROPIC_AUTH_TOKEN=).*/\1<mascarada>/'
  echo "exec $BIN ${*:2}"
  exit 0
fi
mkdir -p "$CONFIG_DIR"
chmod 700 "$(dirname "$CONFIG_DIR")" "$CONFIG_DIR"
exec env -i "${ENVIRONMENT[@]}" "$BIN" "$@"
