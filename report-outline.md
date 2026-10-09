# Report outline (task T8)

> **This is a skeleton, not the report.** Every section lists what to write and where the material comes from. It contains no results: findings, figures and conclusions are written by the student from `log.csv` and the result tables in `index.html` (tasks T6–T7, built by `scripts/build-page.py`) once the data exists (rule A.1).

**Target length:** 8–12 pages of PDF, readable on its own without any attachment (section 7 of the project plan). The page budget per section is a guide; adjust it, but keep section 6 (Results) the largest.

**Rules while writing:**

- Every figure must come from `log.csv`, `effort.csv` or the tables in `index.html`. If a cell is missing, say it is missing; do not estimate.
- Present results as a **case study with figures**, not inferential statistics (section 8). Write "in N features, …", never "X% of AI-generated code …".
- No real source code, customer names, internal module names or other identifying information (rule A.1). Use the anonymised log.
- Do not reuse anything from `demo/` — it is illustration, not research data.

---

## Cover page (not counted)

- Title: *(fill in — may reuse the plan title: "Verifying software quality when most of the code is AI-generated")*
- Student name, year, major: *(fill in)*
- Host organisation, mentor: *(fill in — or anonymise if publication scope was not approved)*
- Internship period: *(fill in actual dates)*
- Recipient: Rector / Faculty board

## Abstract (≈ ½ page)

*To fill in last.* 150–200 words: the problem, the three-tier process, how many features were logged, the one or two most important findings (with figures from section 6), and the proposed short checklist. Must make sense to a reader who reads nothing else.

## 1. Context and problem (≈ 1 page)

*Source: section 2 of the project plan.*

- How code is produced and accepted at the host organisation (AI-generated, accepted by "run it and look").
- The class of problems manual checking cannot see. List the five from the plan; for each, add **one sentence** on whether it actually occurred in this study (point to section 6, do not repeat figures here).
- The core question: how to accept software when nobody reads all of the code any more. Why this belongs to Information Management (process, quality control, risk).

## 2. Objectives (≈ ½ page)

*Source: section 3 of the project plan.*

- General objective.
- The four specific objectives. Keep the wording; section 8 of this report must answer each one explicitly.

## 3. Scope (≈ ½ page)

*Source: section 4 of the project plan.*

- In scope / out of scope.
- State that the study is **prospective**: data was recorded during development, with no historical data.
- State the publication scope that was actually approved, and how the data was anonymised. *(fill in)*

## 4. Method (≈ 2 pages)

*Sources: section 5 of the project plan, `checklist.md`, `automated-scanning.md`, `ai-review.md`, `templates/test-case-template.md`.*

### 4.1 Development log

- The eight columns of `log.csv` and what each records.
- The rule that *Manual check* is filled in **before** scanning, and how it was enforced (`scripts/check-log.py`, `scripts/scan.sh` refuse otherwise).
- Report any deviation honestly: rows filled in late, features dropped, cells left empty. *(fill in)*

### 4.2 The three tiers

- **Tier 1 — automated scan:** tools used (gitleaks, trivy, semgrep) and their versions. *(fill in from `automated-scanning.md` section 6)*
- **Tier 2 — systematic behaviour testing:** how test cases were generated from requirements, the six case groups.
- **Tier 3 — scope-limited AI review:** the 12 criteria (summarise the five groups A–E, do not paste the full checklist), the reviewing model and why it differs from the generating model. *(fill in model names and versions)*

### 4.3 Objectivity measures

- Different model for review than for generation.
- Review based on the requirements document, never on the original prompt.
- Bugs found after one week of real use as the arbiter.
- Cross-check between two models: whether it was done, and on how many features. *(fill in)*
- The 30-minute validation session with a senior engineer: whether it happened, and what changed because of it. *(fill in; if it did not happen, say which fallback from section 9 of the plan was used)*

### 4.4 How findings were classified

- Who classified each finding (true/false positive, category, which tier could catch it), when, and with what rule. *(fill in — this must be a human, rule A.1)*
- The classification is recorded in `findings.csv` and `boundary.csv`; describe the rules in `classification.md` briefly, and any case where the verdict was hard to decide.

## 5. Timeline as executed (≈ ½ page)

*Source: section 6 of the project plan + your own notes.*

- Planned vs. actual per week. A small table is enough.
- What was cut when time ran short (the plan says: cut features, never cut logging or validation). *(fill in)*

## 6. Results (≈ 3–4 pages)

*Sources: `log.csv`, `findings.csv`, `boundary.csv`, `effort.csv`. `scripts/build-page.py` builds the four tables directly from these files into `index.html` (tasks T6–T7); rebuild it before copying any table.*

Open with one sentence on the sample: how many features, over how many weeks. *(fill in)*

### 6.1 Comparison table — passed by eye, yet issues found

- Insert the table from `index.html`.
- 2–4 sentences of reading: what the gap is, in "N of M features" form.
- Name the cells that are missing data and why.

### 6.2 Classification table — what tools catch vs. what only people catch

- Insert the table from `index.html`.
- One short example per category, anonymised, in plain words (no code).

### 6.3 Reliability table — Tier 3 true and false positives

- Insert the table from `index.html`.
- Which criteria produced the most false positives, and a likely reason.
- If two models were cross-checked: where they disagreed and what those disagreements turned out to be.

### 6.4 Boundary table — when the full process is needed

- Insert the table from `index.html`, built on the three questions: touches real user data? public on the internet? kept in use for more than six months?
- Which combinations justify the full three tiers and which can rely on manual checking.

### 6.5 Bugs found after one week

- How many features had a bug after one week of real use, and whether any tier had flagged it beforehand.

## 7. Discussion and limitations (≈ 1 page)

- What the results suggest, kept within the case-study framing.
- Limitations — at minimum address: sample size; one person built, checked and classified; the period of real use was short; any deviation recorded in 4.1 or 4.3. *(fill in)*
- What would change with a larger sample or a longer observation period.

## 8. Conclusions and recommendations (≈ 1 page)

- Answer each of the four specific objectives from section 2, one short paragraph each, pointing to the table that supports it.
- **The short checklist** for future interns: the final list, or a pointer to the appendix if it is longer than half a page. Justify keeping or dropping each tier with what it caught (section 6) against the minutes it cost (`effort.csv`). *(fill in — derived from the results, not from the plan)*

## 9. Value to the school (exactly 1 page, can be read alone)

*Source: section 10 of the project plan; section 7 requires this as a separate page.*

- The new skill gap: AI generates code faster than people can read it.
- Why this is an Information Management competence (process design, quality control, risk assessment), not programming.
- What a student actually practised here: verification and critical assessment, not prompt writing.
- One or two concrete results from section 6 that illustrate the point. *(fill in)*

## Appendices (not counted in the 8–12 pages)

- **A.** The 12-criterion checklist (`checklist.md`).
- **B.** The short process checklist handed over to the organisation.
- **C.** The anonymised development log (`log.csv`), or a note on where it is available.
- **D.** Tool versions and model versions used.
- **E.** Glossary of the few technical terms that remain in the report (e.g. secret key, authorisation, false positive).
