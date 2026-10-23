"""Step 4 - Validate: reconcile counts and write a Markdown migration report."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from . import config


def validate(client, transform_summary: dict, load_results: dict) -> dict:
    mapping = config.load_mapping()
    checks = {}
    for name in mapping["load_order"]:
        obj = mapping["objects"][name]
        in_target = client.count_migrated(obj["entity_set"], obj["target"] + "id", obj["key_column"])
        expected = transform_summary[name]["transformed"]
        checks[name] = {
            "source": transform_summary[name]["source"],
            "expected": expected,
            "in_dynamics": in_target,
            "ok": in_target == expected and load_results[name]["failed"] == 0,
        }
    return checks


def write_report(path: Path, mode: str, checks: dict, load_results: dict, issues: list) -> Path:
    passed = all(c["ok"] for c in checks.values())
    lines = [
        "# Migration report",
        "",
        f"- **Run:** {datetime.now(timezone.utc):%Y-%m-%d %H:%M UTC}",
        f"- **Mode:** {mode}",
        f"- **Result:** {'PASS - every transformed record is in Dynamics' if passed else 'CHECK - see below'}",
        "",
        "## Reconciliation",
        "",
        "| Object | Salesforce rows | Valid after transform | In Dynamics | Created | Updated | Failed | Status |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for name, c in checks.items():
        r = load_results[name]
        lines.append(f"| {name} | {c['source']} | {c['expected']} | {c['in_dynamics']} | "
                     f"{r['created']} | {r['updated']} | {r['failed']} | {'OK' if c['ok'] else 'CHECK'} |")

    lines += ["", f"## Data-quality issues ({len(issues)})", ""]
    if issues:
        lines += ["| Object | Salesforce Id | Field | Level | Detail |", "|---|---|---|---|---|"]
        for i in issues:
            lines.append(f"| {i.object} | {i.sf_id} | {i.field} | {i.level} | {i.message} |")
    else:
        lines.append("None found.")

    failures = [(n, e) for n, r in load_results.items() for e in r["errors"]]
    if failures:
        lines += ["", "## Load failures", ""]
        for name, err in failures:
            lines.append(f"- **{name} {err['sf_id']}**: {err['error']}")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path
