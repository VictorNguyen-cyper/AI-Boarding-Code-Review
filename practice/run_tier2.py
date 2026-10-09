# PRACTICE — run the Tier 2 cases for the "Notes" feature automatically.
# Cases come from requirements-notes-PRACTICE.md, in the 6 groups of templates/test-case-template.md.
import os
import sys
import tempfile
from pathlib import Path

os.environ["NOTES_DB"] = tempfile.NamedTemporaryFile(suffix=".db", delete=False).name
sys.path.insert(0, str(Path(__file__).parent / "app"))
import app as notes  # noqa: E402

ALICE = {"Authorization": "Bearer token-alice"}
BOB = {"Authorization": "Bearer token-bob"}
c = notes.app.test_client()


def brief(r):
    body = r.get_data(as_text=True).strip().replace("\n", " ")
    return f"{r.status_code} {body[:60]}".strip()


def reset():
    with notes.app.app_context():
        notes.db().execute("DELETE FROM notes")
        notes.db().commit()


def alice_note(title="Buy milk", body="2 litres"):
    return c.post("/notes", json={"title": title, "body": body}, headers=ALICE).get_json()["id"]


def count(headers):
    return len(c.get("/notes", headers=headers).get_json())


def tc_01():
    reset()
    alice_note("First")
    alice_note("Second")
    r = c.get("/notes", headers=ALICE)
    titles = [n["title"] for n in r.get_json()]
    return r.status_code == 200 and titles == ["Second", "First"], f"{r.status_code} {titles}"


def tc_02():
    reset()
    r = c.post("/notes", json={"title": "  Buy milk  ", "body": "2 litres"}, headers=ALICE)
    title = c.get(f"/notes/{r.get_json()['id']}", headers=ALICE).get_json()["title"]
    return r.status_code == 201 and title == "Buy milk", f"{brief(r)}, stored title {title!r}"


def tc_03():
    reset()
    r = c.get(f"/notes/{alice_note()}", headers=ALICE)
    return r.status_code == 200, brief(r)


def tc_04():
    reset()
    nid = alice_note()
    r = c.delete(f"/notes/{nid}", headers=ALICE)
    gone = c.get(f"/notes/{nid}", headers=ALICE).status_code
    return r.status_code == 204 and gone == 404, f"{r.status_code}, read afterwards {gone}"


def tc_11():
    reset()
    r = c.get("/notes", headers=BOB)
    return r.status_code == 200 and r.get_json() == [], brief(r)


def tc_12():
    reset()
    r = c.post("/notes", json={"title": "No body"}, headers=ALICE)
    return r.status_code == 201, brief(r)


def tc_13():
    reset()
    r = c.post("/notes", json={"title": "   "}, headers=ALICE)
    return r.status_code == 400, brief(r)


def tc_21():
    reset()
    r = c.get(f"/notes/{alice_note()}", headers=BOB)
    return r.status_code == 404, brief(r)


def tc_22():
    reset()
    nid = alice_note()
    r = c.delete(f"/notes/{nid}", headers=BOB)
    still = c.get(f"/notes/{nid}", headers=ALICE).status_code
    return r.status_code == 404 and still == 200, f"{r.status_code}, Alice still reads it: {still}"


def tc_23():
    reset()
    ok = c.post("/notes", json={"title": "x" * 100}, headers=ALICE).status_code
    r = c.post("/notes", json={"title": "x" * 101}, headers=ALICE)
    return ok == 201 and r.status_code == 400, f"100 chars {ok}; 101 chars {brief(r)}"


def tc_24():
    reset()
    ok = c.post("/notes", json={"title": "t", "body": "x" * 2000}, headers=ALICE).status_code
    r = c.post("/notes", json={"title": "t", "body": "x" * 2001}, headers=ALICE)
    return ok == 201 and r.status_code == 400, f"2000 chars {ok}; 2001 chars {brief(r)}"


def tc_25():
    reset()
    r = c.post("/notes", data="hello", headers=ALICE)
    return r.status_code == 400, brief(r)


def tc_26():
    reset()
    r = c.post("/notes", json={"title": 123}, headers=ALICE)
    return r.status_code == 400, brief(r)


def tc_27():
    reset()
    title = "<script>alert(1)</script> Ghi chú 筆記 ' OR 1=1 --"
    nid = alice_note(title)
    stored = c.get(f"/notes/{nid}", headers=ALICE).get_json()["title"]
    return stored == title and count(ALICE) == 1, "stored unchanged" if stored == title else repr(stored)


def tc_28():
    reset()
    r = c.get("/notes/99999", headers=ALICE)
    return r.status_code == 404, brief(r)


