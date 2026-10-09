# Test cases — <feature name>

Template for **task T4** (Tier 2 — systematic behavior testing). Copy it to `test-case-<feature name>.md` in the repository root and fill it in.

**Principles:**

- Cases are derived **only from the requirements** below, not from the original prompt or the source code.
- All 6 required groups must be present. If a group genuinely does not apply, keep its heading and state why; do not delete it.
- The *Actual result* and *Pass?* columns are filled in by a **human** while trying the feature. When AI generates the list, those two columns stay empty.
- Do not put real user data, customer names or internal module names in the file (rule A.1).
- When asking an AI to generate cases, tell it the output language you read best — English, Traditional Chinese (繁體中文) or Vietnamese — and to keep the case IDs (TC-xx), table headings and the six group headings in English, so files from different students line up.

---

## Requirements

> <paste the *Requirement* column of the matching row in `log.csv` verbatim>

## Preconditions

- Test accounts: <e.g. 2 regular accounts A, B and 1 admin account>
- Required data: <e.g. account A has 0 records, account B has ≥ 1,000 records>
- How to simulate a slow network: <e.g. DevTools → Network → Slow 3G>

---

## 1. Main flow

| ID | Steps | Expected result | Actual result | Pass? |
| --- | --- | --- | --- | --- |
| TC-01 | | | | |

## 2. Empty data

Lists with no elements, filters that match nothing, empty fields, a newly created account with no data.

| ID | Steps | Expected result | Actual result | Pass? |
| --- | --- | --- | --- | --- |
| TC-1x | | | | |

## 3. Invalid data

Wrong type, too long, special characters, negative numbers, non-existent dates, **an ID belonging to someone else** (change the parameter in the URL / request).

| ID | Steps | Expected result | Actual result | Pass? |
| --- | --- | --- | --- | --- |
| TC-2x | | | | |

## 4. Slow network

Slow responses, connection lost midway, an external service not responding.

| ID | Steps | Expected result | Actual result | Pass? |
| --- | --- | --- | --- | --- |
| TC-3x | | | | |

## 5. Duplicate actions

Clicking submit twice, reloading the page after submitting, editing the same record in two tabs.

| ID | Steps | Expected result | Actual result | Pass? |
| --- | --- | --- | --- | --- |
| TC-4x | | | | |

## 6. Expired session

Log out in another tab and then act, delete the session cookie, use an expired token.

| ID | Steps | Expected result | Actual result | Pass? |
| --- | --- | --- | --- | --- |
| TC-5x | | | | |

---

## Notes after testing

- Cases: <total> — passed: <n> — failed: <n>
- Failed cases that were **not** revealed by the first manual check: <list IDs>
