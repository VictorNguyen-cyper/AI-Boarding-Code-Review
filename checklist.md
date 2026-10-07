# Review checklist — 12 criteria

This checklist is used by **Tier 3 (scope-limited AI review)** and by the human part of the review.

**How criteria are chosen:** only questions that **cannot be answered by looking at the UI** are included. There are no generic code-quality criteria (such as "is the code readable", "are variables well named") — those do not produce verifiable evidence.

**How to use it:**

- Answer each criterion with **Yes / No**. The *Passing answer* line states which answer passes, to avoid reading the question the wrong way round.
- Review only against the **requirements document**, never against the original prompt (section 5.3 of the project plan).
- The reviewer **does not decide** whether a finding is right or wrong — they only record it. Classification belongs to a human (rule A.1).

**Finding format** (used in `review-<feature name>.md`, task T5):

```
- Criterion: <criterion code, e.g. C03>
  Location: <file / function / endpoint — do not use internal module names>
  Severity: High / Medium / Low
  Description: <what was observed, 1-2 sentences>
```

**Severity scale:**

| Level | Meaning |
| --- | --- |
| High | Can expose data, leak secrets, or allow access beyond the caller's permissions |
| Medium | Shows wrong figures, or causes errors in states real users will hit |
| Low | Only matters under rare conditions, or only affects operations |

---

## Group A — Secrets and sensitive information

### C01. Is any secret value stored directly in source code or in a committed configuration file?

**Passing answer: No**

Signs to look for:

- A long random string assigned directly to a variable instead of being read from an environment variable.
- A database connection string containing a username and password.
- `.env`, `.env.local`, key files or certificate files appearing in the list of committed files.
- A key in code that runs in the browser (any value sent to the browser must be treated as public).

### C02. Do error messages returned to users contain internal information?

**Passing answer: No**

Signs to look for:

- Error responses contain server file paths, stack traces, or database queries.
- An error is caught and its original message is returned verbatim.
- Login errors distinguish "user does not exist" from "wrong password".

---

## Group B — Authorization and access control

### C03. Does every endpoint that accesses user data check the caller's permissions on the server side?

**Passing answer: Yes**

Signs to look for:

- An endpoint reads or writes data without identifying who the caller is.
- Permissions are enforced only by hiding buttons or menus in the UI.
- There is a "logged in?" check but no "allowed to access this particular record?" check.

### C04. If an ID in the URL or request is changed to a value belonging to someone else, does the system refuse?

**Passing answer: Yes**

Signs to look for:

- The record lookup filters only by the ID from the request, not also by the logged-in user's identity.
- Record IDs are sequential integers, making other users' values easy to guess.
- Delete or update actions take an ID from the request without re-checking ownership.

### C05. Is user-submitted data validated and constrained on the server side?

**Passing answer: Yes**

Signs to look for:

- Validation exists only in the UI (required fields, length limits, choose-from-list).
- The server takes the whole data object from the request and saves it directly, without picking each field that may be changed.
- Fields the system should decide (role, approval status, price, balance) can be set from the request.

---

## Group C — Correctness of displayed figures

### C06. Do the queries behind displayed figures apply all the filters described in the requirements?

**Passing answer: Yes**

Signs to look for:

- The requirements state a condition (only approved records, only the current period, only one unit) but the query lacks it.
- Soft-deleted records are still counted in totals.
- The figures look plausible in size, so nobody cross-checks them — this kind of bug cannot be caught by eye.

### C07. Do sums, counts and ratios handle the case where there is no data?

**Passing answer: Yes**

Signs to look for:

- Division without checking for a zero denominator.
- The sum of an empty list is shown as blank instead of 0.
- An average is computed over a filtered set but divided by the original total count.

---

## Group D — States nobody clicks through

### C08. Is the empty list / no results state handled separately?

**Passing answer: Yes**

Signs to look for:

- The UI was only tried with existing sample data, never with a new account that has no data.
- There is no separate branch for an empty result list.

### C09. Does a duplicate submission (double click, resent request) create duplicate data?

**Passing answer: No**

Signs to look for:

- The submit button is not disabled while the request is in progress.
- There is no unique constraint in the database and no idempotency key for the request.
- An action with financial consequences or outbound notifications has no protection against repetition.

### C10. When the session expires or credentials are invalid, does the system respond clearly?

**Passing answer: Yes**

Signs to look for:

- An expired session leads to a blank page or an incomprehensible error instead of redirecting to the login page.
- Expired credentials keep being used for further calls without a refresh or logout step.

### C11. When an external dependency is slow or failing, is there a timeout and a failure path?

**Passing answer: Yes**

Signs to look for:

- Outbound calls (APIs, payment services, email) have no timeout.
- There is no branch for a failed call — the error propagates straight to the user.
- Retries are unlimited, or actions that are unsafe to repeat are retried.

---

## Group E — Behavior with real data

### C12. Is there any query that runs once per element of a list?

**Passing answer: No**

Signs to look for:

- A database query or network call inside a loop over a list.
- A list returns every record, with no pagination and no limit.
- It runs fast with a few dozen sample records and only chokes once real data grows, so looking at it during development does not reveal it.

---

## Notes on checklist scope

This checklist does **not** replace Tier 2 behavior testing. Tier 2 answers "does the feature do what was asked". This checklist answers "is there a problem even though the feature does what was asked".

If, during the project, a kind of bug keeps recurring that no criterion covers, add a new criterion here and **record the date it was added** — the fact that the checklist had to grow is itself a research result.
