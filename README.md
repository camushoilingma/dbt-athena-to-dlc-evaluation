# dbt-athena to dbt-dlc evaluation

This repository estimates the work required to convert an Iceberg-oriented
`dbt-athena` project to `dbt-dlc==1.1.1`. Athena is not provisioned or executed.
Original Athena/Presto expressions are attempted directly on DLC, then their
DLC/Spark equivalents are run against the same CSV inputs.

`README.md` is the repository's only tracked Markdown file. It contains the
test instructions and the evidence from the recorded live run.

## Repository layout

```text
README.md
run.sh
athena_to_dlc_matrix.csv
tests/
  conftest.py
  suite_01_end_to_end_conversion/
  suite_02_adapter_tests/
```

There is one command entry point: [`run.sh`](run.sh).

## Environment

Python 3.10 or newer is required. Create `.env` from `.env.example`; credentials
must remain local. Live runs require network access to the DLC private endpoint.

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## Test Suite 1: End-to-end conversion

Directory: [`tests/suite_01_end_to_end_conversion`](tests/suite_01_end_to_end_conversion)

Suite 1 uses the generic Jaffle Shop project as a baseline and adds focused
Athena-to-DLC conversion cases. Jaffle Shop itself is not Athena-specific.
The suite uses one fixed dbt project with six CSV inputs and tests:

1. unchanged Jaffle Shop seeds and models;
2. three-level `catalog.database.table` resolution;
3. original Athena/Presto date and JSON expressions on DLC;
4. converted DLC/Spark date and JSON expressions;
5. a two-batch Iceberg `MERGE` upsert;
6. exact final-row reconciliation.

Run the offline parse, compile, and namespace inspection:

```bash
./run.sh 1 lint
```

Run the complete live suite:

```bash
./run.sh 1
```

