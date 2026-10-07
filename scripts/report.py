#!/usr/bin/env python3
"""Task T6: build the four result tables of plan section 8 from the data files.

Usage (normally through ./qa report):
    python3 scripts/report.py [--log P] [--features P] [--findings P] [--out P] [--demo]

Reads log.csv, findings.csv and features.csv; writes results.md (default).
Rules from plan A.1 / T6:
- Only figures that exist in the files are used. A cell that cannot be computed says "missing".
- Unclassified findings are never counted as true or false; they are reported separately.
- Figures are counts for a case study, not statistical inference (plan section 8).
"""
import argparse
import re
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

from qa import (
    BOUNDARY_COLUMNS,
    FEATURE_COLUMNS,
    FINDING_COLUMNS,
    ROOT,
    log_features,
    read_rows,
    validate_features,
    validate_findings,
)

TIER_ORDER = ["1", "2", "3", "Later"]
TIER_NAMES = {
    "1": "Tier 1 — automated scan",
    "2": "Tier 2 — behavior testing",
    "3": "Tier 3 — AI review",
    "Later": "Found after shipping",
}
SERIOUS = {"Critical", "High"}
MISSING = "missing"


def criterion_titles():
    titles = {}
    for line in (ROOT / "checklist.md").read_text(encoding="utf-8").splitlines():
        m = re.match(r"^### (C\d{2})\. (.+)$", line)
        if m:
            titles[m.group(1)] = m.group(2)
    return titles


def table(header, rows):
    out = ["| " + " | ".join(header) + " |", "| " + " | ".join("---" for _ in header) + " |"]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


def pct(n, d):
    return f"{n}/{d} ({round(100 * n / d)}%)" if d else MISSING


def had_later_bug(log_row):
    v = log_row["Bugs found later"].strip()
    return bool(v) and v.lower() != "none"


