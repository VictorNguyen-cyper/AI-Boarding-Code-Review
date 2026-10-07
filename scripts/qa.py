#!/usr/bin/env python3
"""Project status and data checks for the 3-tier acceptance process.

Usage (normally through ./qa in the repository root):
    python3 scripts/qa.py status [--log P] [--features P] [--findings P] [--today YYYY-MM-DD]
    python3 scripts/qa.py check  [--log P] [--features P] [--findings P]

status  shows, for every feature in log.csv, which steps are done and what to do next,
        including features whose one-week follow-up ("Bugs found later") is due.
check   validates features.csv and findings.csv (log.csv itself is checked by check-log.py).

The script only reads files; it never writes to them and never classifies a finding
as true or false (rule A.1).
"""
import csv
import importlib.util
import re
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Reuse the column names and NFC normalization of check-log.py (its filename has a hyphen).
_spec = importlib.util.spec_from_file_location("check_log", ROOT / "scripts" / "check-log.py")
check_log = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(check_log)
normalize = check_log.normalize

# The last three are the boundary questions of plan section 8 (table 4).
BOUNDARY_COLUMNS = ["Real user data", "Public internet", "Over 6 months"]
FEATURE_COLUMNS = ["Feature", "Shipped on", "Follow-up checked on"] + BOUNDARY_COLUMNS
FINDING_COLUMNS = [
    "Feature",
    "Tier",
    "Source",
    "Criterion",
    "Location",
    "Severity",
    "Verdict",
    "Classified on",
    "Note",
]
# "Later" = a bug that showed up after shipping (the "Bugs found later" column, itemized).
TIERS = {"1", "2", "3", "Later"}
VERDICTS = {"True positive", "False positive", "Unsure"}
SEVERITIES = {"Critical", "High", "Medium", "Low"}
CRITERION = re.compile(r"^C\d{2}$")
FOLLOW_UP_DAYS = 7  # section 5.1: "after 1 week of real use"


def read_rows(path):
    if not Path(path).exists():
        return None, []
    with open(path, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f))
    if not rows:
        return [], []
    header = [normalize(c) for c in rows[0]]
    return header, [[normalize(c) for c in r] for r in rows[1:]]


def parse_date(s):
    try:
        return date.fromisoformat(s)
    except ValueError:
        return None


def log_features(log_path):
    header, data = read_rows(log_path)
    if header != check_log.COLUMNS:
        return None
    return [dict(zip(check_log.COLUMNS, r)) for r in data if len(r) == len(check_log.COLUMNS) and r[0]]


def validate_features(path, known):
    errors = []
    header, data = read_rows(path)
    if header is None:
        return [f"{path} not found."]
    if header != FEATURE_COLUMNS:
        return [f"{path}: header must be exactly: {','.join(FEATURE_COLUMNS)}"]
    seen = set()
    for line_no, row in enumerate(data, start=2):
        if not any(row):
            errors.append(f"{path} line {line_no}: empty row, please remove it.")
            continue
        if len(row) != len(FEATURE_COLUMNS):
            errors.append(f"{path} line {line_no}: has {len(row)} cells, expected {len(FEATURE_COLUMNS)}.")
            continue
        name, shipped, checked = row[:3]
        if name not in known:
            errors.append(f"{path} line {line_no}: feature '{name}' has no row in log.csv.")
        if name in seen:
            errors.append(f"{path} line {line_no}: duplicate feature '{name}'.")
        seen.add(name)
        for col, value in (("Shipped on", shipped), ("Follow-up checked on", checked)):
            if value and not parse_date(value):
                errors.append(f"{path} line {line_no}: '{col}' must be a date YYYY-MM-DD, got '{value}'.")
        if checked and not shipped:
            errors.append(f"{path} line {line_no}: 'Follow-up checked on' is filled but 'Shipped on' is empty.")
        for col, value in zip(BOUNDARY_COLUMNS, row[3:]):
            if value and value not in ("Yes", "No"):
                errors.append(f"{path} line {line_no}: '{col}' must be Yes or No, got '{value}'.")
        s, c = parse_date(shipped), parse_date(checked)
        if s and c and c < s + timedelta(days=FOLLOW_UP_DAYS):
            errors.append(
                f"{path} line {line_no}: follow-up on {checked} is less than {FOLLOW_UP_DAYS} days "
                f"after shipping ({shipped}); section 5.1 asks for one week of real use."
            )
    return errors


def validate_findings(path, known):
    errors = []
    header, data = read_rows(path)
    if header is None:
        return [f"{path} not found."]
    if header != FINDING_COLUMNS:
        return [f"{path}: header must be exactly: {','.join(FINDING_COLUMNS)}"]
    for line_no, row in enumerate(data, start=2):
        where = f"{path} line {line_no}"
        if not any(row):
            errors.append(f"{where}: empty row, please remove it.")
            continue
        if len(row) != len(FINDING_COLUMNS):
            errors.append(f"{where}: has {len(row)} cells, expected {len(FINDING_COLUMNS)}.")
            continue
        c = dict(zip(FINDING_COLUMNS, row))
        if c["Feature"] not in known:
            errors.append(f"{where}: feature '{c['Feature']}' has no row in log.csv.")
        if c["Tier"] not in TIERS:
            errors.append(f"{where}: 'Tier' must be 1, 2, 3 or Later, got '{c['Tier']}'.")
        if not c["Source"]:
            errors.append(f"{where}: 'Source' is empty (tool name, test case ID or reviewing model).")
        if c["Criterion"] and not CRITERION.match(c["Criterion"]):
            errors.append(f"{where}: 'Criterion' must look like C03 or be empty, got '{c['Criterion']}'.")
        if c["Severity"] and c["Severity"] not in SEVERITIES:
            errors.append(f"{where}: 'Severity' must be one of {', '.join(sorted(SEVERITIES))}, got '{c['Severity']}'.")
        if c["Verdict"] and c["Verdict"] not in VERDICTS:
            errors.append(f"{where}: 'Verdict' must be one of {', '.join(sorted(VERDICTS))}, got '{c['Verdict']}'.")
        if c["Verdict"] and not parse_date(c["Classified on"]):
            errors.append(f"{where}: 'Verdict' is filled, so 'Classified on' needs a date YYYY-MM-DD.")
        if c["Classified on"] and not c["Verdict"]:
            errors.append(f"{where}: 'Classified on' is filled but 'Verdict' is empty.")
    return errors