The Suite 1 commands are defined in
[`run.sh:59-107`](run.sh#L59-L107). Each case writes a log and one CSV row through
[`run.sh:38-57`](run.sh#L38-L57).

The exact command used for the 2026-08-26 recorded run, before the repository
was simplified, was:

```bash
cd projects/jaffle_shop_athena_migration
./scripts/run_migration.sh full
```

That historical runner executed the same ordered dbt commands now located at
[`run.sh:83-100`](run.sh#L83-L100). The old nested runner was removed so the
current repository has only one entry point.

### Suite 1 recorded environment

The recorded live execution occurred on 2026-08-26 with:

```text
dbt-core: 1.12.3
dbt-dlc:  1.1.1
catalog:  DataLakeCatalog
schema:   athena_migration
```

The catalog and schema are selected by
[`profiles.yml`](tests/suite_01_end_to_end_conversion/profiles.yml). No Athena
engine and no Kaggle dataset were used.

### Test 1.1: Seed inputs

Runner command: [`run.sh:83`](run.sh#L83)

```bash
dbt seed --target dev --full-refresh
```

| Exact CSV input | Rows | Persistent DLC output |
|---|---:|---|
| [`raw_customers.csv`](tests/suite_01_end_to_end_conversion/seeds/raw_customers.csv) | 100 | table `DataLakeCatalog.athena_migration.raw_customers` |
| [`raw_orders.csv`](tests/suite_01_end_to_end_conversion/seeds/raw_orders.csv) | 99 | table `DataLakeCatalog.athena_migration.raw_orders` |
| [`raw_payments.csv`](tests/suite_01_end_to_end_conversion/seeds/raw_payments.csv) | 113 | table `DataLakeCatalog.athena_migration.raw_payments` |
| [`raw_athena_events.csv`](tests/suite_01_end_to_end_conversion/seeds/raw_athena_events.csv) | 3 | table `DataLakeCatalog.athena_migration.raw_athena_events` |
| [`raw_order_updates.csv`](tests/suite_01_end_to_end_conversion/seeds/raw_order_updates.csv) | 4 | table `DataLakeCatalog.athena_migration.raw_order_updates` |
| [`expected_order_upserts.csv`](tests/suite_01_end_to_end_conversion/seeds/expected_order_upserts.csv) | 3 | table `DataLakeCatalog.athena_migration.expected_order_upserts` |

Recorded result: all six seeds loaded successfully as Iceberg tables.

### Test 1.2: Unchanged Jaffle baseline

Runner command: [`run.sh:84`](run.sh#L84)

```bash
dbt build --target dev --select tag:jaffle_baseline
```

| SQL model | Relation inputs | Persistent DLC output |
|---|---|---|
| [`stg_customers.sql`](tests/suite_01_end_to_end_conversion/models/staging/stg_customers.sql) | `raw_customers` | view `stg_customers` |
| [`stg_orders.sql`](tests/suite_01_end_to_end_conversion/models/staging/stg_orders.sql) | `raw_orders` | view `stg_orders` |
| [`stg_payments.sql`](tests/suite_01_end_to_end_conversion/models/staging/stg_payments.sql) | `raw_payments` | view `stg_payments` |
| [`customers.sql`](tests/suite_01_end_to_end_conversion/models/customers.sql) | `stg_customers`, `stg_orders`, `stg_payments` | table `customers` |
| [`orders.sql`](tests/suite_01_end_to_end_conversion/models/orders.sql) | `stg_orders`, `stg_payments` | table `orders` |

All relations use `DataLakeCatalog.athena_migration`. The generic assertions
are declared in
[`models/schema.yml`](tests/suite_01_end_to_end_conversion/models/schema.yml) and
[`models/staging/schema.yml`](tests/suite_01_end_to_end_conversion/models/staging/schema.yml).
The assertions create no persistent tables or views; they pass when their query
returns zero invalid rows.

Recorded result: three views, two tables, and twenty assertions passed.

### Test 1.3: Three-level namespace

Runner command: [`run.sh:85`](run.sh#L85)

```bash
dbt run --target dev --select tag:namespace_probe
```

Exact SQL: [`namespace_probe.sql`](tests/suite_01_end_to_end_conversion/models/migration/namespace_probe.sql)

```text
input:  table DataLakeCatalog.athena_migration.raw_orders
output: view  DataLakeCatalog.athena_migration.namespace_probe
value:  count(*) as order_count
```

Recorded result: the three-level relation resolved and the view was created.
This case did not separately assert that `order_count` was 99.

The offline command [`./run.sh 1 lint`](run.sh#L59-L70) parses and compiles the
project, then passes `target/manifest.json` to
[`inspect_manifest.py`](tests/suite_01_end_to_end_conversion/scripts/inspect_manifest.py).
It produces `results/namespace_compile.csv` with `unique_id`, `database`,
`schema`, `identifier`, `namespace_levels`, and `relation_name` for all 15
models and 6 seeds.

### Test 1.4: Original Athena expressions

Runner commands: [`run.sh:87-90`](run.sh#L87-L90)

All four models read
`DataLakeCatalog.athena_migration.raw_athena_events` from
[`raw_athena_events.csv`](tests/suite_01_end_to_end_conversion/seeds/raw_athena_events.csv).

| SQL input | Athena expression attempted | Attempted DLC output | Recorded result |
|---|---|---|---|
| [`athena_from_iso8601.sql`](tests/suite_01_end_to_end_conversion/models/migration/athena_source/athena_from_iso8601.sql) | `from_iso8601_timestamp(event_ts_iso)` | view `athena_from_iso8601` | not created; function unresolved |
| [`athena_date_parse.sql`](tests/suite_01_end_to_end_conversion/models/migration/athena_source/athena_date_parse.sql) | `try(date_parse(event_date_text, '%Y-%m-%d'))` | view `athena_date_parse` | not created; `try` unresolved |
| [`athena_date_parse_only.sql`](tests/suite_01_end_to_end_conversion/models/migration/athena_source/athena_date_parse_only.sql) | `date_parse(event_date_text, '%Y-%m-%d')` | view `athena_date_parse_only` | not created; function unresolved |
| [`athena_json_extract.sql`](tests/suite_01_end_to_end_conversion/models/migration/athena_source/athena_json_extract.sql) | `json_extract_scalar(payload, '$.channel')` | view `athena_json_extract` | not created; function unresolved |

These are observation cases. Their exit codes are recorded, but an expected
Athena syntax failure does not fail the complete Suite 1 runner.

### Test 1.5: Converted DLC expressions

Runner commands: [`run.sh:92-93`](run.sh#L92-L93)

```bash
dbt build --target dev --select tag:dlc_converted
dbt test --target dev --select assert_dlc_pattern_values
```

| SQL model | DLC expression | Persistent DLC output |
|---|---|---|
| [`dlc_iso_timestamp.sql`](tests/suite_01_end_to_end_conversion/models/migration/dlc_converted/dlc_iso_timestamp.sql) | `to_timestamp(event_ts_iso)` | view `dlc_iso_timestamp` |
| [`dlc_date_parse.sql`](tests/suite_01_end_to_end_conversion/models/migration/dlc_converted/dlc_date_parse.sql) | `to_date(event_date_text, 'yyyy-MM-dd')` | view `dlc_date_parse` |
| [`dlc_json_extract.sql`](tests/suite_01_end_to_end_conversion/models/migration/dlc_converted/dlc_json_extract.sql) | `get_json_object(payload, '$.channel')` | view `dlc_json_extract` |
| [`dlc_pattern_results.sql`](tests/suite_01_end_to_end_conversion/models/migration/dlc_converted/dlc_pattern_results.sql) | joins the three converted views by `id` | view `dlc_pattern_results` |

The exact value assertion is
[`assert_dlc_pattern_values.sql`](tests/suite_01_end_to_end_conversion/assertions/assert_dlc_pattern_values.sql).
It checks non-null converted timestamps and dates plus channels
`web`, `mobile`, and `store` by ID. It creates no persistent relation.

Recorded result: four views and six assertions passed.

### Test 1.6: Iceberg MERGE batch 1

Runner command: [`run.sh:95-96`](run.sh#L95-L96)

```bash
dbt run --target dev --select iceberg_order_upserts \
  --full-refresh --vars '{load_batch: 1}'
```

Exact rows selected from
[`raw_order_updates.csv`](tests/suite_01_end_to_end_conversion/seeds/raw_order_updates.csv):

```csv
batch_id,order_id,customer_id,order_date,status,amount_cents
1,1,10,2024-01-01,placed,1000
1,2,20,2024-01-02,placed,2000
```

Exact model:
[`iceberg_order_upserts.sql`](tests/suite_01_end_to_end_conversion/models/migration/iceberg_order_upserts.sql)

```text
output: Iceberg incremental table DataLakeCatalog.athena_migration.iceberg_order_upserts
```

Recorded result: the full refresh created the table from batch 1.

### Test 1.7: Iceberg MERGE batch 2

Runner command: [`run.sh:97-98`](run.sh#L97-L98)

```bash
dbt run --target dev --select iceberg_order_upserts \
  --vars '{load_batch: 2}'
```

Exact rows selected from `raw_order_updates.csv`:

```csv
batch_id,order_id,customer_id,order_date,status,amount_cents
2,1,10,2024-01-01,shipped,1200
2,3,30,2024-01-03,placed,3000
```

The model config sets `incremental_strategy='merge'`,
`unique_key='order_id'`, and `partition_by='order_date'`.

```text
output updated in place: Iceberg table DataLakeCatalog.athena_migration.iceberg_order_upserts
```

Recorded result: order 1 was updated and order 3 was inserted.

### Test 1.8: Exact MERGE reconciliation

Runner command: [`run.sh:99-100`](run.sh#L99-L100)

```bash
dbt test --target dev \
  --select iceberg_order_upserts assert_iceberg_upsert_matches_expected
```

```text
actual input:   table DataLakeCatalog.athena_migration.iceberg_order_upserts
expected input: table DataLakeCatalog.athena_migration.expected_order_upserts
output:         no persistent relation; assertion must return zero rows
```

Exact expected input from
[`expected_order_upserts.csv`](tests/suite_01_end_to_end_conversion/seeds/expected_order_upserts.csv):

```csv
order_id,customer_id,order_date,status,amount_cents
1,10,2024-01-01,shipped,1200
2,20,2024-01-02,placed,2000
3,30,2024-01-03,placed,3000
```

[`assert_iceberg_upsert_matches_expected.sql`](tests/suite_01_end_to_end_conversion/assertions/assert_iceberg_upsert_matches_expected.sql)
compares all five columns in both directions with `EXCEPT`.

Recorded result: all five assertions returned zero invalid rows. The final
Iceberg table contained exactly the three expected rows, with no missing or
additional rows.

### Suite 1 warehouse inventory

The completed run created nine tables:

```text
customers
expected_order_upserts
iceberg_order_upserts
orders
raw_athena_events
raw_customers
raw_order_updates
raw_orders
raw_payments
```

It created eight views:

```text
dlc_date_parse
dlc_iso_timestamp
dlc_json_extract
dlc_pattern_results
namespace_probe
stg_customers
stg_orders
stg_payments
```

All are under `DataLakeCatalog.athena_migration`. The four `athena_*` views were
not created because their original expressions failed. The 31 dbt assertions
were queries and did not create persistent warehouse objects.

## Test Suite 2: Adapter tests

Directory: [`tests/suite_02_adapter_tests`](tests/suite_02_adapter_tests)

These Python files subclass fixtures from `dbt-tests-adapter`. Pytest creates a
temporary dbt project and schema for each test class.

```bash
./run.sh 2 collect
./run.sh 2
```

The exact pytest invocation is in [`run.sh:109-136`](run.sh#L109-L136).

| Test group | Exact test file | Coverage |
|---|---|---|
| 2.1 | [`test_athena_to_dlc.py`](tests/suite_02_adapter_tests/test_athena_to_dlc.py) | Athena-oriented Iceberg materializations, append/merge, keys, predicates, schema evolution, snapshots, seeds, and catalog generation |
| 2.2 | [`test_basic.py`](tests/suite_02_adapter_tests/test_basic.py) | base table, view, seed, and snapshot behavior |
| 2.3 | [`test_incremental_strategies.py`](tests/suite_02_adapter_tests/test_incremental_strategies.py) | incremental strategy behavior |
| 2.4 | [`test_metadata_and_docs.py`](tests/suite_02_adapter_tests/test_metadata_and_docs.py) | metadata and catalog generation |
| 2.5 | [`test_utils.py`](tests/suite_02_adapter_tests/test_utils.py) | adapter utility macros |
| 2.6 | [`test_workflow.py`](tests/suite_02_adapter_tests/test_workflow.py) | dbt workflow behavior |

The complete Suite 2 collection contains 128 tests. Its Athena-oriented group
contains 23 tests. They were collected offline but were not executed as part of
the recorded Suite 1 live run.

## Run both suites

```bash
./run.sh all
```

This runs live Suite 1 followed by live Suite 2. Generated logs, CSV reports,
JUnit XML, dbt `target/` directories, `.env`, and virtual environments are
ignored by Git.

## Conversion matrix

[`athena_to_dlc_matrix.csv`](athena_to_dlc_matrix.csv) maps dbt-athena inputs to
their dbt-dlc equivalents and names the Suite 2 test class when one exists.

## Source provenance

- Jaffle Shop Classic commit `fd7bfacae4f497ff044a6a0275268676bf1b64c3`:
  <https://github.com/dbt-labs/jaffle-shop-classic>
- dbt-athena commit `802d40f0f0eb663c17e5be08d1e3fb2e55b9ee34`:
  `from_iso8601_timestamp` is represented in its functional tests and the
  `try(date_parse(...))` form in its seed helper.
- `json_extract_scalar` is represented from the AWS Athena JSON documentation:
  <https://docs.aws.amazon.com/athena/latest/ug/extracting-data-from-JSON.html>

The copied Jaffle Shop files retain their Apache 2.0 terms in
[`UPSTREAM_LICENSE`](tests/suite_01_end_to_end_conversion/UPSTREAM_LICENSE).
