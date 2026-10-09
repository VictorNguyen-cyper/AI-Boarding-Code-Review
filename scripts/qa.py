#!/usr/bin/env python3
"""Project status for the 3-tier acceptance process.

Usage (normally through ./qa in the repository root):
    python3 scripts/qa.py [--log P] [--findings P] [--boundary P] [--today YYYY-MM-DD]

Shows, for every feature in log.csv, which steps are done and what to do next.
Classification follows classification.md (findings.csv, boundary.csv); the files
themselves are validated by check-log.py and check-classification.py.

The script only reads files; it never writes to them and never classifies a finding
as true or false (rule A.1).
"""
import argparse
import importlib.util
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _load(name, filename):
    # The checker filenames have a hyphen, so load them by path.
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


check_log = _load("check_log", "check-log.py")
check_classification = _load("check_classification", "check-classification.py")


def rows(path, columns):
    """Well-formed rows of a CSV as dicts; [] when the file is missing or its header is wrong."""
    if not Path(path).exists():
        return []
    header, data = check_log.read(path)
    if header != columns:
        return []
    return [dict(zip(columns, r)) for r in data if len(r) == len(columns) and r[0]]


def artifact(prefix, name):
    # review.sh writes review-<name>.md with the raw name; also accept the scan.sh-style slug.
    slug = name.replace(" ", "-").replace("/", "-")
    return any((ROOT / f"{prefix}-{n}.md").exists() for n in {name, slug})


def scan_done(row):
    slug = row["Feature"].replace(" ", "-").replace("/", "-")
    return bool(row["Automated scan findings"]) or (ROOT / "scan-results" / slug / "summary.txt").exists()


def status(args):
    if not Path(args.log).exists() or check_log.read(args.log)[0] != check_log.COLUMNS:
        print(f"{args.log} is missing or has the wrong header. Run ./qa check.")
        return 1
    features = rows(args.log, check_log.COLUMNS)
    if not features:
        print("log.csv has no features yet. Start with: add a row to log.csv (see README.md).")
        return 0

    findings = rows(args.findings, check_classification.FINDING_COLUMNS)
    boundary = {r["Feature"]: r for r in rows(args.boundary, check_classification.BOUNDARY_COLUMNS)}

    def mark(ok):
        return "✓" if ok else "·"

    today = check_classification.parse_date(args.today) if args.today else date.today()
    if today is None:
        print(f"--today must be a date YYYY-MM-DD, got '{args.today}'.")
        return 2
    print(f"Status on {today.isoformat()}  (✓ done, · not yet)\n")
    print(f"{'Feature':<28} Manual T1 T2 T3  Classified  Boundary  Next step")
    print("-" * 96)
    due = []
    for row in features:
        name = row["Feature"]
        manual = bool(row["Manual check"])
        t1 = scan_done(row)
        t2 = artifact("test-case", name)
        t3 = bool(row["AI review findings"]) or artifact("review", name)
        mine = [f for f in findings if f["Feature"] == name]
        classified = sum(1 for f in mine if f["Verdict"])
        has_raw_findings = any(
            row[c] and row[c] != "(no findings)" for c in ("Automated scan findings", "AI review findings")
        )
        answers = boundary.get(name) or {}
        bounded = all(answers.get(q) for q in check_classification.BOUNDARY_QUESTIONS)

        if not manual:
            step = "Try it by hand, fill 'Manual check' (before any scan)"
        elif not t1:
            step = f'./qa scan "{name}" <code dir>'
        elif not t2:
            step = f"Write test-case-{name}.md (templates/), run the cases"
        elif not t3:
            step = f'./qa review "{name}" <requirements> <code dir>'
        elif has_raw_findings and not mine:
            step = "Add one row per problem to findings.csv (classification.md)"
        elif classified < len(mine):
            step = f"Fill 'Verdict' for {len(mine) - classified} problem(s) in findings.csv"
        elif not bounded:
            step = "Answer the 3 boundary questions in boundary.csv"
        elif row["Bugs found later"]:
            step = "Complete"
        elif not answers.get("Live since"):
            step = f"Fill 'Live since' in boundary.csv when it goes into real use (or '{check_classification.NOT_LIVE}')"
        elif answers["Live since"] == check_classification.NOT_LIVE:
            step = "Not live: no one-week check; report it as missing data"
        else:
            due_on = check_classification.parse_date(answers["Live since"]) + timedelta(
                days=check_classification.FOLLOW_UP_DAYS
            )
            if today >= due_on:
                due.append(name)
                step = "DUE: fill 'Bugs found later' in log.csv ('(no findings)' if nothing broke)"
            else:
                step = f"Wait until {due_on}, then fill 'Bugs found later' in log.csv"

        print(
            f"{name[:28]:<28} {mark(manual):^6} {mark(t1):^2} {mark(t2):^2} {mark(t3):^2}  "
            f"{f'{classified}/{len(mine)}':^10}  {mark(bounded):^8}  {step}"
        )

    print()
    if due:
        print(f"⚠ One-week follow-up due: {', '.join(due)}")
    complete = sum(1 for r in features if r["Bugs found later"])
    print(f"{len(features)} feature(s) logged; {complete} with 'Bugs found later' filled. Plan target: 15–25.")
    return 0


def main(argv):
    p = argparse.ArgumentParser(prog="qa status")
    p.add_argument("--log", default=str(ROOT / "log.csv"))
    p.add_argument("--findings", default=str(ROOT / "findings.csv"))
    p.add_argument("--boundary", default=str(ROOT / "boundary.csv"))
    p.add_argument("--today", help="override today's date (YYYY-MM-DD), for testing")
    return status(p.parse_args(argv))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
