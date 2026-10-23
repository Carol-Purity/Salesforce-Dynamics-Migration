"""Paths, settings and the field-mapping file."""

from __future__ import annotations

import os
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
MAPPING_FILE = ROOT / "mapping" / "field_mapping.yaml"
DATA_DIR = ROOT / "data"
EXTRACT_DIR = DATA_DIR / "extract"          # Salesforce CSVs land here
TRANSFORM_DIR = DATA_DIR / "transformed"    # Dataverse-ready JSON lands here
ID_MAP_FILE = DATA_DIR / "id_map.json"      # Salesforce Id -> Dataverse GUID
REPORTS_DIR = ROOT / "reports"
SAMPLE_DIR = ROOT / "sample_data"


def load_env() -> None:
    """Read settings from a .env file in the project root, if there is one."""
    try:
        from dotenv import load_dotenv
    except ImportError:  # python-dotenv is optional
        return
    load_dotenv(ROOT / ".env")


def env(name: str, required: bool = True, default: str | None = None) -> str | None:
    value = os.getenv(name, default)
    if required and not value:
        raise SystemExit(
            f"Missing setting {name}. Copy .env.example to .env and fill it in "
            f"(see docs/02-set-up-dynamics.md)."
        )
    return value


def load_mapping(path: Path = MAPPING_FILE) -> dict:
    with open(path, encoding="utf-8") as fh:
        mapping = yaml.safe_load(fh)
    for name in mapping["load_order"]:
        if name not in mapping["objects"]:
            raise ValueError(f"load_order lists {name} but it has no mapping")

    # Dynamics adds your publisher prefix to custom columns (e.g. cr8a1_salesforceid).
    # Set SF_ID_COLUMN in .env instead of editing every object above.
    load_env()
    override = os.getenv("SF_ID_COLUMN")
    if override:
        for obj in mapping["objects"].values():
            obj["key_column"] = override
    return mapping
