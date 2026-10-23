"""Command line:  python -m sfdm <command>

  extract              Salesforce -> data/extract/*.csv
  migrate --dry-run    transform + load + validate on CSVs, no Dynamics needed
  migrate              transform + load + validate into your Dynamics trial
"""

from __future__ import annotations

import argparse
from pathlib import Path

from . import config, dataverse, extract, load, report, transform


def cmd_extract(_args):
    print("Extracting from Salesforce...")
    extract.extract()


def cmd_migrate(args):
    source = Path(args.source) if args.source else (
        config.SAMPLE_DIR if args.dry_run else config.EXTRACT_DIR)
    mode = "dry run (no Dynamics connection)" if args.dry_run else "live load into Dynamics 365"
    print(f"Source CSVs: {source}\nMode: {mode}\n")

    print("[1/3] Transform")
    summary, issues = transform.transform(source)
    print(f"      {len(issues)} data-quality issue(s) -> data/transformed/issues.json\n")

    print("[2/3] Load")
    client = dataverse.connect(dry_run=args.dry_run)
    results, _ = load.load(client, id_map_file=None if args.dry_run else config.ID_MAP_FILE)

    print("\n[3/3] Validate")
    checks = report.validate(client, summary, results)
    name = "dry_run_report.md" if args.dry_run else "migration_report.md"
    path = report.write_report(config.REPORTS_DIR / name, mode, checks, results, issues)
    ok = all(c["ok"] for c in checks.values())
    print(f"      {'PASS' if ok else 'CHECK'} -> {path.relative_to(config.ROOT)}")
    return 0 if ok else 1


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python -m sfdm", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("extract", help="export Salesforce objects to data/extract/").set_defaults(func=cmd_extract)

    p = sub.add_parser("migrate", help="transform, load and validate")
    p.add_argument("--dry-run", action="store_true", help="simulate Dynamics; defaults to sample_data/")
    p.add_argument("--source", help="folder of Salesforce CSVs (default: data/extract/)")
    p.set_defaults(func=cmd_migrate)

    args = parser.parse_args(argv)
    return args.func(args) or 0


if __name__ == "__main__":
    raise SystemExit(main())
