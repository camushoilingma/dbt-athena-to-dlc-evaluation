"""Tier 2: the cross-database macros dbt projects rely on.

dbt-dlc overrides 15 of these in dbt/include/dlc/macros/utils/. The rest fall
through to the dbt-adapters defaults, which are ANSI-flavoured and may or may not
hold on DLC's Spark dialect — that is what this module measures. Anything failing
here breaks dbt_utils and dbt_date, which most real projects depend on.
"""

import pytest
from dbt.tests.adapter.utils.test_any_value import BaseAnyValue
from dbt.tests.adapter.utils.test_array_append import BaseArrayAppend
from dbt.tests.adapter.utils.test_array_concat import BaseArrayConcat
from dbt.tests.adapter.utils.test_array_construct import BaseArrayConstruct
from dbt.tests.adapter.utils.test_bool_or import BaseBoolOr
from dbt.tests.adapter.utils.test_cast import BaseCast
from dbt.tests.adapter.utils.test_cast_bool_to_text import BaseCastBoolToText
from dbt.tests.adapter.utils.test_concat import BaseConcat
from dbt.tests.adapter.utils.test_current_timestamp import BaseCurrentTimestampNaive
from dbt.tests.adapter.utils.test_date import BaseDate
from dbt.tests.adapter.utils.test_date_spine import BaseDateSpine
from dbt.tests.adapter.utils.test_date_trunc import BaseDateTrunc
from dbt.tests.adapter.utils.test_dateadd import BaseDateAdd
from dbt.tests.adapter.utils.test_datediff import BaseDateDiff
from dbt.tests.adapter.utils.test_equals import BaseEquals
from dbt.tests.adapter.utils.test_escape_single_quotes import BaseEscapeSingleQuotesBackslash
from dbt.tests.adapter.utils.test_except import BaseExcept
from dbt.tests.adapter.utils.test_generate_series import BaseGenerateSeries
from dbt.tests.adapter.utils.test_get_intervals_between import BaseGetIntervalsBetween
from dbt.tests.adapter.utils.test_get_powers_of_two import BaseGetPowersOfTwo
from dbt.tests.adapter.utils.test_hash import BaseHash
from dbt.tests.adapter.utils.test_intersect import BaseIntersect
from dbt.tests.adapter.utils.test_last_day import BaseLastDay
from dbt.tests.adapter.utils.test_length import BaseLength
from dbt.tests.adapter.utils.test_listagg import BaseListagg
from dbt.tests.adapter.utils.test_null_compare import BaseMixedNullCompare, BaseNullCompare
from dbt.tests.adapter.utils.test_position import BasePosition
from dbt.tests.adapter.utils.test_replace import BaseReplace
from dbt.tests.adapter.utils.test_right import BaseRight
from dbt.tests.adapter.utils.test_safe_cast import BaseSafeCast
from dbt.tests.adapter.utils.test_split_part import BaseSplitPart
from dbt.tests.adapter.utils.test_string_literal import BaseStringLiteral
from dbt.tests.adapter.utils.test_validate_sql import BaseValidateSqlMethod

pytestmark = pytest.mark.extended


# --- macros dbt-dlc overrides explicitly ---


class TestAnyValue(BaseAnyValue):
    pass


class TestArrayAppend(BaseArrayAppend):
    pass


class TestArrayConcat(BaseArrayConcat):
    pass


class TestArrayConstruct(BaseArrayConstruct):
    pass


class TestBoolOr(BaseBoolOr):
    pass


class TestConcat(BaseConcat):
    pass


class TestCurrentTimestamp(BaseCurrentTimestampNaive):
    # dlc__current_timestamp emits Spark's current_timestamp(), which has no zone.
    pass


class TestDate(BaseDate):
    pass


class TestDateAdd(BaseDateAdd):
    pass


class TestDateDiff(BaseDateDiff):
    pass


class TestEscapeSingleQuotes(BaseEscapeSingleQuotesBackslash):
    # dlc__escape_single_quotes uses the Spark backslash form.
    pass


class TestListagg(BaseListagg):
    pass


class TestSafeCast(BaseSafeCast):
    pass


class TestSplitPart(BaseSplitPart):
    pass


# --- macros dbt-dlc inherits from dbt-adapters unchanged ---


class TestCast(BaseCast):
    pass


class TestCastBoolToText(BaseCastBoolToText):
    pass


class TestDateSpine(BaseDateSpine):
    pass


class TestDateTrunc(BaseDateTrunc):
    pass


class TestEquals(BaseEquals):
    pass


class TestExcept(BaseExcept):
    pass


class TestGenerateSeries(BaseGenerateSeries):
    pass


class TestGetIntervalsBetween(BaseGetIntervalsBetween):
    pass


class TestGetPowersOfTwo(BaseGetPowersOfTwo):
    pass


class TestHash(BaseHash):
    pass


class TestIntersect(BaseIntersect):
    pass


class TestLastDay(BaseLastDay):
    pass


class TestLength(BaseLength):
    pass


class TestNullCompare(BaseNullCompare):
    pass


class TestMixedNullCompare(BaseMixedNullCompare):
    pass


class TestPosition(BasePosition):
    pass


class TestReplace(BaseReplace):
    pass


class TestRight(BaseRight):
    pass


class TestStringLiteral(BaseStringLiteral):
    pass


class TestValidateSqlMethod(BaseValidateSqlMethod):
    pass
