"""Pytest configuration for running dbt Labs' adapter conformance suite on DLC.

`dbt-tests-adapter` is the suite dbt Labs publishes for adapter maintainers: a
library of base test classes that every adapter is expected to subclass and pass.
The tests here subclass them unmodified wherever possible, so a failure means the
adapter (or DLC) deviates from documented dbt behaviour rather than that the test
was bent to fit.

Connection settings come from the repository-root .env. Nothing
account-specific lives in source control.
"""

import os
import pytest
import yaml
from dbt.tests.util import write_file

from envfile import load_dotenv

# The fixtures that build a throwaway dbt project per test class.
pytest_plugins = ["dbt.tests.fixtures.project"]

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))


def pytest_configure(config):
    load_dotenv()

    # dbt reads DBT_* as CLI flags. The repo's .env points DBT_TARGET at the
    # showcase project's `dev` target, but this suite builds its own profile
    # whose only target is `default`, so leaving it set aborts every dbt call.
    for leaked in ("DBT_TARGET", "DBT_PROFILES_DIR", "DBT_PROJECT_DIR"):
        os.environ.pop(leaked, None)


def _required(name):
    val = os.environ.get(name)
    if not val:
        pytest.exit(f"missing {name} — set it in {REPO_ROOT}/.env", returncode=2)
    return val


def _connect(database):
    """Open a raw driver connection, bypassing dbt, against `database`."""
    import dlc_sql

    return dlc_sql.connect(
        host=_required("DLC_HOST"),
        port=int(os.environ.get("DLC_PORT", "10009")),
        engine_name=_required("DLC_ENGINE_NAME"),
        resource_group_name=_required("DLC_RESOURCE_GROUP"),
        catalog=os.environ.get("DLC_CATALOG", "DataLakeCatalog"),
        database=database,
        auth_mode="AccessKey",
        transport_mode=os.environ.get("DLC_TRANSPORT_MODE", "binary"),
        secret_id=_required("TENCENTCLOUD_SECRET_ID"),
        secret_key=_required("TENCENTCLOUD_SECRET_KEY"),
        socket_timeout_ms=600000,
    )


def _bootstrap_schema():
    """A database that already exists, used only to host the bootstrap DDL."""
    for name in ("DLC_BOOTSTRAP_SCHEMA", "DLC_SHOWCASE_SCHEMA", "DLC_DATABASE"):
        if os.environ.get(name):
            return os.environ[name]
    return "default"


def _ddl(statement):
    conn = _connect(_bootstrap_schema())
    try:
        cur = conn.cursor()
        cur.execute(statement)
    finally:
        try:
            conn.close()
        except Exception:
            pass


@pytest.fixture(scope="class")
def dlc_schema_bootstrap(unique_schema):
    """Create the per-test-class DLC database before any dbt connection opens.

    Set DLC_CONFORMANCE_BOOTSTRAP=0 to exercise the adapter's native schema path.
    """
    if os.environ.get("DLC_CONFORMANCE_BOOTSTRAP", "1") != "1":
        yield unique_schema
        return

    _ddl(f"create database if not exists {unique_schema}")
    yield unique_schema
    if os.environ.get("DLC_CONFORMANCE_KEEP_SCHEMA") != "1":
        try:
            _ddl(f"drop database if exists {unique_schema} cascade")
        except Exception as exc:  # teardown must not mask a test failure
            print(f"warning: could not drop {unique_schema}: {exc}")


@pytest.fixture(scope="class")
def dbt_project_yml(project_root, project_config_update, vars_yml):
    """Upstream fixture, plus an Iceberg default for every relation.

    dbt-dlc 1.1.1 defaults `file_format` to Iceberg, matching DLC's
    transactional feature set (merge, delete+insert, snapshots). The fixture keeps
    that explicit so older historical runs and current runs are easy to compare.
    Set DLC_CONFORMANCE_FILE_FORMAT to override.
    """
    project_config = {
        "name": "test",
        "profile": "test",
        "flags": {"send_anonymous_usage_stats": False},
    }
    if isinstance(project_config_update, str):
        project_config_update = yaml.safe_load(project_config_update)
    if project_config_update:
        project_config.update(project_config_update)

    file_format = os.environ.get("DLC_CONFORMANCE_FILE_FORMAT", "iceberg")
    if file_format != "none":
        for resource_type in ("models", "seeds", "snapshots"):
            section = project_config.setdefault(resource_type, {})
            if isinstance(section, dict):
                section.setdefault("+file_format", file_format)

    write_file(yaml.safe_dump(project_config), project_root, "dbt_project.yml")
    return project_config


@pytest.fixture(scope="class")
def dbt_profile_target(dlc_schema_bootstrap):
    # Depending on the bootstrap fixture is what orders it before the connection.
    return {
        "type": "dlc",
        "threads": int(os.environ.get("DBT_THREADS", "4")),
        "host": _required("DLC_HOST"),
        "port": int(os.environ.get("DLC_PORT", "10009")),
        "engine_name": _required("DLC_ENGINE_NAME"),
        "resource_group_name": _required("DLC_RESOURCE_GROUP"),
        "catalog": os.environ.get("DLC_CATALOG", "DataLakeCatalog"),
        "auth_mode": "AccessKey",
        "secret_id": _required("TENCENTCLOUD_SECRET_ID"),
        "secret_key": _required("TENCENTCLOUD_SECRET_KEY"),
        "transport_mode": os.environ.get("DLC_TRANSPORT_MODE", "binary"),
        # DLC is serverless: a cold resource group can take minutes to start.
        "socket_timeout_ms": 600000,
        "connect_retries": 3,
        "connect_timeout": 30,
    }
