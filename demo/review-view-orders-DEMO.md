# Review — View orders (DEMO)

> **DEMO** — a trial run of the process on a simulated app. Not research data; do not add it to `log.csv` or the results report.
> Demo limitation: the code and the review were produced by **the same model**, contrary to section 5.3. A real review must use a different reviewing model.

## Review information

| Item | Value |
| --- | --- |
| Feature | View orders |
| Code-generating model | Claude Opus 5.5 (demo) |
| Reviewing model | Claude Opus 5.5 (demo — violates section 5.3) |
| Review date | 2026-10-06 |
| Files reviewed | `app/app.py`, `app/requirements.txt` |

## Results for the 12 criteria

| Code | Criterion (short) | Passing answer | Answer | Findings |
| --- | --- | --- | --- | --- |
| C01 | Secret in source / committed config | No | Yes | 2 |
| C02 | Error messages contain internal information | No | Yes | 1 |
| C03 | Data endpoints check permissions server-side | Yes | No | 1 |
| C04 | Changing an ID to someone else's is refused | Yes | No | 1 |
| C05 | Submitted data validated server-side | Yes | No | 1 |
| C06 | Figure queries apply all required filters | Yes | No | 1 |
| C07 | Sum / count / ratio handle no data | Yes | No | 1 |
| C08 | Empty list state handled separately | Yes | Yes | 0 |
| C09 | Duplicate submission creates duplicate data | No | Yes | 1 |
| C10 | Expired session / bad credentials answered clearly | Yes | No | 1 |
| C11 | External dependencies have timeout and failure path | Yes | No | 1 |
| C12 | Query runs once per list element | No | Yes | 1 |

## Findings

```
- Criterion: C01
  Location: app/app.py:9 — SECRET_KEY config
  Severity: High
  Description: The session signing key is assigned directly as a random string instead of being read from an environment variable.
  Also found by automated scan: Yes — semgrep avoid_hardcoded_config_SECRET_KEY
  Human classification:

- Criterion: C01
  Location: app/app.py:10 — SHIPPING_API_KEY constant
  Severity: High
  Description: The shipping service API key is assigned directly as a random string in source code.
  Also found by automated scan: Yes — gitleaks generic-api-key
  Human classification:

- Criterion: C02
  Location: app/app.py:92 — GET /orders/<id>/tracking
  Severity: Medium
  Description: The error branch returns str(e) verbatim and the internal service address to the user.
  Also found by automated scan: No
  Human classification:

- Criterion: C03
  Location: app/app.py:54 — GET /orders/<id>
  Severity: High
  Description: The handler only identifies the caller; it does not compare the order's user_id with the caller before returning data.
  Also found by automated scan: No
  Human classification:

- Criterion: C04
  Location: app/app.py:54 — GET /orders/<id>
  Severity: High
  Description: The query filters by id only; changing the id to another user's order still returns 200.
  Also found by automated scan: No
  Human classification:

- Criterion: C05
  Location: app/app.py:68 — POST /orders
  Severity: Medium
  Description: The note field is not checked for presence, type or length.
  Also found by automated scan: No
  Human classification:

- Criterion: C06
  Location: app/app.py:77 — GET /stats
  Severity: Medium
  Description: The total count query lacks the deleted=0 condition, while the requirements say "excluding deleted orders".
  Also found by automated scan: No
  Human classification:

- Criterion: C07
  Location: app/app.py:81 — GET /stats
  Severity: Medium
  Description: The division done / total does not handle total = 0.
  Also found by automated scan: No
  Human classification:

- Criterion: C09
  Location: app/app.py:63 — POST /orders
  Severity: Medium
  Description: No idempotency key or unique constraint; every request creates a record.
  Also found by automated scan: No
  Human classification:

- Criterion: C10
  Location: app/app.py:37 — caller identification function
  Severity: Medium
  Description: A missing header or invalid token raises KeyError instead of returning 401.
  Also found by automated scan: No
  Human classification:

- Criterion: C11
  Location: app/app.py:90 — GET /orders/<id>/tracking
  Severity: Low
  Description: urlopen is called without a timeout; when the service hangs, the request hangs too.
  Also found by automated scan: Partly — semgrep dynamic-urllib-use-detected (different warning, same location)
  Human classification:

- Criterion: C12
  Location: app/app.py:48 — GET /orders
  Severity: Low
  Description: Each order runs one more query inside the loop to fetch its items.
  Also found by automated scan: No
  Human classification:
```

## Signs outside the 12 criteria

- None.
