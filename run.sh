#!/usr/bin/env bash
# Run dbt Labs' adapter conformance suite against a live DLC engine.
#
# Must run from a host inside the VPC that holds the DLC private link, because
# dbt-dlc speaks HiveServer2 Thrift to an internal address.
#
#   ./run.sh core        # the baseline every adapter is expected to pass
#   ./run.sh extended    # capability suites beyond the baseline
#   ./run.sh athena      # converted dbt-athena Iceberg fixtures
#   ./run.sh all
#
# Reads connection settings from the repo-root .env (never committed).
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TIER="${1:-core}"
VENV="${VENV:-$HOME/venv}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUT_DIR="$HERE/results"
mkdir -p "$OUT_DIR"

case "$TIER" in
  core)     SELECT=(-m core) ;;
  extended) SELECT=(-m extended) ;;
  athena)   SELECT=(-m athena_conversion) ;;
  all)      SELECT=() ;;
  *) echo "usage: $0 {core|extended|athena|all} [extra pytest args]" >&2; exit 2 ;;
esac
shift || true
cd "$HERE"

LOG="$OUT_DIR/${TIER}-${STAMP}.log"
XML="$OUT_DIR/${TIER}-${STAMP}.xml"

echo "tier=$TIER  log=$LOG"
"$VENV/bin/python" -m pytest "${SELECT[@]}" \
  --junitxml="$XML" \
  -p no:cacheprovider \
  "$@" 2>&1 | tee "$LOG"

# pytest's exit code, not tee's
STATUS="${PIPESTATUS[0]}"
echo
echo "exit=$STATUS  log=$LOG  junit=$XML"
exit "$STATUS"
