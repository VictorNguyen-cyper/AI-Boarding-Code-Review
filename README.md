# 3-tier acceptance process for AI-generated code

How to accept software when most of its code was written by AI and nobody reads all of it.
The full rationale is in `ke-hoach-du-an-thuc-tap.docx` (project plan, Vietnamese).

**Start here:** run `./qa status`. It lists every feature, which steps are done, and the next step to take.

---

## Three rules you must never break

1. **Fill in *Manual check* (`Pass` / `Fail`) before running any tier.** Filled in afterwards, the control column is worthless. `./qa scan` and `./qa review` refuse to run until it is filled in.
2. **Give the reviewing AI the requirements, never the original prompt.** Otherwise it just confirms itself.
3. **Tools and AI never decide whether a finding is true or false.** Only a human fills *Verdict* in `findings.csv`.

---

## One-time setup

```bash
brew install gitleaks semgrep trivy          # Tier 1 scanners (automated-scanning.md §0)
git config core.hooksPath .githooks          # blocks leaked secrets and invalid data files
```

Then fill in section 2 of `ai-review.md` (reviewing model, date, mentor approval to send code).

---

## Steps for each feature

| # | Step | What to do | Writes to |
| --- | --- | --- | --- |
| 1 | Log it | Add a row to `log.csv`: *Feature*, *Requirement*, *Prompt rounds*, *Time* | `log.csv` |
| 2 | Manual check | Try the feature by hand, then fill *Manual check* — **before step 3** | `log.csv` |
| 3 | Tier 1 — scan | `./qa scan "<feature>" <code dir>` and paste `summary.txt` | `log.csv`, `findings.csv` |
| 4 | Tier 2 — test cases | Copy `templates/test-case-template.md` to `test-case-<feature>.md`, run every case | `test-case-<feature>.md`, `findings.csv` |
| 5 | Tier 3 — AI review | `./qa review --lang vi "<feature>" requirements-<feature>.md <code dir>`, then follow `ai-review.md` §5 | `review-<feature>.md`, `log.csv`, `findings.csv` |
| 6 | Classify | For each row in `findings.csv`, fill *Verdict* and *Classified on* | `findings.csv` |
| 7 | Ship | When the feature goes into real use, fill *Shipped on* | `features.csv` |
| 8 | One week later | `./qa status` shows **DUE**; fill *Bugs found later* in `log.csv` (`None` if nothing broke) and *Follow-up checked on* | `log.csv`, `features.csv` |

Run `./qa check` any time to validate the three data files (the pre-commit hook runs it too).

---

## Data files

**`log.csv`**: one row per feature, with exactly the 8 columns of section 5.1 of the plan. Do not add columns.

**`findings.csv`**: one row per finding from any tier. This is what the reliability table (true- / false-positive rate) and the classification table are built from.

| Column | Values |
| --- | --- |
| Feature | Same name as in `log.csv` |
| Tier | `1`, `2` or `3` |
| Source | Tool (`gitleaks`, `trivy`, `semgrep`), test case ID (`TC-21`) or reviewing model |
| Criterion | `C01`–`C12` from `checklist.md`, or empty if none matches |
| Location | `file:line`, endpoint or package. **Never** a secret value |
| Severity | `Critical`, `High`, `Medium`, `Low`, or empty |
| Verdict | Empty until a human classifies it: `True positive`, `False positive` or `Unsure` |
| Classified on | Date `YYYY-MM-DD`, required once *Verdict* is filled |
| Note | Free text, e.g. why it is a false positive |

When a problem is found by several tiers, add one row per tier. That overlap is what the comparison table measures.

**`features.csv`**: shipping dates, so the one-week follow-up is not forgotten.

| Column | Values |
| --- | --- |
| Feature | Same name as in `log.csv` |
| Shipped on | Date the feature went into real use |
| Follow-up checked on | Date you filled *Bugs found later*, at least 7 days after shipping |

---

## Where things are

| Plan (Vietnamese) | Task | This repository |
| --- | --- | --- |
| `nhat-ky.csv` | T1 | `log.csv` (+ `findings.csv`, `features.csv`) |
| `checklist.md` | T2 | `checklist.md` |
| `quet-tu-dong.md` | T3 | `automated-scanning.md`, `scripts/scan.sh` |
| `test-case-<tên>.md` | T4 | `templates/test-case-template.md` → `test-case-<feature>.md` |
| `ra-soat-<tên>.md` | T5 | `ai-review.md`, `review.sh` → `review-<feature>.md` |
| `ket-qua.md` | T6 | *not built yet* |
| `index.html` | T7 | *not built yet* (see `demo/demo.html` for the shape) |
| `bao-cao-khung.md` | T8 | *not built yet* |

`demo/` is a trial run on a simulated app with planted bugs. **It is not research data.**

Not committed: `scan-results/` and `review-input/`, because they may contain source code or internal paths.