def build(log, ship, findings, demo, sources):
    titles = criterion_titles()
    names = [r["Feature"] for r in log]
    by_feature = defaultdict(list)
    for f in findings:
        by_feature[f["Feature"]].append(f)
    true = [f for f in findings if f["Verdict"] == "True positive"]
    unclassified = [f for f in findings if not f["Verdict"]]

    lines = [
        "# Results — four tables (task T6)",
        "",
    ]
    if demo:
        lines += ["> **DEMO — not research data.** Built from the simulated app in `demo/`. Do not quote these figures.", ""]
    lines += [
        f"Generated on {date.today().isoformat()} by `./qa report` from " + ", ".join(f"`{s}`" for s in sources) + ".",
        "Do not edit by hand: fix the data files and run the command again.",
        "",
        "Figures are counts from a small set of features: read them as a case study, not as statistics (plan section 8).",
        "",
        "## Data completeness",
        "",
    ]

    manual = sum(1 for r in log if r["Manual check"])
    shipped = sum(1 for n in names if ship.get(n, {}).get("Shipped on"))
    followed = sum(1 for r in log if r["Bugs found later"] or ship.get(r["Feature"], {}).get("Follow-up checked on"))
    boundary = sum(1 for n in names if all(ship.get(n, {}).get(c) for c in BOUNDARY_COLUMNS))
    itemized = sum(
        1
        for r in log
        if by_feature[r["Feature"]]
        or not any(r[c] and r[c] != "(no findings)" for c in ("Automated scan findings", "AI review findings"))
    )
    lines += [
        table(
            ["Item", "Value"],
            [
                ["Features logged (plan target 15–25)", len(log)],
                ["Manual check filled", f"{manual}/{len(log)}"],
                ["Features whose log findings are itemized in findings.csv", f"{itemized}/{len(log)}"],
                ["Findings in findings.csv", len(findings)],
                ["Findings not yet classified by a human", len(unclassified)],
                ["Features shipped", f"{shipped}/{len(log)}"],
                ["One-week follow-up done", f"{followed}/{len(log)}"],
                ["Boundary questions answered", f"{boundary}/{len(log)}"],
            ],
        ),
        "",
    ]
    if unclassified:
        lines += [
            f"**{len(unclassified)} finding(s) are not classified yet.** They are left out of every true / false figure below.",
            "",
        ]

    # Table 1 — manual check vs. what the tiers found.
    lines += [
        "## Table 1 — Manual check vs. what the tiers found",
        "",
        "True-positive findings per tier for each feature. *Unclassified* findings are not counted as true.",
        "",
    ]
    rows = []
    for r in log:
        mine = by_feature[r["Feature"]]
        tp = Counter(f["Tier"] for f in mine if f["Verdict"] == "True positive")
        rows.append(
            [r["Feature"], r["Manual check"] or MISSING]
            + [tp[t] for t in TIER_ORDER]
            + [sum(1 for f in mine if not f["Verdict"])]
        )
    lines += [table(["Feature", "Manual check"] + [TIER_NAMES[t] for t in TIER_ORDER] + ["Unclassified"], rows), ""]

    passed = [r["Feature"] for r in log if r["Manual check"] == "Pass"]
    missed = [n for n in passed if any(f["Verdict"] == "True positive" for f in by_feature[n])]
    missed_serious = [
        n for n in missed if any(f["Verdict"] == "True positive" and f["Severity"] in SERIOUS for f in by_feature[n])
    ]
    pending = [n for n in passed if n not in missed and any(not f["Verdict"] for f in by_feature[n])]
    if passed:
        lines.append(
            f"Of {len(passed)} feature(s) rated **Pass** by eye, {len(missed)} still had at least one true-positive "
            f"finding, {len(missed_serious)} of them with High or Critical severity."
        )
        if pending:
            lines.append(f"Not yet decidable (findings still unclassified): {', '.join(pending)}.")
    else:
        lines.append(f"Summary: {MISSING} — no feature has *Manual check* = Pass yet.")
    lines.append("")

    # Table 2 — which tier catches which kind of problem.
    lines += [
        "## Table 2 — Which tier catches which kind of problem",
        "",
        "True-positive findings per checklist criterion. Several tiers can report the same problem, so these are",
        "counts of findings, not of distinct problems.",
        "",
    ]
    by_crit = defaultdict(Counter)
    for f in true:
        by_crit[f["Criterion"] or "—"][f["Tier"]] += 1
    rows = []
    for code in list(titles) + ["—"]:
        c = by_crit.get(code)
        if not c:
            continue
        if c["1"]:
            caught = "Automated tools"
        elif c["2"] or c["3"]:
            caught = "Needs a human or AI review"
        else:
            caught = "Missed by all tiers"
        label = f"{code} {titles[code]}" if code in titles else "No checklist criterion"
        rows.append([label] + [c[t] for t in TIER_ORDER] + [caught])
    if rows:
        lines += [table(["Criterion"] + [TIER_NAMES[t] for t in TIER_ORDER] + ["Caught by"], rows), ""]
        lines += [
            "*Caught by* is derived mechanically: \"Automated tools\" when Tier 1 has any true positive; otherwise",
            "\"Needs a human or AI review\" when Tier 2 or 3 does; otherwise \"Missed by all tiers\".",
            "",
        ]
    else:
        lines += [f"{MISSING} — no classified true-positive findings yet.", ""]

    # Table 3 — reliability.
    lines += [
        "## Table 3 — Reliability of each tier",
        "",
        "Rates use only classified findings (True + False). *Unsure* and *Unclassified* are shown but left out of the rates.",
        "",
    ]
    groups = defaultdict(Counter)
    for f in findings:
        if f["Tier"] == "Later":
            continue
        # Tier 3 is split by reviewing model, so a mid-project model change stays visible.
        key = (f["Tier"], f["Source"] if f["Tier"] == "3" else "")
        groups[key][f["Verdict"] or "Unclassified"] += 1
    rows = []
    for (tier, source), c in sorted(groups.items()):
        decided = c["True positive"] + c["False positive"]
        rows.append(
            [
                TIER_NAMES[tier] + (f" ({source})" if source else ""),
                sum(c.values()),
                c["True positive"],
                c["False positive"],
                c["Unsure"],
                c["Unclassified"],
                pct(c["True positive"], decided),
                pct(c["False positive"], decided),
            ]
        )
    if rows:
        lines += [
            table(
                ["Tier", "Findings", "True", "False", "Unsure", "Unclassified", "True-positive rate", "False-alarm rate"],
                rows,
            ),
            "",
        ]
    else:
        lines += [f"{MISSING} — no findings recorded yet.", ""]

    # Table 4 — boundary of application.
    lines += [
        "## Table 4 — Where the full process is needed",
        "",
        "Features grouped by the three boundary questions (plan section 8): touches real user data? public on the",
        "internet? kept running over six months?",
        "",
    ]
    profiles = defaultdict(list)
    for n in names:
        answers = [ship.get(n, {}).get(c, "") for c in BOUNDARY_COLUMNS]
        profiles[tuple(answers) if all(answers) else None].append(n)
    rows = []
    log_by_name = {r["Feature"]: r for r in log}
    for key in sorted((k for k in profiles if k), reverse=True) + ([None] if None in profiles else []):
        group = profiles[key]
        tp = [f for n in group for f in by_feature[n] if f["Verdict"] == "True positive"]
        rows.append(
            (list(key) if key else [MISSING] * 3)
            + [
                len(group),
                len(tp),
                sum(1 for f in tp if f["Severity"] in SERIOUS),
                f"{sum(1 for n in group if had_later_bug(log_by_name[n]))}/{len(group)}",
            ]
        )
    if rows:
        lines += [
            table(
                BOUNDARY_COLUMNS + ["Features", "True positives", "High / Critical", "Features with bugs found later"],
                rows,
            ),
            "",
        ]
    else:
        lines += [f"{MISSING} — no features logged yet.", ""]
    if None in profiles:
        lines += [f"Boundary answers {MISSING} for: {', '.join(profiles[None])}.", ""]

    return "\n".join(lines)


def main(argv):
    p = argparse.ArgumentParser(prog="qa report")
    p.add_argument("--log", default=str(ROOT / "log.csv"))
    p.add_argument("--features", default=str(ROOT / "features.csv"))
    p.add_argument("--findings", default=str(ROOT / "findings.csv"))
    p.add_argument("--out", default=str(ROOT / "results.md"))
    p.add_argument("--demo", action="store_true", help="mark the output as demo data")
    args = p.parse_args(argv)

    log = log_features(args.log)
    if log is None:
        print(f"{args.log} is missing or invalid; run ./qa check.", file=sys.stderr)
        return 1
    known = {r["Feature"] for r in log}
    errors = validate_features(args.features, known) + validate_findings(args.findings, known)
    if errors:
        print("Data files are not valid; fix them first:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    _, ship_rows = read_rows(args.features)
    ship = {r[0]: dict(zip(FEATURE_COLUMNS, r)) for r in ship_rows}
    _, finding_rows = read_rows(args.findings)
    findings = [dict(zip(FINDING_COLUMNS, r)) for r in finding_rows]

    sources = [Path(x).name for x in (args.log, args.findings, args.features)]
    Path(args.out).write_text(build(log, ship, findings, args.demo, sources) + "\n", encoding="utf-8")
    print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
