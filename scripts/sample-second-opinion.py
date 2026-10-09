#!/usr/bin/env python3
"""Pick a random sample of classified problems for an independent second verdict.

Usage:
    python3 scripts/sample-second-opinion.py [--share 0.2] [--seed N] [findings.csv]

Prints the sampled problems WITHOUT the first verdict, so the second classifier
(e.g. the mentor) decides without being anchored by it. Their answers go in the
"Second verdict" column of findings.csv; see classification.md.

Only problems that already have a verdict and no second verdict are eligible.
The seed is printed so the same sample can be drawn again. The script only
reads; it never modifies any file.
"""
import argparse
import importlib.util
import math
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

spec = importlib.util.spec_from_file_location("check_classification", ROOT / "scripts" / "check-classification.py")
check_classification = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check_classification)


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--share", type=float, default=0.2, help="fraction to sample (default 0.2)")
    ap.add_argument("--seed", type=int, help="random seed; printed so the sample can be repeated")
    ap.add_argument("findings", nargs="?", default=ROOT / "findings.csv")
    args = ap.parse_args(argv)
    if not 0 < args.share <= 1:
        ap.error("--share must be between 0 and 1")

    rows, errors = check_classification.load(args.findings, check_classification.FINDING_COLUMNS)
    if errors:
        print("fix these first (python3 scripts/check-classification.py):", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1
    eligible = [r for _, r in rows if r["Verdict"] and not r["Second verdict"]]
    if not eligible:
        print("No problem has a verdict without a second verdict yet; nothing to sample.")
        return 0

    seed = args.seed if args.seed is not None else random.SystemRandom().randrange(10**6)
    n = max(1, math.ceil(len(eligible) * args.share))
    sample = random.Random(seed).sample(eligible, n)

    print(f"Seed: {seed} (re-run with --seed {seed} to draw the same sample)")
    print(f"Sampled {n} of {len(eligible)} eligible problem(s). First verdicts are hidden on purpose.\n")
    for i, r in enumerate(sample, start=1):
        print(f"{i}. [{r['Feature']}] {r['Problem']} (criterion: {r['Criterion'] or 'not set'}, "
              f"severity: {r['Severity'] or 'not set'})")
    print("\nFor each one, the second classifier answers Real or False positive.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
