"""Step 2 - Transform: turn Salesforce CSV rows into Dataverse-ready records.

Pure Python, no network calls, so it is fully unit-tested (tests/test_transform.py).
Every problem found is recorded as an "issue" instead of crashing, so you get a
complete data-quality picture in one run.
"""

from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path

from . import config

DATE_FORMATS = ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S.%f%z", "%d/%m/%Y", "%m/%d/%Y")


@dataclass
class Issue:
    object: str
    sf_id: str
    field: str
    level: str      # "warning" = loaded with a gap, "error" = record skipped
    message: str


@dataclass
class Record:
    sf_id: str
    payload: dict
    lookups: dict = field(default_factory=dict)   # navigation -> [parent_object, parent_sf_id]


# --------------------------------------------------------------------------- values

def convert(value: str, kind: str):
    """Convert a CSV string to the Dataverse type. Raises ValueError if impossible."""
    value = value.strip()
    if kind == "string":
        return value
    if kind == "int":
        return int(float(value.replace(",", "").replace(" ", "")))
    if kind == "money":
        return round(float(value.replace(",", "").replace(" ", "")), 2)
    if kind == "date":
        for fmt in DATE_FORMATS:
            try:
                return datetime.strptime(value, fmt).strftime("%Y-%m-%d")
            except ValueError:
                continue
        raise ValueError(f"unrecognised date '{value}'")
    raise ValueError(f"unknown type '{kind}'")


def column_spec(spec) -> tuple[str, str]:
    """Mapping entries are either 'column' or {column: ..., type: ...}."""
    if isinstance(spec, str):
        return spec, "string"
    return spec["column"], spec.get("type", "string")


# --------------------------------------------------------------------------- records

def transform_row(name: str, row: dict, obj_map: dict, known_ids: dict[str, set]) -> tuple[Record | None, list[Issue]]:
    issues: list[Issue] = []
    sf_id = (row.get("Id") or "").strip()
    if not sf_id:
        return None, [Issue(name, "", "Id", "error", "row has no Salesforce Id - skipped")]

    payload: dict = {obj_map["key_column"]: sf_id}

    for sf_field, spec in obj_map.get("fields", {}).items():
        raw = row.get(sf_field)
        if raw is None or raw.strip() == "":
            continue  # send nothing rather than a blank, so Dynamics keeps its defaults
        column, kind = column_spec(spec)
        try:
            payload[column] = convert(raw, kind)
        except ValueError as exc:
            issues.append(Issue(name, sf_id, sf_field, "warning", f"{exc} - field left empty"))

    for column, template in obj_map.get("defaults", {}).items():
        payload[column] = template.format_map(_Blank(row)) if isinstance(template, str) else template

    lookups: dict = {}
    for sf_field, spec in obj_map.get("lookups", {}).items():
        parent_id = (row.get(sf_field) or "").strip()
        if not parent_id:
            continue
        parent = spec["parent_object"]
        if parent_id not in known_ids.get(parent, set()):
            issues.append(Issue(name, sf_id, sf_field, "warning",
                                f"parent {parent} {parent_id} not found in export - loaded without link"))
            continue
        lookups[spec["navigation"]] = [parent, parent_id]

    required = [c for c in ("name", "lastname") if c in obj_map.get("fields", {}).values()]
    for column in required:
        if column not in payload:
            issues.append(Issue(name, sf_id, column, "error", f"required column '{column}' is empty - skipped"))
            return None, issues

    return Record(sf_id, payload, lookups), issues


class _Blank(dict):
    """format_map helper: missing or empty placeholders become ''."""
    def __missing__(self, key):
        return ""


def read_csv(path: Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def transform(source_dir: Path, out_dir: Path = config.TRANSFORM_DIR, mapping: dict | None = None):
    mapping = mapping or config.load_mapping()
    rows = {name: read_csv(source_dir / f"{name}.csv") for name in mapping["load_order"]}
    known_ids = {name: {r["Id"].strip() for r in rs if r.get("Id")} for name, rs in rows.items()}

    out_dir.mkdir(parents=True, exist_ok=True)
    all_issues: list[Issue] = []
    summary: dict[str, dict] = {}

    for name in mapping["load_order"]:
        obj_map = mapping["objects"][name]
        records: list[Record] = []
        for row in rows[name]:
            record, issues = transform_row(name, row, obj_map, known_ids)
            all_issues.extend(issues)
            if record:
                records.append(record)

        with open(out_dir / f"{name}.jsonl", "w", encoding="utf-8") as fh:
            for rec in records:
                fh.write(json.dumps(asdict(rec), ensure_ascii=False) + "\n")

        summary[name] = {"source": len(rows[name]), "transformed": len(records)}
        print(f"  {name:<12} {len(rows[name]):>4} rows -> {len(records):>4} records")

    with open(out_dir / "issues.json", "w", encoding="utf-8") as fh:
        json.dump([asdict(i) for i in all_issues], fh, indent=2)

    return summary, all_issues


def read_transformed(name: str, in_dir: Path = config.TRANSFORM_DIR) -> list[Record]:
    with open(in_dir / f"{name}.jsonl", encoding="utf-8") as fh:
        return [Record(**json.loads(line)) for line in fh if line.strip()]
