# Classifying findings (input for task T6)

`log.csv` records **what each tier reported**. It does not record whether a finding was real, which criterion it belongs to, or which tiers caught the same problem. Three of the four result tables (section 8 of the project plan) need exactly that, so it is recorded by a **human** in two separate files. A third file, `effort.csv`, records what each step cost:

| File | One row per | Feeds |
| --- | --- | --- |
| `findings.csv` | distinct problem in a feature | Classification table, Reliability table |
| `boundary.csv` | feature | Boundary table |
| `effort.csv` | feature and step | The short checklist (objective 4): what each tier costs against what it catches |

`log.csv` keeps its 8 columns unchanged (section 5.1).

**Rules (A.1):**

- Only a person fills in these files. An AI may suggest a criterion code, but the *Verdict* is always a human decision.
- Leave a cell empty when you do not know yet. Empty means "not classified", never "No".
- No real source code, customer names or internal module names in *Problem*. Describe the problem in plain words.

---

## `findings.csv`

Fill it in **after** the feature's row in `log.csv` is complete (all tiers run). Add one row per **distinct problem**: if Tier 1 and Tier 3 report the same hard-coded key, that is one row with *Tier 1* = Yes and *Tier 3* = Yes.

| Column | Values | Meaning |
| --- | --- | --- |
| Feature | exactly as in `log.csv` | Which feature |
| Problem | short plain text | What is wrong, 1 sentence |
| Criterion | `C01`–`C12` or `Other`; several separated by `, ` | Matching criterion in `checklist.md` |
| Severity | High / Medium / Low | Scale in `checklist.md` |
| Verdict | Real / False positive | **Human decision**: is it really a problem? |
| Manual | Yes / No | Was it noticed during the manual check? |
| Tier 1 | Yes / No | Reported by gitleaks / trivy / semgrep? |
| Tier 2 | Yes / No | Revealed by a test case? |
| Tier 3 | Yes / No | Reported by the AI review? |
| Found later | Yes / No | Did it surface during the week of real use? |
| Classified on | YYYY-MM-DD | Date of the verdict |

**How to decide the Verdict:**

- **Real**: you can show the problem: reproduce it, point to the line, or a bug surfaced later.
- **False positive**: a tier reported it, but after checking, it is not a problem (e.g. a test key, a check that exists in another layer).
- Not sure yet: leave it empty and come back. Do not guess.

**Problems missed by a tier still get a row.** For example, a bug found after one week that no tier reported gets *Found later* = Yes and *Tier 1/2/3* = No. These rows are what show each tier's blind spots.

## `boundary.csv`

One row per feature. Answer the three questions from section 8 of the plan with Yes / No:

| Column | Question |
| --- | --- |
| Real user data | Does the feature touch real user data? |
| Public on the internet | Is it reachable from the public internet? |
| In use over 6 months | Will it stay in use for more than six months? |

## `effort.csv`

Record the minutes **as soon as each step ends**, the same way as the *Time* column of `log.csv`: estimating them later is guesswork. One row per feature and step; if a step was done in several sittings, add the minutes up in one row.

| Column | Values | Meaning |
| --- | --- | --- |
| Feature | exactly as in `log.csv` | Which feature |
| Step | `Manual check` / `Tier 1` / `Tier 2` / `Tier 3` / `Classification` | Which step the time was spent on |
| Minutes | a number, e.g. `25` or `2.5` | Hands-on time, including setup and recording results; for Tier 3 include the wait for the answer |

A step that was skipped gets no row. Do not write `0` for it: `0` means the step was done and took no time.

## Checking and using the files

```bash
python3 scripts/check-classification.py   # validate findings.csv, boundary.csv and effort.csv against log.csv
python3 scripts/build-page.py             # rebuild index.html with the three tables
```

`build-page.py` refuses to build while any of these files has problems. The tables count only what is filled in: problems without a verdict are left out and counted separately, and empty cells are shown as `+n ?`.
