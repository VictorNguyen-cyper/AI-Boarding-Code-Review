# Installing and running the automated scanners (Tier 1)

Tier 1 covers three kinds of problems: **leaked secrets**, **libraries with published vulnerabilities**, and **pattern-based security bugs**. Install once, then run automatically.

Guide environment: macOS with Homebrew. Already available on the machine: `brew`, `git`, `npm`, `python3`.

---

## 0. One-time installation

```bash
brew install gitleaks semgrep trivy
```

Verify the installation:

```bash
gitleaks version && semgrep --version && trivy --version
```

None of these three tools send source code anywhere in the modes used below. `semgrep` and `trivy` download rule sets / vulnerability databases from the network — that is a download, not an upload of source code.

---

## 1. Secret leak scanning — `gitleaks`

### Commands

Scan files in the working directory (including uncommitted files):

```bash
gitleaks dir . --report-format json --report-path gitleaks-report.json
```

Scan the entire commit history — use this for the first run, because a key that was committed and later deleted is still in history:

```bash
gitleaks git . --report-format json --report-path gitleaks-history-report.json
```

### Reading the results

The tool prints the number of findings (`leaks found`) and returns a **non-zero exit code** when it finds something. Fields to read in each JSON finding:

| Field | Meaning |
| --- | --- |
| `RuleID` | Kind of key detected (AWS key, GitHub token, private key…) |
| `File`, `StartLine` | Location |
| `Secret` | The detected value — **never paste this into the log or a report** |
| `Commit`, `Date` | Present when scanning history: when the key was introduced |

Record in the *Automated scan findings* column of `log.csv` as: `gitleaks: <RuleID> at <File>:<StartLine>`. Never record the key value.

### False positives

Random strings in test data, public keys and hashes can be mistaken for secrets. Once confirmed as a false positive, add it to `.gitleaksignore` in the repository root, one entry per line:

```
<Fingerprint of the finding, copied from the JSON file>
```

**Keep the false-positive count.** The false-positive rate of each tier is one of the four result tables (section 8 of the project plan) — deleting them loses data.

### If a key really has leaked

Removing it from the code is **not enough** — the key is still in commit history and must be treated as exposed. What to do: revoke and reissue the key where it was issued. Tell your mentor before acting.

---

## 2. Scanning libraries with published vulnerabilities

### 2a. One command for every language — `trivy`

`trivy` detects the dependency manifests present in the project:

```bash
trivy fs . --scanners vuln --format table
```

Show only high severity, and only vulnerabilities that already have a fix:

```bash
trivy fs . --scanners vuln --severity HIGH,CRITICAL --ignore-unfixed
```

Export JSON to keep a record:

```bash
trivy fs . --scanners vuln --format json --output trivy-report.json
```

### 2b. Per-ecosystem commands

Also run the command matching the project's language — its results are usually more specific about how to fix:

```bash
# Node.js / JavaScript / TypeScript projects
npm audit
npm audit --json > npm-audit-report.json
npm audit fix            # only upgrades within the safe range

# Python projects
pip3 install pip-audit
pip-audit -r requirements.txt
```

### Reading the results

| What to read | Meaning |
| --- | --- |
| Severity | Handle CRITICAL / HIGH first |
| Is a fix available | If yes, upgrade; if not, record it and tell your mentor |
| Direct or transitive dependency | Transitive (a dependency of a dependency) must be fixed by upgrading the parent library |
| Where it is used | Development-only dependencies have lower priority than production ones |

Record in the log as: `trivy: <library name> <CVE ID> severity <HIGH>`.

### Note on AI code-generation tools

AI tools often pin library versions based on their training data, so they may specify an old version with a known vulnerability. This kind of problem is characteristic of AI-generated code — keep it separate when building the classification table in section 8.

---

## 3. Pattern-based security scanning — `semgrep`

### Commands

Use the built-in rule sets, running locally:

```bash
semgrep --config=p/security-audit --config=p/secrets .
```

Only high-severity findings, exported as JSON:

