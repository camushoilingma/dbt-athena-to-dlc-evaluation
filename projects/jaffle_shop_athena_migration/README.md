# Jaffle Shop Athena-to-DLC migration baseline

This local-only project measures the refactoring required to move a small
e-commerce dbt project from Athena/Presto SQL to dbt-dlc 1.1.1. It does not run
Athena. Instead, it executes the original syntax and converted syntax separately
against DLC and records both outcomes.

## Source provenance

- Jaffle Shop Classic at commit `fd7bfacae4f497ff044a6a0275268676bf1b64c3`:
  <https://github.com/dbt-labs/jaffle-shop-classic>
- dbt-athena at commit `802d40f0f0eb663c17e5be08d1e3fb2e55b9ee34`:
  `from_iso8601_timestamp` comes from `test_incremental_microbatch.py`; the
  `try(date_parse(...))` form comes from the adapter seed helper.
- `json_extract_scalar` comes from the official AWS Athena JSON documentation.
  The current dbt-athena functional suite has no JSON extraction fixture:
  <https://docs.aws.amazon.com/athena/latest/ug/extracting-data-from-JSON.html>

The copied Jaffle Shop files remain under their upstream Apache 2.0 license in
`UPSTREAM_LICENSE`.

## Test phases

1. Build unchanged Jaffle Shop seeds and models.
2. Execute each Athena expression independently to observe native compatibility.
3. Build the mechanically converted DLC/Spark equivalents and validate values.
4. Build an Iceberg incremental model with batch 1, merge batch 2, then reconcile
   the complete table to an expected seed.
5. Inspect `manifest.json` to prove dbt resolves relations as
   `catalog.database.table`.

## Run

Python 3.10 or newer and `dbt-dlc==1.1.1` are required.

```bash
./scripts/run_migration.sh lint
./scripts/run_migration.sh full
```

`lint` is offline. `full` must run on the in-VPC CVM holding the route to the DLC
private endpoint. Set `DLC_ENV_FILE` to the merged configuration/credential file
and `DLC_VENV` to the venv when they differ from the repo defaults.

Results are written as CSV plus per-case logs under `results/`.
