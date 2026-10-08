#!/usr/bin/env python3
"""Validate log.csv against the rules in sections 5.1 and A.1 of the project plan.

Usage:
    python3 scripts/check-log.py [path]                  # default: log.csv
    python3 scripts/check-log.py --filled <feature name> [path]

The second form exits 0 only when the feature already has a row in the log and
its "Manual check" column is filled in. scripts/scan.sh uses it to refuse to
scan before a human has recorded the result of the manual check.

Warnings (printed, but not counted as problems) flag rows that already have
findings while "Prompt rounds" or "Time" is still empty: those two values can
only be recorded while the feature is being built (section 5.1).

The script only reads the log; it never modifies it.
"""
import csv
import sys
import unicodedata
from pathlib import Path

COLUMNS = [
    "Feature",
    "Requirement",
    "Prompt rounds",
    "Time",
    "Manual check",
    "Automated scan findings",
    "AI review findings",
    "Bugs found later",
]
MANUAL_COLUMN = "Manual check"
AFTER_MANUAL_COLUMNS = ["Automated scan findings", "AI review findings", "Bugs found later"]
BUILD_COLUMNS = ["Prompt rounds", "Time"]
MANUAL_VALUES = {"Pass", "Fail"}


def normalize(s):
    # macOS and some editors store non-ASCII text (e.g. Vietnamese) as NFD; compare as NFC.
    return unicodedata.normalize("NFC", (s or "").strip())


def read(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f))
    if not rows:
        return None, []
    header = [normalize(c) for c in rows[0]]
    data = [[normalize(c) for c in r] for r in rows[1:]]
    return header, data


def validate(path):
    errors = []
    header, data = read(path)
    if header is None:
        return ["File is empty; header row is missing."]
    if header != COLUMNS:
        errors.append(
            "Header does not match the 8 columns in section 5.1.\n"
            f"    Expected: {','.join(COLUMNS)}\n"
            f"    Found:    {','.join(header)}"
        )
        return errors

    i_manual = COLUMNS.index(MANUAL_COLUMN)
    seen = {}
    for line_no, row in enumerate(data, start=2):
        if not any(row):
            errors.append(f"Line {line_no}: empty row, please remove it.")
            continue
        if len(row) != len(COLUMNS):
            errors.append(f"Line {line_no}: has {len(row)} cells, expected exactly {len(COLUMNS)}.")
            continue
        cells = dict(zip(COLUMNS, row))
        name = cells["Feature"]
        if not name:
            errors.append(f"Line {line_no}: feature name is missing.")
        elif name in seen:
            errors.append(f"Line {line_no}: duplicate feature name with line {seen[name]} ('{name}').")
        else:
            seen[name] = line_no

        manual = row[i_manual]
        if manual and manual not in MANUAL_VALUES:
            errors.append(f"Line {line_no}: column '{MANUAL_COLUMN}' only accepts 'Pass' or 'Fail', got '{manual}'.")
        if not manual:
            filled = [c for c in AFTER_MANUAL_COLUMNS if cells[c]]
            if filled:
                errors.append(
                    f"Line {line_no} ('{name}'): {', '.join(filled)} already has data "
                    f"but column '{MANUAL_COLUMN}' is empty. It must be filled in BEFORE scanning (section 5.1)."
                )
    return errors


def warnings(path):
    """Rows that already have findings but are missing values only knowable at build time."""
    header, data = read(path)
    if header != COLUMNS:
        return []
    result = []
    for line_no, row in enumerate(data, start=2):
        if len(row) != len(COLUMNS):
            continue
        cells = dict(zip(COLUMNS, row))
        empty = [c for c in BUILD_COLUMNS if not cells[c]]
        if empty and any(cells[c] for c in AFTER_MANUAL_COLUMNS):
            result.append(
                f"Line {line_no} ('{cells['Feature']}'): {', '.join(empty)} still empty. "
                "Fill in now; it cannot be recovered later (section 5.1)."
            )
    return result


def is_filled(path, name):
    header, data = read(path)
    if header != COLUMNS:
        return False
    i_manual = COLUMNS.index(MANUAL_COLUMN)
    name = normalize(name)
    return any(len(r) == len(COLUMNS) and r[0] == name and r[i_manual] in MANUAL_VALUES for r in data)


def main(argv):
    if len(argv) >= 2 and argv[0] == "--filled":
        path = argv[2] if len(argv) > 2 else "log.csv"
        return 0 if is_filled(path, argv[1]) else 1

    path = argv[0] if argv else "log.csv"
    if not Path(path).exists():
        print(f"{path} not found.", file=sys.stderr)
        return 2
    errors = validate(path)
    for w in warnings(path):
        print(f"  warning: {w}")
    if errors:
        print(f"{path}: {len(errors)} problem(s)")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"{path}: valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