```bash
semgrep --config=p/security-audit --severity=ERROR --json --output=semgrep-report.json .
```

Language-specific rule sets — use instead of `p/security-audit` once the project language is known:

```bash
semgrep --config=p/javascript .
semgrep --config=p/python .
```

If the first run has too many results, limit it to recent changes:

```bash
semgrep --config=p/security-audit --baseline-commit=HEAD~1 .
```

### Reading the results

Each finding has: **file and line**, **rule ID** (`check_id`), **severity** (`ERROR` / `WARNING` / `INFO`), and a **description** with remediation advice.

Rule types directly related to criteria in `checklist.md`:

| semgrep finding type | Matching criterion |
| --- | --- |
| String concatenation into a database query | C05 |
| Secret hard-coded in source | C01 |
| Network call without a timeout | C11 |
| Original error message returned verbatim | C02 |
| Certificate verification disabled, weak hash algorithm | — (record separately) |

When a semgrep finding matches a checklist criterion, **record both sources in the log** (the *Automated scan findings* and *AI review findings* columns). Where both tiers catch something and where only one does is exactly the data for the classification table in section 8.

### Ignoring a finding

Add a comment directly above the flagged line:

```
// nosemgrep: <check_id>
```

Always give the reason on the same line, and still count the finding as a false positive.

---

## 4. Running automatically

### 4a. Block before commit

Prevent secrets from being committed — the fastest and most important step, because once a key is in history it cannot be taken back. The repository ships this hook in `.githooks/pre-commit` (it also validates `log.csv`); enable it once:

```bash
git config core.hooksPath .githooks
```

### 4b. Full run with one command

`scripts/scan.sh` runs all three tools for one feature and writes a summary ready to paste into the log:

```bash
scripts/scan.sh "<feature name>" [source directory]
```

It refuses to run until the feature's *Manual check* column in `log.csv` is filled in (section 5 below). Reports go to `scan-results/<feature name>/`, which is not committed.

### 4c. Running on GitHub

If the code is hosted on GitHub, create `.github/workflows/scan.yml`:

```yaml
name: automated-scan
on: [push, pull_request]
jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: gitleaks/gitleaks-action@v2
      - uses: aquasecurity/trivy-action@master
        with:
          scan-type: fs
          severity: HIGH,CRITICAL
      - uses: semgrep/semgrep-action@v1
        with:
          config: p/security-audit
```

Note: this configuration sends source code to GitHub's runners. **Only use it once the internship organization has confirmed what data may leave the company** (risk #1, section 9 of the project plan). Until then, run locally only, as in 4a and 4b.

---

## 5. Order of steps for each feature

1. Finish the feature and try it by hand.
2. **Fill in the *Manual check* column of `log.csv` (`Pass` / `Fail`) — do this before step 3.** Filling it in after seeing scan results makes the whole control column worthless (section 5.1 of the project plan).
3. Run `gitleaks` → `trivy` → `semgrep` (or `scripts/scan.sh`).
4. Record every finding in the *Automated scan findings* column, including ones later judged to be false positives, marked as such.
5. Do not decide at this step whether a finding is true or false (rule A.1). Classification happens during consolidation in task T6.

---

## 6. Records from installation

On the first installation, record these three facts for the report:

- The version of each tool (`gitleaks version`, `semgrep --version`, `trivy --version`).
- Time spent installing and configuring, in minutes.
- Time for one full scan, in seconds.

Section 5.2 of the project plan says Tier 1 is *"the lowest cost, catching the most expensive kind of bug"*. These three numbers are the evidence for that claim — without them it is only an opinion.

### First installation figures (2026-10-06)

| Item | Value |
| --- | --- |
| gitleaks | 8.30.1 |
| semgrep | 1.179.0 |
| trivy | 0.75.0 |
| Install time with `brew install` | 1129 seconds (about 19 minutes; mostly semgrep) |
| Time for one full scan | 19 seconds (repository contained only documentation, no feature code yet; first run downloaded semgrep rules) |
| Pre-commit hook (section 4a) | Installed |
