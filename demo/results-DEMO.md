# Results — four tables (task T6)

> **DEMO — not research data.** Built from the simulated app in `demo/`. Do not quote these figures.

Generated on 2026-10-07 by `./qa report` from `log-DEMO.csv`, `findings-DEMO.csv`, `features-DEMO.csv`.
Do not edit by hand: fix the data files and run the command again.

Figures are counts from a small set of features: read them as a case study, not as statistics (plan section 8).

## Data completeness

| Item | Value |
| --- | --- |
| Features logged (plan target 15–25) | 1 |
| Manual check filled | 1/1 |
| Features whose log findings are itemized in findings.csv | 1/1 |
| Findings in findings.csv | 25 |
| Findings not yet classified by a human | 1 |
| Features shipped | 0/1 |
| One-week follow-up done | 0/1 |
| Boundary questions answered | 1/1 |

**1 finding(s) are not classified yet.** They are left out of every true / false figure below.

## Table 1 — Manual check vs. what the tiers found

True-positive findings per tier for each feature. *Unclassified* findings are not counted as true.

| Feature | Manual check | Tier 1 — automated scan | Tier 2 — behavior testing | Tier 3 — AI review | Found after shipping | Unclassified |
| --- | --- | --- | --- | --- | --- | --- |
| View orders | Pass | 2 | 10 | 12 | 0 | 1 |

Of 1 feature(s) rated **Pass** by eye, 1 still had at least one true-positive finding, 1 of them with High or Critical severity.

## Table 2 — Which tier catches which kind of problem

True-positive findings per checklist criterion. Several tiers can report the same problem, so these are
counts of findings, not of distinct problems.

| Criterion | Tier 1 — automated scan | Tier 2 — behavior testing | Tier 3 — AI review | Found after shipping | Caught by |
| --- | --- | --- | --- | --- | --- |
| C01 Is any secret value stored directly in source code or in a committed configuration file? | 2 | 0 | 2 | 0 | Automated tools |
| C02 Do error messages returned to users contain internal information? | 0 | 1 | 1 | 0 | Needs a human or AI review |
| C03 Does every endpoint that accesses user data check the caller's permissions on the server side? | 0 | 0 | 1 | 0 | Needs a human or AI review |
| C04 If an ID in the URL or request is changed to a value belonging to someone else, does the system refuse? | 0 | 1 | 1 | 0 | Needs a human or AI review |
| C05 Is user-submitted data validated and constrained on the server side? | 0 | 2 | 1 | 0 | Needs a human or AI review |
| C06 Do the queries behind displayed figures apply all the filters described in the requirements? | 0 | 1 | 1 | 0 | Needs a human or AI review |
| C07 Do sums, counts and ratios handle the case where there is no data? | 0 | 1 | 1 | 0 | Needs a human or AI review |
| C09 Does a duplicate submission (double click, resent request) create duplicate data? | 0 | 1 | 1 | 0 | Needs a human or AI review |
| C10 When the session expires or credentials are invalid, does the system respond clearly? | 0 | 2 | 1 | 0 | Needs a human or AI review |
| C11 When an external dependency is slow or failing, is there a timeout and a failure path? | 0 | 1 | 1 | 0 | Needs a human or AI review |
| C12 Is there any query that runs once per element of a list? | 0 | 0 | 1 | 0 | Needs a human or AI review |

*Caught by* is derived mechanically: "Automated tools" when Tier 1 has any true positive; otherwise
"Needs a human or AI review" when Tier 2 or 3 does; otherwise "Missed by all tiers".

## Table 3 — Reliability of each tier

Rates use only classified findings (True + False). *Unsure* and *Unclassified* are shown but left out of the rates.

| Tier | Findings | True | False | Unsure | Unclassified | True-positive rate | False-alarm rate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Tier 1 — automated scan | 3 | 2 | 0 | 0 | 1 | 2/2 (100%) | 0/2 (0%) |
| Tier 2 — behavior testing | 10 | 10 | 0 | 0 | 0 | 10/10 (100%) | 0/10 (0%) |
| Tier 3 — AI review (same model (demo)) | 12 | 12 | 0 | 0 | 0 | 12/12 (100%) | 0/12 (0%) |

## Table 4 — Where the full process is needed

Features grouped by the three boundary questions (plan section 8): touches real user data? public on the
internet? kept running over six months?

| Real user data | Public internet | Over 6 months | Features | True positives | High / Critical | Features with bugs found later |
| --- | --- | --- | --- | --- | --- | --- |
| Yes | Yes | Yes | 1 | 24 | 7 | 0/1 |

