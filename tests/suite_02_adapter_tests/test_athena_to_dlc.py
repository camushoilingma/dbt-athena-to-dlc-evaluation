"""High-value dbt-athena Iceberg fixtures converted to dbt-dlc.

Source corpus:
https://github.com/dbt-labs/dbt-adapters/tree/main/dbt-athena/tests/functional/adapter

These tests preserve the dbt Labs inputs and row-level assertions where the
feature is portable. Only adapter configuration and merge aliases are changed.
Athena service integrations are listed in athena_to_dlc_matrix.csv instead of
being simulated here.
"""

import pytest
from dbt.artifacts.schemas.results import RunStatus
from dbt.tests.adapter.basic.test_base import BaseSimpleMaterializations
from dbt.tests.adapter.basic.test_incremental import BaseIncremental
from dbt.tests.adapter.basic.test_snapshot_check_cols import BaseSnapshotCheckCols
from dbt.tests.adapter.basic.test_snapshot_timestamp import BaseSnapshotTimestamp
from dbt.tests.adapter.incremental.test_incremental_merge_exclude_columns import (
    BaseMergeExcludeColumns,
)
from dbt.tests.adapter.incremental.test_incremental_on_schema_change import (
    BaseIncrementalOnSchemaChange,
)
from dbt.tests.adapter.incremental.test_incremental_predicates import (
    BaseIncrementalPredicates,
)
from dbt.tests.adapter.incremental.test_incremental_unique_id import (
    BaseIncrementalUniqueKey,
)
from dbt.tests.adapter.simple_seed.test_seed import BaseBasicSeedTests
from dbt.tests.util import run_dbt

pytestmark = pytest.mark.athena_conversion


ICEBERG_MODELS = {"+file_format": "iceberg"}
ICEBERG_MERGE_MODELS = {
    "+file_format": "iceberg",
    "+incremental_strategy": "merge",
}


class TestAthenaIcebergMaterializationsToDlc(BaseSimpleMaterializations):
    @pytest.fixture(scope="class")
    def project_config_update(self):
        return {"models": ICEBERG_MODELS}


class TestAthenaIcebergAppendToDlc(BaseIncremental):
    @pytest.fixture(scope="class")
    def project_config_update(self):
        return {
            "name": "athena_iceberg_append_to_dlc",
            "models": {
                "+file_format": "iceberg",
                "+incremental_strategy": "append",
            },
        }


class TestAthenaIcebergUniqueKeysToDlc(BaseIncrementalUniqueKey):
    @pytest.fixture(scope="class")
    def project_config_update(self):
        return {"models": ICEBERG_MERGE_MODELS}

    @pytest.mark.xfail(reason="DLC merge requires a non-empty unique_key")
    def test__no_unique_keys(self, project):
        super().test__no_unique_keys(project)

    @pytest.mark.skip(reason="An empty unique_key is outside the conversion contract")
    def test__empty_str_unique_key(self, project):
        pass

    @pytest.mark.skip(reason="An empty unique_key is outside the conversion contract")
    def test__empty_unique_key_list(self, project):
        pass


class TestAthenaIcebergIncrementalPredicatesToDlc(BaseIncrementalPredicates):
    @pytest.fixture(scope="class")
    def project_config_update(self):
        return {
            "models": {
                "+file_format": "iceberg",
                "+incremental_strategy": "merge",
                "+incremental_predicates": [
                    "DBT_INTERNAL_SOURCE.id <> 3",
                    "DBT_INTERNAL_DEST.id <> 2",
                ],
            }
        }


class TestAthenaIcebergMergeExcludeColumnsToDlc(BaseMergeExcludeColumns):
    @pytest.fixture(scope="class")
    def project_config_update(self):
        return {"models": ICEBERG_MERGE_MODELS}


class TestAthenaIcebergOnSchemaChangeToDlc(BaseIncrementalOnSchemaChange):
    @pytest.fixture(scope="class")
    def project_config_update(self):
        return {"models": ICEBERG_MODELS}


class TestAthenaIcebergSnapshotCheckToDlc(BaseSnapshotCheckCols):
    @pytest.fixture(scope="class")
    def project_config_update(self):
        return {"snapshots": {"+file_format": "iceberg"}}


class TestAthenaIcebergSnapshotTimestampToDlc(BaseSnapshotTimestamp):
    @pytest.fixture(scope="class")
    def project_config_update(self):
        return {"snapshots": {"+file_format": "iceberg"}}


class TestAthenaSeedToDlc(BaseBasicSeedTests):
    pass


class TestAthenaDocsGenerateToDlc:
    @pytest.fixture(scope="class")
    def models(self):
        return {
            "model.sql": "{{ config(materialized='table', file_format='iceberg') }}\nselect 1 as id\n"
        }

    @pytest.fixture(scope="class")
    def macros(self):
        return {
            "get_catalog_relations.sql": """
{% macro get_catalog_relations(information_schema, relations) %}
    {{ return(adapter.get_catalog_by_relations(information_schema, relations)) }}
{% endmacro %}
"""
        }

    def test_generate_docs(self, project):
        results = run_dbt(["run"])
        assert len(results) == 1
        assert results[0].status == RunStatus.Success

        catalog = run_dbt(["--warn-error", "docs", "generate"])
        assert catalog.errors is None
        assert "model.test.model" in catalog.nodes
