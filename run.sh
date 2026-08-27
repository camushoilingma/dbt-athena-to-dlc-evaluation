#!/usr/bin/env bash
# Run the two numbered dbt-athena to dbt-dlc test suites.
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SUITE_1="$ROOT/tests/suite_01_end_to_end_conversion"
SUITE_2="$ROOT/tests/suite_02_adapter_tests"
VENV="${DLC_VENV:-${VENV:-$ROOT/.venv}}"
ENV_FILE="${DLC_ENV_FILE:-$ROOT/.env}"
PYTHON="$VENV/bin/python"
DBT="$VENV/bin/dbt"

set -a
# shellcheck disable=SC1090
[ -f "$ENV_FILE" ] && . "$ENV_FILE"
set +a

need_tools() {
  if [ ! -x "$PYTHON" ] || [ ! -x "$DBT" ]; then
    echo "dbt environment not found at $VENV" >&2
    echo "Create .venv from requirements.txt or set DLC_VENV." >&2
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
  local log="$SUITE_1/results/${case_name}.log"
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

run_suite_1_lint() {
  need_tools
  mkdir -p "$SUITE_1/results"
  export DBT_PROFILES_DIR="$SUITE_1"
  cd "$SUITE_1" || exit 2
  "$DBT" parse --target parse --no-partial-parse || exit $?
  "$DBT" compile --target parse --no-partial-parse \
    --no-introspect --no-populate-cache || exit $?
  "$PYTHON" scripts/inspect_manifest.py target/manifest.json \
    >results/namespace_compile.csv || exit $?
  echo "suite=1 namespace_report=$SUITE_1/results/namespace_compile.csv"
}

run_suite_1() {
  need_tools
  need_live_config
  mkdir -p "$SUITE_1/results"
  export DBT_PROFILES_DIR="$SUITE_1"
  cd "$SUITE_1" || exit 2

  REPORT="$SUITE_1/results/runtime_results.csv"
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

  echo "suite=1 runtime_report=$REPORT"
  if [ "$REQUIRED_FAILURES" -ne 0 ]; then
    echo "$REQUIRED_FAILURES required case(s) failed" >&2
    exit 1
  fi
}

run_suite_2() {
  local mode="${1:-run}"
  local stamp out_dir log xml status
  local extra=()

  need_tools
  case "$mode" in
    run) need_live_config ;;
    collect) extra=(--collect-only) ;;
    *) echo "usage: $0 2 [collect]" >&2; exit 2 ;;
  esac

  stamp="$(date -u +%Y%m%dT%H%M%SZ)"
  out_dir="$SUITE_2/results"
  log="$out_dir/${mode}-${stamp}.log"
  xml="$out_dir/${mode}-${stamp}.xml"
  mkdir -p "$out_dir"
  cd "$ROOT" || exit 2

  echo "suite=2 mode=$mode log=$log"
  set +e
  "$PYTHON" -m pytest "$SUITE_2" "${extra[@]}" \
    --junitxml="$xml" -p no:cacheprovider 2>&1 | tee "$log"
  status="${PIPESTATUS[0]}"
  set -e
  echo "exit=$status log=$log junit=$xml"
  exit "$status"
}

case "${1:-}" in
  1)
    case "${2:-run}" in
      run) run_suite_1 ;;
      lint) run_suite_1_lint ;;
      *) echo "usage: $0 1 [lint]" >&2; exit 2 ;;
    esac
    ;;
  2) run_suite_2 "${2:-run}" ;;
  all)
    run_suite_1
    run_suite_2 run
    ;;
  *)
    echo "usage: $0 {1|2|all} [lint|collect]" >&2
    exit 2
    ;;
esac
