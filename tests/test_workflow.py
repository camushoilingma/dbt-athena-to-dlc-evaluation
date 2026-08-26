"""Tier 2: the day-to-day workflow surface.

Hooks, seeds, aliases, concurrency, query comments, `dbt show`, storing test
failures, `dbt clone` and unit tests. None of this is exotic — it is what a team
running dbt on a schedule uses every day.
"""

import pytest
from dbt.tests.adapter.aliases.test_aliases import BaseAliasErrors, BaseAliases
from dbt.tests.adapter.concurrency.test_concurrency import BaseConcurrency
from dbt.tests.adapter.dbt_clone.test_dbt_clone import BaseCloneNotPossible
from dbt.tests.adapter.dbt_show.test_dbt_show import BaseShowLimit, BaseShowSqlHeader
from dbt.tests.adapter.empty.test_empty import BaseTestEmpty
from dbt.tests.adapter.hooks.test_model_hooks import BasePrePostModelHooks
from dbt.tests.adapter.hooks.test_run_hooks import BaseAfterRunHooks, BasePrePostRunHooks
from dbt.tests.adapter.query_comment.test_query_comment import (
    BaseEmptyQueryComments,
    BaseMacroQueryComments,
    BaseQueryComments,
)
from dbt.tests.adapter.simple_seed.test_seed import (
    BaseBasicSeedTests,
    BaseSeedConfigFullRefreshOff,
    BaseSeedConfigFullRefreshOn,
    BaseSeedCustomSchema,
    BaseTestEmptySeed,
)
from dbt.tests.adapter.store_test_failures_tests.test_store_test_failures import (
    BaseStoreTestFailures,
)
from dbt.tests.adapter.unit_testing.test_case_insensitivity import BaseUnitTestCaseInsensivity
from dbt.tests.adapter.unit_testing.test_invalid_input import BaseUnitTestInvalidInput

pytestmark = pytest.mark.extended


class TestQueryComments(BaseQueryComments):
    pass


class TestMacroQueryComments(BaseMacroQueryComments):
    pass


class TestEmptyQueryComments(BaseEmptyQueryComments):
    pass


class TestPrePostModelHooks(BasePrePostModelHooks):
    pass


class TestPrePostRunHooks(BasePrePostRunHooks):
    pass


class TestAfterRunHooks(BaseAfterRunHooks):
    pass


class TestBasicSeedTests(BaseBasicSeedTests):
    pass


class TestSeedConfigFullRefreshOn(BaseSeedConfigFullRefreshOn):
    pass


class TestSeedConfigFullRefreshOff(BaseSeedConfigFullRefreshOff):
    pass


class TestSeedCustomSchema(BaseSeedCustomSchema):
    pass


class TestEmptySeed(BaseTestEmptySeed):
    pass


class TestAliases(BaseAliases):
    pass


class TestAliasErrors(BaseAliasErrors):
    pass


class TestConcurrency(BaseConcurrency):
    pass


class TestShowLimit(BaseShowLimit):
    pass


class TestShowSqlHeader(BaseShowSqlHeader):
    pass


class TestEmpty(BaseTestEmpty):
    pass


class TestStoreTestFailures(BaseStoreTestFailures):
    pass


class TestCloneNotPossible(BaseCloneNotPossible):
    """dbt-dlc defines no `can_clone_table`, so dbt should fall back to
    re-running the model rather than issuing a shallow clone."""

    pass


class TestUnitTestCaseInsensitivity(BaseUnitTestCaseInsensivity):
    pass


class TestUnitTestInvalidInput(BaseUnitTestInvalidInput):
    pass