def artifact(prefix, name):
    # review.sh writes review-<name>.md with the raw name; also accept the scan.sh-style slug.
    slug = name.replace(" ", "-").replace("/", "-")
    return any((ROOT / f"{prefix}-{n}.md").exists() for n in {name, slug})


def scan_done(row):
    slug = row["Feature"].replace(" ", "-").replace("/", "-")
    return bool(row["Automated scan findings"]) or (ROOT / "scan-results" / slug / "summary.txt").exists()


def status(args, today):
    features = log_features(args.log)
    if features is None:
        print(f"{args.log} is missing or has the wrong header. Run ./qa check.")
        return 1
    if not features:
        print("log.csv has no features yet. Start with: add a row to log.csv (see README.md, step 1).")
        return 0

    _, ship_rows = read_rows(args.features)
    shipping = {r[0]: r for r in ship_rows if len(r) == len(FEATURE_COLUMNS)}
    _, finding_rows = read_rows(args.findings)
    findings = [dict(zip(FINDING_COLUMNS, r)) for r in finding_rows if len(r) == len(FINDING_COLUMNS)]

    def mark(ok):
        return "✓" if ok else "·"

    print(f"Status on {today.isoformat()}  (✓ done, · not yet)\n")
    print(f"{'Feature':<28} Manual T1 T2 T3  Classified  Follow-up        Next step")
    print("-" * 100)
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

        shipped_on, checked_on = (shipping.get(name) or [name, "", ""])[1:3]
        shipped = parse_date(shipped_on)
        if row["Bugs found later"] or checked_on:
            follow = "done"
        elif not shipped:
            follow = "not shipped"
        else:
            due_on = shipped + timedelta(days=FOLLOW_UP_DAYS)
            follow = f"DUE {due_on}" if due_on <= today else f"on {due_on}"
            if due_on <= today:
                due.append(name)

        if not manual:
            step = "Try it by hand, fill 'Manual check' (before any scan)"
        elif not t1:
            step = f'./qa scan "{name}" <code dir>'
        elif not t2:
            step = f"Write test-case-{name}.md (templates/), run the cases"
        elif not t3:
            step = f'./qa review "{name}" <requirements> <code dir>'
        elif has_raw_findings and not mine:
            step = "Itemize findings into findings.csv"
        elif classified < len(mine):
            step = f"Classify {len(mine) - classified} finding(s) in findings.csv"
        elif not all((shipping.get(name) or [""] * 6)[3:6]):
            step = "Answer the 3 boundary questions in features.csv"
        elif not shipped:
            step = "Fill 'Shipped on' in features.csv when it goes live"
        elif follow.startswith("DUE"):
            step = "Fill 'Bugs found later' in log.csv + 'Follow-up checked on'"
        elif follow == "done":
            step = "Complete"
        else:
            step = "Wait for the one-week follow-up"

        print(
            f"{name[:28]:<28} {mark(manual):^6} {mark(t1):^2} {mark(t2):^2} {mark(t3):^2}  "
            f"{f'{classified}/{len(mine)}':^10}  {follow:<16} {step}"
        )

    print()
    if due:
        print(f"⚠ One-week follow-up due: {', '.join(due)}")
    total = len(features)
    complete = sum(1 for r in features if r["Bugs found later"] or (shipping.get(r["Feature"]) or ["", "", ""])[2])
    print(f"{total} feature(s) logged; {complete} with the one-week follow-up done. Plan target: 15–25.")
    return 0


def check(args):
    features = log_features(args.log)
    if features is None:
        print(f"{args.log} is missing or invalid; fix it first (python3 scripts/check-log.py).")
        return 1
    known = {r["Feature"] for r in features}
    errors = []
    for path, validate in ((args.features, validate_features), (args.findings, validate_findings)):
        errs = validate(path, known)
        errors += errs
        if not errs:
            print(f"{path}: valid.")
    for e in errors:
        print(f"  - {e}")
    return 1 if errors else 0


def main(argv):
    import argparse

    p = argparse.ArgumentParser(prog="qa")
    p.add_argument("command", choices=["status", "check"])
    p.add_argument("--log", default=str(ROOT / "log.csv"))
    p.add_argument("--features", default=str(ROOT / "features.csv"))
    p.add_argument("--findings", default=str(ROOT / "findings.csv"))
    p.add_argument("--today", help="override today's date (YYYY-MM-DD), for testing")
    args = p.parse_args(argv)
    if args.command == "check":
        return check(args)
    today = parse_date(args.today) if args.today else date.today()
    return status(args, today)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
