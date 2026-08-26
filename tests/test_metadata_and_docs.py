"""Tier 2: relation metadata, comments and schema lifecycle.

These exercise the metadata paths that DLC serves over HiveServer2 RPCs rather
than SQL — relation listing, relation type, column comments, schema drop — which
is where an adapter fronting a gateway is most likely to diverge.
"""

import pytest
from dbt.tests.adapter.caching.test_caching import (
    BaseCachingLowercaseModel,
    BaseCachingSelectedSchemaOnly,
    BaseNoPopulateCache,
)
from dbt.tests.adapter.persist_docs.test_persist_docs import (
    BasePersistDocs,
    BasePersistDocsColumnMissing,
)
from dbt.tests.adapter.relations.test_changing_relation_type import (
    BaseChangeRelationTypeValidator,
)
from dbt.tests.adapter.relations.test_dropping_schema_named import BaseDropSchemaNamed

pytestmark = pytest.mark.extended


class TestChangeRelationType(BaseChangeRelationTypeValidator):
    """Table -> view -> incremental swaps. Requires the adapter to report the
    existing relation's true type before replacing it."""

    pass


class TestDropSchemaNamed(BaseDropSchemaNamed):
    pass


class TestPersistDocs(BasePersistDocs):
    pass


class TestPersistDocsColumnMissing(BasePersistDocsColumnMissing):
    pass


class TestCachingLowercaseModel(BaseCachingLowercaseModel):
    pass


class TestCachingSelectedSchemaOnly(BaseCachingSelectedSchemaOnly):
    pass


class TestNoPopulateCache(BaseNoPopulateCache):
    pass
