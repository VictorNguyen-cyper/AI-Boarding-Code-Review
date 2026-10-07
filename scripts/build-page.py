#!/usr/bin/env python3
"""Build index.html (task T7) — a static one-page results site from log.csv.

Usage:
    python3 scripts/build-page.py [log path] [output path]   # default: log.csv index.html

findings.csv and boundary.csv (the human classification, see classification.md)
are read from the same directory as the log when they exist.

Rules (section A.1 of the project plan):
- Only figures that can be counted directly from log.csv are shown. Nothing is
  estimated, sampled or filled in. An empty cell is reported as missing data.
- "(no findings)" (what scripts/scan.sh writes when nothing is found) counts as
  zero findings; an empty cell counts as missing.
- The classification, reliability and boundary tables need human judgement that
  log.csv does not hold. They are built only from findings.csv and boundary.csv,
  and shown as missing until those files have rows.
- The output is a single file with no external requests: it opens offline.

The script refuses to build if scripts/check-log.py or
scripts/check-classification.py reports problems.
"""
import html
import importlib.util
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NO_FINDINGS = "(no findings)"

spec = importlib.util.spec_from_file_location("check_log", ROOT / "scripts" / "check-log.py")
check_log = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check_log)
COLUMNS = check_log.COLUMNS

spec = importlib.util.spec_from_file_location("check_classification", ROOT / "scripts" / "check-classification.py")
check_classification = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check_classification)
SOURCES = check_classification.SOURCES
criteria = check_classification.criteria


def findings(cell):
    """Number of findings in a cell, or None when the cell is empty (missing)."""
    if not cell:
        return None
    if cell == NO_FINDINGS:
        return 0
    return len([f for f in cell.split(";") if f.strip()])


def esc(s):
    return html.escape(s or "")


def missing(text="missing"):
    return f'<span class="miss">{esc(text)}</span>'


def table(head, rows):
    t = "<table><thead><tr>" + "".join(f"<th>{esc(h)}</th>" for h in head) + "</tr></thead><tbody>"
    for r in rows:
        t += "<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>"
    return t + "</tbody></table>"


def count_row(label, rows, key):
    """One row of the comparison table: features with >=1 finding, with 0, and with the cell empty."""
    vals = [findings(r[key]) for r in rows]
    found = sum(1 for v in vals if v)
    zero = sum(1 for v in vals if v == 0)
    empty = sum(1 for v in vals if v is None)
    return [esc(label), str(found), str(zero), missing(str(empty)) if empty else "0"]


def yes_cell(probs, col):
    """Count of 'Yes' in a column; empty cells are shown separately as unknown."""
    yes = sum(1 for p in probs if p[col] == "Yes")
    unknown = sum(1 for p in probs if not p[col])
    return str(yes) + (f" {missing(f'+{unknown} ?')}" if unknown else "")


def bold(cells):
    return [f"<strong>{c}</strong>" for c in cells]


def classification_table(probs):
    """Real problems per criterion, and which source caught them."""
    real = [p for p in probs if p["Verdict"] == "Real"]
    if not real:
        return None
    keys = sorted({c for p in real for c in criteria(p["Criterion"])})
    if any(not criteria(p["Criterion"]) for p in real):
        keys.append("Not set")

    def row(label, subset):
        no_ai = sum(1 for p in subset if p["Tier 1"] != "Yes" and p["Tier 3"] != "Yes")
        return [esc(label), str(len(subset)), *(yes_cell(subset, s) for s in SOURCES), str(no_ai)]

    body = [row(k, [p for p in real if k in criteria(p["Criterion"]) or (k == "Not set" and not criteria(p["Criterion"]))])
            for k in keys]
    body.append(bold(row("Total (each problem once)", real)))
    return table(["Criterion", "Real problems", *SOURCES, "Caught by neither Tier 1 nor Tier 3"], body)


def reliability_table(probs):
    """Tier 3 findings split by the human verdict, per severity."""
    if not probs:
        return None

    def row(label, subset):
        t3 = [p for p in subset if p["Tier 3"] == "Yes"]
        return [esc(label), str(len(t3)),
                str(sum(1 for p in t3 if p["Verdict"] == "Real")),
                str(sum(1 for p in t3 if p["Verdict"] == "False positive")),
                str(sum(1 for p in t3 if not p["Verdict"])),
                str(sum(1 for p in subset if p["Verdict"] == "Real" and p["Tier 3"] == "No"))]

    body = []
    for sev in ["High", "Medium", "Low", ""]:
        subset = [p for p in probs if p["Severity"] == sev]
        if subset:
            body.append(row(sev or "Not set", subset))
    body.append(bold(row("Total", probs)))
    return table(["Severity", "Tier 3 findings", "Real", "False positive", "Not classified yet",
                  "Real problems Tier 3 missed"], body)


