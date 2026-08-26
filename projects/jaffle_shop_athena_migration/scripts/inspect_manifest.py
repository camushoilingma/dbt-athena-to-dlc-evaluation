#!/usr/bin/env python3
"""Print dbt relation namespace resolution as CSV."""

import csv
import json
import sys
from pathlib import Path


def main() -> int:
    manifest_path = Path(sys.argv[1] if len(sys.argv) > 1 else "target/manifest.json")
    manifest = json.loads(manifest_path.read_text())
    writer = csv.writer(sys.stdout, lineterminator="\n")
    writer.writerow(
        ["unique_id", "database", "schema", "identifier", "namespace_levels", "relation_name"]
    )
    invalid_namespaces = 0

    for unique_id, node in sorted(manifest.get("nodes", {}).items()):
        if node.get("resource_type") not in {"model", "seed"}:
            continue
        database = node.get("database") or ""
        schema = node.get("schema") or ""
        identifier = node.get("alias") or node.get("name") or ""
        levels = sum(bool(part) for part in (database, schema, identifier))
        if levels != 3:
            invalid_namespaces += 1
        writer.writerow(
            [unique_id, database, schema, identifier, levels, node.get("relation_name") or ""]
        )
    return 1 if invalid_namespaces else 0


if __name__ == "__main__":
    raise SystemExit(main())
