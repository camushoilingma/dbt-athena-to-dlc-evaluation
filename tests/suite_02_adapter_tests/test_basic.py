"""Tier 1: the baseline every dbt adapter is expected to pass.

Each class subclasses dbt Labs' base test unmodified. A failure here means
dbt-dlc or DLC deviates from behaviour dbt documents for all adapters.
"""

import pytest
from dbt.tests.adapter.basic.test_adapter_methods import BaseAdapterMethod
from dbt.tests.adapter.basic.test_base import BaseSimpleMaterializations
from dbt.tests.adapter.basic.test_empty import BaseEmpty
from dbt.tests.adapter.basic.test_ephemeral import BaseEphemeral
from dbt.tests.adapter.basic.test_generic_tests import BaseGenericTests
from dbt.tests.adapter.basic.test_incremental import (
    BaseIncremental,
    BaseIncrementalBadStrategy,
    BaseIncrementalNotSchemaChange,
)
from dbt.tests.adapter.basic.test_singular_tests import BaseSingularTests
from dbt.tests.adapter.basic.test_singular_tests_ephemeral import BaseSingularTestsEphemeral
from dbt.tests.adapter.basic.test_snapshot_check_cols import BaseSnapshotCheckCols
from dbt.tests.adapter.basic.test_snapshot_timestamp import BaseSnapshotTimestamp
from dbt.tests.adapter.basic.test_table_materialization import BaseTableMaterialization
from dbt.tests.adapter.basic.test_validate_connection import BaseValidateConnection

pytestmark = pytest.mark.core


class TestValidateConnection(BaseValidateConnection):
    pass


class TestEmpty(BaseEmpty):
    pass


class TestSimpleMaterializations(BaseSimpleMaterializations):
    pass


class TestTableMaterialization(BaseTableMaterialization):
    pass


class TestSingularTests(BaseSingularTests):
    pass


class TestSingularTestsEphemeral(BaseSingularTestsEphemeral):
    pass


class TestEphemeral(BaseEphemeral):
    pass


class TestGenericTests(BaseGenericTests):
    pass


class TestIncremental(BaseIncremental):
    pass


class TestIncrementalNotSchemaChange(BaseIncrementalNotSchemaChange):
    pass


class TestIncrementalBadStrategy(BaseIncrementalBadStrategy):
    pass


class TestSnapshotCheckCols(BaseSnapshotCheckCols):
    pass


class TestSnapshotTimestamp(BaseSnapshotTimestamp):
    pass


class TestAdapterMethod(BaseAdapterMethod):
    pass
