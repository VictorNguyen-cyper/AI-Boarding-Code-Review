# Review — <feature name>

Template for **task T5** (Tier 3 — scope-limited AI review). Copy it to `review-<feature name>.md` in the repository root and fill it in.

**Principles** (from `checklist.md` and section 5.3 of the project plan):

- Review only against the **requirements document** and the source code; never give the original prompt to the reviewing model.
- Use a **different** model from the one that generated the code.
- The reviewer only records findings and **does not decide right or wrong**. Leave the *Human classification* field empty until consolidation in task T6.
- Record locations as file / function / endpoint, not internal module names. Never copy secret values into the file.
- AI output language: English, Traditional Chinese (繁體中文) or Vietnamese — pick the one you read best (`./review.sh --lang en|zh-Hant|vi`, see `ai-review.md`). Criterion codes, answers (Yes / No) and severity (High / Medium / Low) always stay in English.

---

## Review information

| Item | Value |
| --- | --- |
| Feature | <must match the *Feature* column in `log.csv` exactly> |
| Code-generating model | <model name> |
| Reviewing model | <model name — must differ from the line above> |
| Output language | <en / zh-Hant / vi> |
| Review date | <YYYY-MM-DD> |
| Files reviewed | <list of files / directories> |

## Requirements

> <paste the *Requirement* column from `log.csv` verbatim>

---

## Results for the 12 criteria

*Passing answer* comes from `checklist.md`. The *Answer* column records the literal answer to the criterion's question (Yes / No / Not applicable), not yet a verdict that something is a bug.

| Code | Criterion (short) | Passing answer | Answer | Findings |
| --- | --- | --- | --- | --- |
| C01 | Secret in source / committed config | No | | |
| C02 | Error messages contain internal information | No | | |
| C03 | Data endpoints check permissions server-side | Yes | | |
| C04 | Changing an ID to someone else's is refused | Yes | | |
| C05 | Submitted data validated server-side | Yes | | |
| C06 | Figure queries apply all required filters | Yes | | |
| C07 | Sum / count / ratio handle no data | Yes | | |
| C08 | Empty list state handled separately | Yes | | |
| C09 | Duplicate submission creates duplicate data | No | | |
| C10 | Expired session / bad credentials answered clearly | Yes | | |
| C11 | External dependencies have timeout and failure path | Yes | | |
| C12 | Query runs once per list element | No | | |

---

## Findings

One entry per finding, in exactly the format from `checklist.md`:

```
- Criterion: <criterion code, e.g. C03>
  Location: <file / function / endpoint>
  Severity: High / Medium / Low
  Description: <what was observed, 1-2 sentences>
  Also found by automated scan: <Yes — rule ID / No>
  Human classification: <leave empty — fill in during T6: True / False positive>
```

<!-- Findings start here -->

---

## Signs outside the 12 criteria

Problems observed that no criterion covers. If this kind recurs across several features, add a new criterion to `checklist.md` with the date it was added.

- <leave empty if none>
