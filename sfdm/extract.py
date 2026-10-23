"""Step 1 - Extract: pull records out of Salesforce into CSV files.

Uses the Salesforce REST API through `simple-salesforce`. If you prefer not to use
the API, export the same objects with Workbench or Data Loader and drop the CSVs
into data/extract/ (see docs/03-export-from-salesforce.md) - the rest of the
pipeline works the same.
"""

from __future__ import annotations

import csv
from pathlib import Path

from . import config


def fields_to_query(obj_map: dict) -> list[str]:
    """Id + every mapped field + every lookup field, without duplicates."""
    fields = ["Id", *obj_map.get("fields", {}).keys(), *obj_map.get("lookups", {}).keys()]
    return list(dict.fromkeys(fields))


def connect():
    from simple_salesforce import Salesforce

    config.load_env()
    return Salesforce(
        username=config.env("SF_USERNAME"),
        password=config.env("SF_PASSWORD"),
        security_token=config.env("SF_SECURITY_TOKEN", required=False, default=""),
        domain=config.env("SF_DOMAIN", required=False, default="login"),
    )


def extract(out_dir: Path = config.EXTRACT_DIR) -> dict[str, int]:
    mapping = config.load_mapping()
    sf = connect()
    out_dir.mkdir(parents=True, exist_ok=True)
    counts: dict[str, int] = {}

    for name in mapping["load_order"]:
        fields = fields_to_query(mapping["objects"][name])
        soql = f"SELECT {', '.join(fields)} FROM {name}"
        records = sf.query_all(soql)["records"]

        path = out_dir / f"{name}.csv"
        with open(path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=fields)
            writer.writeheader()
            for rec in records:
                writer.writerow({f: rec.get(f) if rec.get(f) is not None else "" for f in fields})
        counts[name] = len(records)
        print(f"  {name:<12} {len(records):>6} records -> {path.relative_to(config.ROOT)}")

    return counts
