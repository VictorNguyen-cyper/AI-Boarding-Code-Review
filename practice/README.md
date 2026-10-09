# Practice — a small "Notes" feature

> **Not research data.** Use this to practise the 3-tier process on code without planted bugs. Do not put anything from here into `log.csv` (rule A.1).

## Run the app

From the repository root (reuses the demo's virtual environment):

```bash
python3 -m venv demo/.venv && demo/.venv/bin/pip install -r practice/app/requirements.txt
cd practice/app && ../../demo/.venv/bin/python app.py      # http://127.0.0.1:5000
```

Try it from another terminal:

```bash
ALICE=token-alice BOB=token-bob
curl -H "Authorization: Bearer $ALICE" http://127.0.0.1:5000/notes
curl -X POST -H "Authorization: Bearer $ALICE" -H "Content-Type: application/json" \
     -d '{"title":"Buy milk","body":"2 litres"}' http://127.0.0.1:5000/notes
curl -H "Authorization: Bearer $BOB" http://127.0.0.1:5000/notes/1   # 404: not Bob's note
```

Test tokens: `token-alice`, `token-bob`. Data is stored in `practice/app/notes.db` (not committed).

## Run the 3 tiers

1. **Manual check:** try the app yourself, then create `practice/log-PRACTICE.csv` with the header of `log.csv` and one row `Notes`, with *Manual check* set to `Pass` or `Fail`.
2. **Tier 1:** `LOG=practice/log-PRACTICE.csv scripts/scan.sh "Notes" practice/app`
3. **Tier 2:** copy `templates/test-case-template.md` to `practice/test-case-notes-PRACTICE.md` and derive cases from `requirements-notes-PRACTICE.md`.
4. **Tier 3:** `./review.sh --lang vi notes-PRACTICE practice/requirements-notes-PRACTICE.md practice/app`, then follow `ai-review.md` section 5.
