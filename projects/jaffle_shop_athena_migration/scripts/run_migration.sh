#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ROOT="$(cd "$PROJECT_DIR/../.." && pwd)"
VENV="${DLC_VENV:-$ROOT/.venv}"
ENV_FILE="${DLC_ENV_FILE:-$ROOT/.env}"
RESULTS_DIR="$PROJECT_DIR/results"
DBT="$VENV/bin/dbt"

set -a
# shellcheck disable=SC1090
[ -f "$ENV_FILE" ] && . "$ENV_FILE"
set +a

export DBT_PROFILES_DIR="$PROJECT_DIR"
mkdir -p "$RESULTS_DIR"

need_dbt() {
  if [ ! -x "$DBT" ]; then
    echo "dbt not found at $DBT" >&2
    echo "Install requirements.txt or set DLC_VENV." >&2
    exit 2
  fi
}

need_live_config() {
  local missing=()
  for name in DLC_HOST DLC_ENGINE_NAME DLC_RESOURCE_GROUP \
    TENCENTCLOUD_SECRET_ID TENCENTCLOUD_SECRET_KEY; do
    [ -n "${!name:-}" ] || missing+=("$name")
  done
  if [ ${#missing[@]} -gt 0 ]; then
    echo "missing live configuration: ${missing[*]}" >&2
    exit 2
  fi
}

run_case() {
  local case_name="$1"
  local expectation="$2"
  shift 2
  local log="$RESULTS_DIR/${case_name}.log"
  local status outcome

  set +e
  "$@" >"$log" 2>&1
  status=$?
  set -e

  if [ "$status" -eq 0 ]; then outcome=pass; else outcome=fail; fi
  printf '%s,%s,%s,%s,%s\n' \
    "$case_name" "$expectation" "$status" "$outcome" "$log" >>"$REPORT"

  if [ "$expectation" = pass ] && [ "$status" -ne 0 ]; then
    REQUIRED_FAILURES=$((REQUIRED_FAILURES + 1))
  fi
}

cmd_lint() {
  need_dbt
  cd "$PROJECT_DIR"
  "$DBT" parse --target parse --no-partial-parse
  "$DBT" compile --target parse --no-partial-parse --no-introspect --no-populate-cache
  "$VENV/bin/python" scripts/inspect_manifest.py target/manifest.json \
    >"$RESULTS_DIR/namespace_compile.csv"
  echo "namespace report: $RESULTS_DIR/namespace_compile.csv"
}

cmd_full() {
  need_dbt
  need_live_config
  cd "$PROJECT_DIR"

  REPORT="$RESULTS_DIR/runtime_results.csv"
  REQUIRED_FAILURES=0
  printf 'case,expectation,exit_code,outcome,log\n' >"$REPORT"

  run_case seed pass "$DBT" seed --target dev --full-refresh
  run_case jaffle_baseline pass "$DBT" build --target dev --select tag:jaffle_baseline
  run_case namespace_probe pass "$DBT" run --target dev --select tag:namespace_probe

  run_case athena_from_iso8601 observe "$DBT" run --target dev --select athena_from_iso8601
  run_case athena_date_parse observe "$DBT" run --target dev --select athena_date_parse
  run_case athena_date_parse_only observe "$DBT" run --target dev --select athena_date_parse_only
  run_case athena_json_extract observe "$DBT" run --target dev --select athena_json_extract

  run_case dlc_converted pass "$DBT" build --target dev --select tag:dlc_converted
  run_case dlc_pattern_values pass "$DBT" test --target dev --select assert_dlc_pattern_values

  run_case iceberg_batch_1 pass "$DBT" run --target dev --select iceberg_order_upserts \
    --full-refresh --vars '{load_batch: 1}'
  run_case iceberg_batch_2 pass "$DBT" run --target dev --select iceberg_order_upserts \
    --vars '{load_batch: 2}'
  run_case iceberg_merge_result pass "$DBT" test --target dev \
    --select iceberg_order_upserts assert_iceberg_upsert_matches_expected

  echo "runtime report: $REPORT"
  if [ "$REQUIRED_FAILURES" -ne 0 ]; then
    echo "$REQUIRED_FAILURES required case(s) failed" >&2
    exit 1
  fi
}

case "${1:-}" in
  lint) cmd_lint ;;
  full) cmd_full ;;
  *) echo "usage: $0 {lint|full}" >&2; exit 2 ;;
esac