def boundary_table(bounds, probs, rows):
    """Features grouped by their answers to the three boundary questions."""
    if not bounds:
        return None
    answers = {b["Feature"]: tuple(b[q] or "?" for q in check_classification.BOUNDARY_QUESTIONS) for b in bounds}
    groups = {}
    for r in rows:
        groups.setdefault(answers.get(r["Feature"], ("?", "?", "?")), []).append(r["Feature"])
    body = []
    for combo, names in sorted(groups.items()):
        real = [p for p in probs if p["Feature"] in names and p["Verdict"] == "Real"]
        body.append([*(missing(a) if a == "?" else esc(a) for a in combo), str(len(names)), str(len(real)),
                     str(sum(1 for p in real if p["Severity"] == "High")),
                     str(sum(1 for p in real if p["Manual"] == "No"))])
    return table([*check_classification.BOUNDARY_QUESTIONS, "Features", "Real problems",
                  "High severity", "Not caught by the manual check"], body)


def build(rows, probs=(), bounds=()):
    n = len(rows)
    passed = [r for r in rows if r["Manual check"] == "Pass"]
    failed = [r for r in rows if r["Manual check"] == "Fail"]
    no_manual = n - len(passed) - len(failed)

    def gap(key):
        # Denominator is only the passed features whose cell is filled in; empty cells are missing, not zero.
        known = [findings(r[key]) for r in passed if findings(r[key]) is not None]
        return f"{sum(1 for v in known if v)}/{len(known)}" if known else "—"

    kpis = [
        (str(n), "Features logged"),
        (f"{len(passed)}/{n}" if n else "—", "Passed the manual check"),
        (gap("Automated scan findings"), "Passed manually, Tier 1 still found issues"),
        (gap("AI review findings"), "Passed manually, Tier 3 still found issues"),
        (gap("Bugs found later"), "Passed manually, broke within a week"),
    ]
    kpi_html = "".join(f'<div class="kpi"><b>{esc(v)}</b><span>{esc(l)}</span></div>' for v, l in kpis)

    comparison = table(
        ["Among features that passed the manual check", "With ≥1 finding", "With no findings", "Cell empty"],
        [
            count_row("Tier 1 — automated scan", passed, "Automated scan findings"),
            count_row("Tier 3 — AI review", passed, "AI review findings"),
            count_row("Bugs found after one week", passed, "Bugs found later"),
        ],
    ) if passed else ""

    log_rows = []
    for r in rows:
        cells = []
        for c in COLUMNS:
            v = r[c]
            if c == "Manual check" and v:
                cells.append(f'<span class="badge {v.lower()}">{esc(v)}</span>')
            elif c in ("Automated scan findings", "AI review findings", "Bugs found later") and v and v != NO_FINDINGS:
                items = [i.strip() for i in v.split(";") if i.strip()]
                cells.append("<ul>" + "".join(f"<li>{esc(i)}</li>" for i in items) + "</ul>")
            else:
                cells.append(esc(v) if v else missing("—"))
        log_rows.append(cells)

    empty_banner = (
        '<p class="note"><strong>No data yet.</strong> log.csv has no feature rows. '
        "Add rows as each feature is finished (section 5.1), then rebuild this page.</p>"
        if not n else ""
    )
    manual_note = (
        f'<p class="sub">{no_manual} feature(s) have no manual check recorded and are left out of the comparison.</p>'
        if no_manual else ""
    )

    def pending(what, needs):
        return (f'<div class="pending"><b>Missing data.</b> {esc(what)} '
                f"Needs: {esc(needs)}. See <code>classification.md</code>.</div>")

    unclassified = sum(1 for p in probs if not p["Verdict"])
    class_note = (f'<p class="sub">{unclassified} problem(s) in findings.csv have no verdict yet and are left out '
                  "of this table. “+n ?” = cells not filled in.</p>" if unclassified else "")
    classification = classification_table(probs)
    reliability = reliability_table(probs)
    boundary = boundary_table(bounds, probs, rows)

    def section(content, what, needs, note=""):
        return f'{note}<div class="wrap">{content}</div>' if content else pending(what, needs)

    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Acceptance study results</title><style>
