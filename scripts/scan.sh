#!/bin/sh
# Run all three Tier 1 scanners for one feature, in the order given in section 5
# of automated-scanning.md: gitleaks -> trivy -> semgrep.
#
# Usage:
#   scripts/scan.sh "<feature name>" [source directory]    # default: .
#
# Output goes to scan-results/<feature name>/:
#   gitleaks-report.json, trivy-report.json, semgrep-report.json
#   summary.txt  — each finding pre-formatted for the
#                  "Automated scan findings" column of log.csv.
#
# The script does NOT write to log.csv and does NOT decide whether any finding
# is a true or false positive (rule A.1). A human copies summary.txt into the log.

set -u

NAME="${1:-}"
SOURCE="${2:-.}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LOG="${LOG:-$ROOT/log.csv}"

if [ -z "$NAME" ]; then
  echo "Usage: scripts/scan.sh \"<feature name>\" [source directory]" >&2
  exit 2
fi

# Refuse to scan before the manual check is recorded — otherwise the control column loses its value.
if ! python3 "$ROOT/scripts/check-log.py" --filled "$NAME" "$LOG"; then
  echo "No row '$NAME' in log.csv, or its 'Manual check' column is empty." >&2
  echo "Fill in 'Pass' / 'Fail' BEFORE scanning (section 5.1 of the project plan)." >&2
  exit 1
fi

for tool in gitleaks trivy semgrep; do
  command -v "$tool" >/dev/null 2>&1 || {
    echo "$tool is missing. Install it as described in section 0 of automated-scanning.md." >&2
    exit 2
  }
done

DIR_NAME=$(printf '%s' "$NAME" | tr ' /' '--')
OUT="$ROOT/scan-results/$DIR_NAME"
mkdir -p "$OUT"

started=$(date +%s)

echo "[1/3] gitleaks"
# --redact: keep secret values out of the report.
gitleaks dir "$SOURCE" --redact --no-banner --exit-code 0 \
  --report-format json --report-path "$OUT/gitleaks-report.json"

echo "[2/3] trivy"
trivy fs "$SOURCE" --scanners vuln --severity HIGH,CRITICAL --quiet \
  --format json --output "$OUT/trivy-report.json"

echo "[3/3] semgrep"
semgrep --config=p/security-audit --config=p/secrets --quiet --metrics=off \
  --json --output="$OUT/semgrep-report.json" "$SOURCE"

finished=$(date +%s)

python3 - "$OUT" "$NAME" "$((finished - started))" "$(cd "$SOURCE" && pwd)" <<'PY'
import json, os, sys
from pathlib import Path

out, name, seconds, source = Path(sys.argv[1]), sys.argv[2], sys.argv[3], sys.argv[4]

def relative(path):
    # Record paths relative to the source directory so local machine paths are not exposed.
    return os.path.relpath(os.path.abspath(path), source) if path else path

def load(file):
    p = out / file
    if not p.exists() or p.stat().st_size == 0:
        return None
    return json.loads(p.read_text(encoding="utf-8"))

lines = []
# One line per finding, in the formats from sections 1, 2 and 3 of automated-scanning.md.
for f in load("gitleaks-report.json") or []:
    lines.append(f"gitleaks: {f.get('RuleID')} at {relative(f.get('File'))}:{f.get('StartLine')}")
for r in (load("trivy-report.json") or {}).get("Results") or []:
    for v in r.get("Vulnerabilities") or []:
        lines.append(f"trivy: {v.get('PkgName')} {v.get('VulnerabilityID')} severity {v.get('Severity')}")
for f in (load("semgrep-report.json") or {}).get("results") or []:
    severity = (f.get("extra") or {}).get("severity")
    lines.append(f"semgrep: {f.get('check_id')} at {relative(f.get('path'))}:{(f.get('start') or {}).get('line')} severity {severity}")

summary = "\n".join([
    f"Feature: {name}",
    f"Time for one full scan: {seconds} seconds",
    f"Findings: {len(lines)}",
    "",
    "Paste into the 'Automated scan findings' column (not yet classified as true / false positive):",
    "; ".join(lines) if lines else "(no findings)",
    "",
    "Findings:",
    *[f"- {l}" for l in lines],
]) + "\n"
(out / "summary.txt").write_text(summary, encoding="utf-8")
print(summary)
PY

echo "Full reports: $OUT"
