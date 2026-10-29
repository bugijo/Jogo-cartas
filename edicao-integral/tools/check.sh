#!/usr/bin/env bash
# Verificação compacta: uma linha por etapa; detalhes só em falha.
#   tools/check.sh quick tests.test_x [tests.test_y ...]   # testes direcionados
#   tools/check.sh full                                     # antes de commit/push
# Variável CHECK_TAIL (padrão 60) limita as linhas mostradas em falha.
set -u
cd "$(dirname "$0")/.." || exit 2
TAIL=${CHECK_TAIL:-60}
LOG=$(mktemp)
trap 'rm -f "$LOG"' EXIT
status=0

step() {  # step <rótulo> <comando...>
  local label=$1; shift
  local start=$SECONDS
  if "$@" >"$LOG" 2>&1; then
    printf 'ok   %-34s %3ss  %s\n' "$label" $((SECONDS-start)) \
      "$(grep -E '^(Ran|OK|FAILED)' "$LOG" | tr '\n' ' ' | cut -c1-60)"
  else
    printf 'FAIL %-34s %3ss\n' "$label" $((SECONDS-start))
    tail -n "$TAIL" "$LOG"
    status=1
  fi
}

case ${1:-} in
  quick)
    shift
    [ $# -gt 0 ] || { echo "uso: $0 quick tests.test_modulo ..."; exit 2; }
    step "unittest $*" python3 -m unittest -q "$@"
    ;;
  full)
    step "suite completa" python3 -m unittest discover -s tests -q
    for script in verify_campaign_player02.py verify_continuous_campaign.py \
                  verify_regional_player.py verify_regional_travel.py verify_regional_campaign.py \
                  verify_pre_radio_celia_route.py \
                  validate_data.py simulate_cistern_sweep.py simulate_regional_campaign.py; do
      step "$script" python3 "$script"
    done
    step "compileall" python3 -m compileall -q .
    step "git diff --check" git -C .. diff --check
    ;;
  *)
    echo "uso: $0 quick <módulos> | full"; exit 2
    ;;
esac
exit $status