:root{{--bg:#f7f7f5;--fg:#1d1d1b;--muted:#6b6b66;--card:#fff;--line:#e3e2dc;--ok:#1f7a4d;--bad:#b3261e;--warn:#8a5a00;--warnbg:#fff4d6}}
@media (prefers-color-scheme:dark){{:root{{--bg:#161615;--fg:#ecebe6;--muted:#a3a29b;--card:#1f1f1d;--line:#34332f;--ok:#5cc28c;--bad:#f0817a;--warn:#f2c46b;--warnbg:#2e2615}}}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--fg);font:15px/1.55 -apple-system,system-ui,sans-serif}}
main{{max-width:1100px;margin:0 auto;padding:32px 16px 64px}}h1{{font-size:26px;margin:0 0 4px}}h2{{font-size:18px;margin:36px 0 10px}}
.sub{{color:var(--muted);margin:0 0 20px}}.note{{background:var(--warnbg);color:var(--warn);border-radius:8px;padding:12px 14px;font-size:14px}}
.kpis{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin:20px 0}}
.kpi{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px}}.kpi b{{display:block;font-size:28px}}.kpi span{{color:var(--muted);font-size:13px}}
.wrap{{overflow-x:auto;background:var(--card);border:1px solid var(--line);border-radius:10px}}
table{{border-collapse:collapse;width:100%;font-size:14px}}th,td{{padding:9px 12px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}}
th{{font-weight:600;color:var(--muted);font-size:12px;text-transform:uppercase;letter-spacing:.03em}}tr:last-child td{{border-bottom:0}}
td ul{{margin:0;padding-left:18px}}code{{font-size:12.5px}}.miss{{color:var(--muted);font-style:italic}}
.pending{{background:var(--card);border:1px dashed var(--line);border-radius:10px;padding:14px;color:var(--muted);font-size:14px}}
.badge{{font-size:12px;padding:2px 8px;border-radius:99px;white-space:nowrap;font-weight:600}}
.pass{{color:var(--ok);border:1px solid var(--ok)}}.fail{{color:var(--bad);border:1px solid var(--bad)}}
</style></head><body><main>
<h1>Acceptance of AI-generated software — results</h1>
<p class="sub">Built from <code>log.csv</code> on {date.today().isoformat()} · {n} feature(s) · case study with figures, not inferential statistics</p>
{empty_banner}
<div class="kpis">{kpi_html}</div>

<h2>1. Comparison — passed the manual check, yet issues were found</h2>
{manual_note}{f'<div class="wrap">{comparison}</div>' if passed else pending("No feature has passed the manual check yet.", "rows in log.csv with Manual check = Pass")}

<h2>2. Classification — what tools catch vs. what only people catch</h2>
{section(classification, "No problem in findings.csv has the verdict Real yet.", "rows in findings.csv with a verdict", class_note)}

<h2>3. Reliability of the AI review (Tier 3)</h2>
{section(reliability, "findings.csv has no rows yet.", "a human verdict (Real / False positive) for each Tier 3 finding")}

<h2>4. Where the full process applies</h2>
{section(boundary, "boundary.csv has no rows yet.", "per-feature answers to: touches real user data? public on the internet? kept in use for more than six months?")}

<h2>Development log</h2>
{f'<div class="wrap">{table(COLUMNS, log_rows)}</div>' if n else pending("log.csv is empty.", "one row per finished feature")}

<p class="sub" style="margin-top:28px">Rebuild with <code>python3 scripts/build-page.py</code>. This page makes no network requests.</p>
</main></body></html>
"""


def main(argv):
    log = Path(argv[0]) if argv else ROOT / "log.csv"
    out = Path(argv[1]) if len(argv) > 1 else ROOT / "index.html"
    if not log.exists():
        print(f"{log} not found.", file=sys.stderr)
        return 2
    errors = check_log.validate(log)
    if errors:
        print(f"{log}: fix these first (python3 scripts/check-log.py):", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1
    _, data = check_log.read(log)
    rows = [dict(zip(COLUMNS, r)) for r in data]
    features = {r["Feature"] for r in rows}

    probs, bounds = [], []
    f_path, b_path = log.parent / "findings.csv", log.parent / "boundary.csv"
    if f_path.exists():
        probs, errors = check_classification.validate_findings(f_path, features)
    if b_path.exists():
        bounds, b_errors = check_classification.validate_boundary(b_path, features)
        errors += b_errors
    if errors:
        print("fix these first (python3 scripts/check-classification.py):", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1
    out.write_text(build(rows, probs, bounds), encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
