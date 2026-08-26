"""Tier 2: incremental behaviour beyond the baseline.

dbt-dlc validates four strategies (append, merge, insert_overwrite, microbatch)
in macros/materializations/incremental/validate.sql. It has no delete+insert, so
the predicates suite is re-pointed at merge, the way dbt-spark does it.
"""

import pytest
from dbt.tests.adapter.incremental.test_incremental_merge_exclude_columns import (
    BaseMergeExcludeColumns,
)
from dbt.tests.adapter.incremental.test_incremental_microbatch import BaseMicrobatch
from dbt.tests.adapter.incremental.test_incremental_on_schema_change import (
    BaseIncrementalOnSchemaChange,
)
from dbt.tests.adapter.incremental.test_incremental_predicates import BaseIncrementalPredicates
from dbt.tests.adapter.incremental.test_incremental_unique_id import BaseIncrementalUniqueKey

pytestmark = pytest.mark.extended


class TestIncrementalOnSchemaChange(BaseIncrementalOnSchemaChange):
    pass


class TestIncrementalUniqueKey(BaseIncrementalUniqueKey):
    pass


class TestMergeExcludeColumns(BaseMergeExcludeColumns):
    pass


class TestIncrementalPredicatesMerge(BaseIncrementalPredicates):
    @pytest.fixture(scope="class")
    def project_config_update(self):
        return {
            "models": {
                "+incremental_predicates": ["dbt_internal_dest.id != 2"],
                "+incremental_strategy": "merge",
                "+unique_key": "id",
            }
        }


class TestMicrobatch(BaseMicrobatch):
    """dbt-dlc wraps microbatch around insert_overwrite and requires partition_by."""

    @pytest.fixture(scope="class")
    def microbatch_model_sql(self):
        return """
{{ config(
    materialized='incremental',
    incremental_strategy='microbatch',
    partition_by='event_time',
    event_time='event_time',
    batch_size='day',
    begin=modules.datetime.datetime(2020, 1, 1, 0, 0, 0)
) }}
select * from {{ ref('input_model') }}
"""
