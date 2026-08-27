# dbt-athena to dbt-dlc evaluation

Standalone test repository for estimating the work required to convert an
Iceberg-oriented `dbt-athena` project to `dbt-dlc==1.1.1`.

Athena is not provisioned or executed. Original Athena/Presto expressions are
run directly on DLC to identify syntax that needs conversion; their DLC/Spark
equivalents are then built and validated on the same input rows.

## Contents

- `projects/jaffle_shop_athena_migration/`: the customer-focused experiment.
- `tests/test_athena_to_dlc.py`: dbt Labs adapter fixtures converted to DLC.
- `athena_to_dlc_matrix.csv`: source configuration to DLC mapping.
- [`test_run_2026-08-26.md`](test_run_2026-08-26.md): exact inputs, commands,
  outputs, and assertions from the completed live run.
- `tests/test_*.py`: optional broader dbt adapter conformance coverage.

The Jaffle Shop fixture is based on dbt Labs' `jaffle-shop-classic` at commit
`fd7bfacae4f497ff044a6a0275268676bf1b64c3`. Athena patterns are attributed in
the fixture README and migration matrix.

## Environment

Python 3.10 or newer is required. Create `.env` from `.env.example`; credentials
must remain local.

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

Live execution must run from a host with network access to the DLC private
endpoint.

## Customer migration experiment

```bash
cd projects/jaffle_shop_athena_migration
./scripts/run_migration.sh lint
./scripts/run_migration.sh full
```

`lint` parses and compiles without a database connection. `full` loads the six
CSV seeds, builds the unchanged Jaffle baseline, observes the original Athena
expressions, validates converted date/JSON models, and executes a two-batch
Iceberg MERGE with exact result reconciliation.

This runner executes one checked-in dbt project with fixed CSV inputs and a
fixed command order. It is the runner used for the dated evidence in
[`test_run_2026-08-26.md`](test_run_2026-08-26.md).

## Adapter fixture suite

```bash
./run.sh athena
```

The Python files under `tests/` are pytest test definitions, not command-line
scripts. They subclass fixtures from `dbt-tests-adapter`; pytest creates a
temporary dbt project and schema for each test class. Root `run.sh` selects the
`athena_conversion` marker and invokes them through:

```text
./run.sh athena
  -> python -m pytest -m athena_conversion
  -> tests/test_athena_to_dlc.py
```

The Athena conversion tier contains 23 collected tests for materializations,
append/merge, unique keys, predicates, excluded columns, schema evolution,
snapshots, seeds, and catalog generation. This broader tier has been collected
offline but has not been executed as part of the recorded customer run.

It is deliberately not called by `run_migration.sh full`: that command records
the fixed Jaffle customer experiment, while the Python suite creates many
temporary projects and tests broader adapter behavior. Combining them would
make the dated run claim tests that were never executed live. To execute the
Python tests, run `./run.sh athena` separately from the repository root.

The optional `core`, `extended`, and `all` tiers exercise general adapter
behavior beyond the customer migration scope.

## Generated files

Raw logs, JUnit XML, dbt `target/` directories, `.env`, and virtual environments
are intentionally ignored. They stay on the machine that produced them and are
not suitable for source control.