def tc_41():
    reset()
    a = c.post("/notes", json={"title": "Same"}, headers=ALICE).status_code
    b = c.post("/notes", json={"title": "Same"}, headers=ALICE).status_code
    n = count(ALICE)
    return None, f"{a}, {b} — {n} notes created"


def tc_42():
    reset()
    nid = alice_note()
    a = c.delete(f"/notes/{nid}", headers=ALICE).status_code
    b = c.delete(f"/notes/{nid}", headers=ALICE)
    return a == 204 and b.status_code == 404, f"first {a}, second {brief(b)}"


def tc_51():
    r = c.get("/notes")
    return r.status_code == 401, brief(r)


def tc_52():
    r = c.get("/notes", headers={"Authorization": "Bearer token-expired"})
    return r.status_code == 401, brief(r)


def tc_53():
    r = c.post("/notes", json={"title": "x"}, headers={"Authorization": "token-alice"})
    return r.status_code == 401, brief(r)


GROUPS = [
    ("1. Main flow", [
        ("TC-01", "Alice creates 2 notes, then lists them", "200, both notes, newest first", tc_01),
        ("TC-02", "Alice creates a note with title `  Buy milk  `", "201 with id; title stored without surrounding spaces", tc_02),
        ("TC-03", "Alice reads her own note", "200, the note", tc_03),
        ("TC-04", "Alice deletes her own note, then reads it", "204, then 404", tc_04),
    ]),
    ("2. Empty data", [
        ("TC-11", "Bob (no notes) lists his notes", "200, empty list", tc_11),
        ("TC-12", "Create a note with a title and no body", "201 (body is optional)", tc_12),
        ("TC-13", "Create a note whose title is only spaces", "400, title required", tc_13),
    ]),
    ("3. Invalid data", [
        ("TC-21", "Bob opens Alice's note by changing the ID", "404", tc_21),
        ("TC-22", "Bob deletes Alice's note by changing the ID", "404; note still exists for Alice", tc_22),
        ("TC-23", "Title of 100, then 101 characters", "201, then 400", tc_23),
        ("TC-24", "Body of 2,000, then 2,001 characters", "201, then 400", tc_24),
        ("TC-25", "Send a body that is not JSON", "400, short message", tc_25),
        ("TC-26", "Send a title that is a number", "400", tc_26),
        ("TC-27", "Title with HTML, SQL and Vietnamese/Chinese characters", "Stored and returned unchanged; nothing else affected", tc_27),
        ("TC-28", "Read a note ID that does not exist", "404", tc_28),
    ]),
    ("4. Slow network", []),
    ("5. Duplicate actions", [
        ("TC-41", "Submit the same note twice", "Not specified in the requirements", tc_41),
        ("TC-42", "Delete the same note twice", "204, then 404", tc_42),
    ]),
    ("6. Expired session", [
        ("TC-51", "List notes without a token", "401, sign in again message", tc_51),
        ("TC-52", "List notes with an unknown/expired token", "401", tc_52),
        ("TC-53", "Create a note with a header missing `Bearer `", "401", tc_53),
    ]),
]

SLOW_NETWORK_NOTE = (
    "Not applicable: the feature calls no external service; it only uses a local database. "
    "Slow-network behaviour on the client side is outside the requirements."
)


def main():
    lines = [
        "# Test cases — Notes (PRACTICE)",
        "",
        "> PRACTICE — not research data. Cases derived from `requirements-notes-PRACTICE.md`;",
        "> *Actual result* and *Pass?* filled in automatically by `python practice/run_tier2.py`, not by a person.",
        "",
    ]
    total = passed = failed = unclear = 0
    for heading, cases in GROUPS:
        lines += [f"## {heading}", ""]
        if not cases:
            lines += [SLOW_NETWORK_NOTE, ""]
            continue
        lines += ["| ID | Steps | Expected result | Actual result | Pass? |", "| --- | --- | --- | --- | --- |"]
        for cid, steps, expected, fn in cases:
            ok, actual = fn()
            total += 1
            if ok is None:
                unclear += 1
                verdict = "Unclear (requirements gap)"
            elif ok:
                passed += 1
                verdict = "Pass"
            else:
                failed += 1
                verdict = "**Fail**"
            lines.append(f"| {cid} | {steps} | {expected} | {actual.replace('|', '/')} | {verdict} |")
        lines.append("")
    summary = f"Cases: {total} — passed: {passed} — failed: {failed} — unclear: {unclear}"
    lines += ["## Notes after testing", "", f"- {summary}", ""]
    out = Path(__file__).parent / "test-case-notes-PRACTICE.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    os.unlink(os.environ["NOTES_DB"])


main()
