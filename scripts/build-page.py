#!/usr/bin/env python3
"""Build index.html (task T7) — a static one-page results site from log.csv.

Usage:
    python3 scripts/build-page.py [log path] [output path]   # default: log.csv index.html

Rules (section A.1 of the project plan):
- Only figures that can be counted directly from log.csv are shown. Nothing is
  estimated, sampled or filled in. An empty cell is reported as missing data.
- "(no findings)" (what scripts/scan.sh writes when nothing is found) counts as
  zero findings; an empty cell counts as missing.
- The classification, reliability and boundary tables need human judgement that
  log.csv does not hold, so they are shown as missing until that data exists.
- The output is a single file with no external requests: it opens offline.

The script refuses to build if scripts/check-log.py reports problems.
"""
import csv
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


def build(rows):
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
                f"Needs: {esc(needs)}. Filled in during consolidation (task T6, <code>results.md</code>).</div>")

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
{pending("log.csv records findings but not their category or who could have caught them.", "a human classification of each finding")}

<h2>3. Reliability of the AI review (Tier 3)</h2>
{pending("log.csv records Tier 3 findings but not whether each one is a true or false positive.", "a human true/false judgement for each Tier 3 finding")}

<h2>4. Where the full process applies</h2>
{pending("log.csv does not record the three boundary questions.", "per-feature answers to: touches real user data? public on the internet? kept in use for more than six months?")}

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
    out.write_text(build(rows), encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
