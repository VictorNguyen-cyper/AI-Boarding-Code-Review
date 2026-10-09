# Demo — a trial run of the 3-tier acceptance process

> **Not research data.** This directory only illustrates how the tools in this repository work together. Do not put any figures from here into `log.csv`, the results report or any other report (rule A.1).

## Demo limitations

- Bugs were **deliberately planted** in the simulated app, so the Tier 3 detection rate is inflated.
- The code and the review were produced by **the same model**, contrary to section 5.3 of the project plan. The demo's Tier 3 review was done by hand in the finding format of `checklist.md`, **not** through `review.sh` and Gemini as in the real process (see `ai-review.md`).
- The *Manual check* column in `log-DEMO.csv` is **assumed**, not filled in by a person trying the feature.
- The two keys in `app/app.py` (lines 9 and 10) are **fake keys**. The gitleaks finding on line 10 is listed in `.gitleaksignore` in the repository root so the hook does not block commits; if you edit `app.py` and the line moves, update that file.

## Contents

| File | Tier | Contents |
| --- | --- | --- |
| `app/` | — | Flask app simulating a "View orders" feature |
| `log-DEMO.csv` | — | One log row with exactly the 8 columns |
| `test-case-view-orders-DEMO.md` | 2 | 14 cases in the 6 groups, with real run results |
| `review-view-orders-DEMO.md` | 3 | Review against the 12 criteria, in the `checklist.md` format (not via Gemini) |
| `requirements-view-orders-DEMO.md` | 3 | Sample requirements file, input for `review.sh` |
| `review-view-orders-DEMO-gemini.md` | 3 | Skeleton created by `review.sh --lang vi`, waiting for Gemini's answer |
| `comparison-DEMO.md` | — | Which problems each tier caught |
| `demo.html` | — | Summary page, open directly in a browser |
| `run_tier2.py`, `build_page.py`, `tier2.json` | — | Tier 2 runner, page builder, raw results |

## Re-running

From the repository root:

```bash
python3 -m venv demo/.venv && demo/.venv/bin/pip install -r demo/app/requirements.txt

# Tier 1 — reports go to scan-results/ (not committed).
# Note: because .gitleaksignore lists the key at app.py:10, a re-run will NOT show
# that gitleaks finding (Tier 1 shows 1/11 instead of the 2/11 in the comparison table).
# To reproduce it exactly, temporarily rename .gitleaksignore before running, then rename it back.
LOG=demo/log-DEMO.csv scripts/scan.sh "View orders" demo/app

# Tier 2
demo/.venv/bin/python demo/run_tier2.py

# Rebuild the summary page
python3 demo/build_page.py
```
