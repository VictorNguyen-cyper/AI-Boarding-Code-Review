# Comparison table — DEMO (1 feature, simulated app)

> DEMO — not research data. The "Manual check" column is a demo assumption (the main flow works).

| # | Problem | Criterion | Severity | Manual | Tier 1 — scan | Tier 2 — testing | Tier 3 — review |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Hard-coded SECRET_KEY | C01 | High | — | ✓ semgrep | — | ✓ |
| 2 | Shipping API key in code | C01 | High | — | ✓ gitleaks | — | ✓ |
| 3 | Another user's order visible by changing the ID | C03, C04 | High | — | — | ✓ TC-21 | ✓ |
| 4 | Raw error + internal URL returned | C02 | Medium | — | — | ✓ TC-31 | ✓ |
| 5 | Submitted data not validated | C05 | Medium | — | — | ✓ TC-22, TC-23 | ✓ |
| 6 | Rate includes deleted orders | C06 | Medium | — | — | ✓ TC-04 | ✓ |
| 7 | Division by zero with no orders | C07 | Medium | — | — | ✓ TC-12 | ✓ |
| 8 | Double click creates two orders | C09 | Medium | — | — | ✓ TC-41 | ✓ |
| 9 | Missing / bad token returns 500 instead of 401 | C10 | Medium | — | — | ✓ TC-51, TC-52 | ✓ |
| 10 | External service call without timeout | C11 | Low | — | ~ different warning on same line | ✓ TC-32 | ✓ |
| 11 | Query per order in a loop (N+1) | C12 | Low | — | — | — (small data) | ✓ |
| | **Total** | | | **0/11** | **2/11** | **9/11** | **11/11** |

Tier 1 findings not matching any problem above: semgrep dynamic-urllib-use-detected (app.py:90) — not classified, left for a human to decide (rule A.1). trivy: 0 findings with Flask 3.1.3 / Werkzeug 3.1.9.
