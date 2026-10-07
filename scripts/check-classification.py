#!/usr/bin/env python3
"""Validate findings.csv and boundary.csv — the human classification used by task T6.

Usage:
    python3 scripts/check-classification.py [findings.csv] [boundary.csv] [log.csv]

Both files are filled in by a human (rule A.1); see classification.md. Empty cells
are allowed and mean "not classified yet". The script only reads; it never
modifies any file.
"""
import importlib.util
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

spec = importlib.util.spec_from_file_location("check_log", ROOT / "scripts" / "check-log.py")
check_log = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check_log)

SOURCES = ["Manual", "Tier 1", "Tier 2", "Tier 3", "Found later"]
FINDING_COLUMNS = ["Feature", "Problem", "Criterion", "Severity", "Verdict", *SOURCES, "Classified on"]
BOUNDARY_QUESTIONS = ["Real user data", "Public on the internet", "In use over 6 months"]
BOUNDARY_COLUMNS = ["Feature", *BOUNDARY_QUESTIONS]

VERDICTS = {"Real", "False positive"}
SEVERITIES = {"High", "Medium", "Low"}
YES_NO = {"Yes", "No"}
CRITERION = re.compile(r"^(C(0[1-9]|1[0-2])|Other)$")
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def criteria(cell):
    return [c.strip() for c in cell.split(",") if c.strip()]


def load(path, columns):
    """Return (rows as dicts, errors). A missing file is an error."""
    if not Path(path).exists():
        return [], [f"{path} not found."]
    header, data = check_log.read(path)
    if header != columns:
        return [], [
            f"{path}: header does not match.\n"
            f"    Expected: {','.join(columns)}\n"
            f"    Found:    {','.join(header or [])}"
        ]
    rows, errors = [], []
    for line_no, row in enumerate(data, start=2):
        if not any(row):
            errors.append(f"{path} line {line_no}: empty row, please remove it.")
        elif len(row) != len(columns):
            errors.append(f"{path} line {line_no}: has {len(row)} cells, expected exactly {len(columns)}.")
        else:
            rows.append((line_no, dict(zip(columns, row))))
    return rows, errors


def check_value(errors, where, column, value, allowed):
    if value and value not in allowed:
        errors.append(f"{where}: column '{column}' only accepts {' / '.join(sorted(allowed))}, got '{value}'.")


def validate_findings(path, features):
    rows, errors = load(path, FINDING_COLUMNS)
    seen = {}
    for line_no, r in rows:
        where = f"{path} line {line_no}"
        if not r["Feature"]:
            errors.append(f"{where}: feature name is missing.")
        elif r["Feature"] not in features:
            errors.append(f"{where}: feature '{r['Feature']}' has no row in log.csv.")
        if not r["Problem"]:
            errors.append(f"{where}: problem description is missing.")
        key = (r["Feature"], r["Problem"])
        if key in seen:
            errors.append(f"{where}: duplicate of line {seen[key]} (same feature and problem).")
        seen.setdefault(key, line_no)
        for c in criteria(r["Criterion"]):
            if not CRITERION.match(c):
                errors.append(f"{where}: criterion '{c}' must be C01–C12 or Other.")
        check_value(errors, where, "Severity", r["Severity"], SEVERITIES)
        check_value(errors, where, "Verdict", r["Verdict"], VERDICTS)
        for s in SOURCES:
            check_value(errors, where, s, r[s], YES_NO)
        if not any(r[s] == "Yes" for s in SOURCES):
            errors.append(f"{where}: no source column is 'Yes' — record at least who found it.")
        if r["Classified on"] and not DATE.match(r["Classified on"]):
            errors.append(f"{where}: 'Classified on' must be YYYY-MM-DD.")
    return [r for _, r in rows], errors


def validate_boundary(path, features):
    rows, errors = load(path, BOUNDARY_COLUMNS)
    seen = {}
    for line_no, r in rows:
        where = f"{path} line {line_no}"
        name = r["Feature"]
        if not name:
            errors.append(f"{where}: feature name is missing.")
        elif name not in features:
            errors.append(f"{where}: feature '{name}' has no row in log.csv.")
        elif name in seen:
            errors.append(f"{where}: duplicate feature name with line {seen[name]}.")
        seen.setdefault(name, line_no)
        for q in BOUNDARY_QUESTIONS:
            check_value(errors, where, q, r[q], YES_NO)
    return [r for _, r in rows], errors


def features_in(log):
    header, data = check_log.read(log)
    return {r[0] for r in data if r and r[0]} if header else set()


def main(argv):
    findings = argv[0] if len(argv) > 0 else ROOT / "findings.csv"
    boundary = argv[1] if len(argv) > 1 else ROOT / "boundary.csv"
    log = argv[2] if len(argv) > 2 else ROOT / "log.csv"
    features = features_in(log)
    errors = validate_findings(findings, features)[1] + validate_boundary(boundary, features)[1]
    if errors:
        print(f"{len(errors)} problem(s)")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"{findings}, {boundary}: valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
