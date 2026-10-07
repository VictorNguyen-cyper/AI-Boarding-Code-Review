# DEMO — run the Tier 2 cases for the "View orders" feature automatically.
# Cases are derived from the requirements, following the 6 groups in templates/test-case-template.md.
import json
import sqlite3
import sys
import tempfile
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "app"))
import app as demo  # noqa: E402

ALICE = {"Authorization": "Bearer token-alice"}
NEW = {"Authorization": "Bearer token-new"}


def fresh_db():
    path = tempfile.NamedTemporaryFile(suffix=".db", delete=False).name
    conn = sqlite3.connect(path)
    demo.init_db(conn)
    conn.commit()
    conn.close()
    demo.app.config.update(DB=path, TESTING=False, PROPAGATE_EXCEPTIONS=False)
    return demo.app.test_client()


def brief(r):
    body = r.get_data(as_text=True).strip().replace("\n", " ")
    return f"{r.status_code} {body[:70]}"


cases = []


def tc(case_id, group, steps, expected, fn):
    c = fresh_db()
    try:
        actual, passed = fn(c)
    except Exception as e:  # error in the test step itself
        actual, passed = f"error while testing: {e}", False
    cases.append((case_id, group, steps, expected, actual, passed))


# 1. Main flow
tc("TC-01", "Main flow", "Alice views her order list", "200, Alice's 2 non-deleted orders",
   lambda c: (lambda r: (f"{r.status_code}, {len(r.json)} orders", r.status_code == 200 and len(r.json) == 2))(c.get("/orders", headers=ALICE)))
tc("TC-02", "Main flow", "Alice views order 1", "200, order 1",
   lambda c: (lambda r: (brief(r), r.status_code == 200 and r.json["id"] == 1))(c.get("/orders/1", headers=ALICE)))
tc("TC-03", "Main flow", "Alice creates a new order", "201, with id",
   lambda c: (lambda r: (brief(r), r.status_code == 201))(c.post("/orders", headers=ALICE, json={"note": "new"})))


def tc04(c):
    r = c.get("/stats", headers=ALICE)
    # Alice has 2 non-deleted orders, 1 done -> requirements say "excluding deleted orders" -> 50.0
    return f"{r.status_code} total={r.json['total']} rate={r.json['rate']}", r.json["total"] == 2 and r.json["rate"] == 50.0


tc("TC-04", "Main flow", "Alice views her completion rate", "total=2, rate=50.0 (deleted orders excluded)", tc04)

# 2. Empty data
tc("TC-11", "Empty data", "New account views the order list", "200, empty list",
   lambda c: (lambda r: (brief(r), r.status_code == 200 and r.json == []))(c.get("/orders", headers=NEW)))
tc("TC-12", "Empty data", "New account views stats", "200, rate=0 or a no-data message",
   lambda c: (lambda r: (brief(r), r.status_code == 200))(c.get("/stats", headers=NEW)))

# 3. Invalid data
tc("TC-21", "Invalid data", "Alice opens order 4 (Bob's) by changing the ID", "403 or 404",
   lambda c: (lambda r: (brief(r), r.status_code in (403, 404)))(c.get("/orders/4", headers=ALICE)))
tc("TC-22", "Invalid data", "Create an order without the note field", "400, missing field message",
   lambda c: (lambda r: (brief(r), r.status_code == 400))(c.post("/orders", headers=ALICE, json={})))
tc("TC-23", "Invalid data", "Create an order with a 100,000-character note", "400, too long message",
   lambda c: (lambda r: (brief(r), r.status_code == 400))(c.post("/orders", headers=ALICE, json={"note": "x" * 100000})))


# 4. Slow network / failing dependency
def tc31(c):
    r = c.get("/orders/1/tracking", headers=ALICE)
    leaked = "127.0.0.1" in r.get_data(as_text=True)
    return brief(r) + (" (internal URL leaked)" if leaked else ""), r.status_code in (502, 503) and not leaked


tc("TC-31", "Slow network", "Shipping service refuses the connection", "502/503, generic message, no internal address", tc31)


def tc32(c):
    # Simulate a hung service: the socket accepts connections but never answers.
    import socket
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    s.listen()
    demo.SHIPPING_URL = f"http://127.0.0.1:{s.getsockname()[1]}/track"
    out = {}

    def call():
        t0 = time.time()
        out["r"] = c.get("/orders/1/tracking", headers=ALICE)
        out["t"] = time.time() - t0

    th = threading.Thread(target=call, daemon=True)
    th.start()
    th.join(8)
    demo.SHIPPING_URL = "http://127.0.0.1:9/track"
    if th.is_alive():
        return "still waiting after 8 seconds, no timeout", False
    return f"{brief(out['r'])} after {out['t']:.1f}s", out["t"] < 8


tc("TC-32", "Slow network", "Shipping service hangs without answering", "Error returned within a few seconds", tc32)


# 5. Duplicate actions
def tc41(c):
    c.post("/orders", headers=ALICE, json={"note": "double click"})
    c.post("/orders", headers=ALICE, json={"note": "double click"})
    n = len([o for o in c.get("/orders", headers=ALICE).json if o["note"] == "double click"])
    return f"{n} orders created", n == 1


tc("TC-41", "Duplicate actions", "Click Submit twice with the same content", "Only 1 order created", tc41)

# 6. Expired session
tc("TC-51", "Expired session", "Call /orders without a token", "401, login required message",
   lambda c: (lambda r: (brief(r), r.status_code == 401))(c.get("/orders")))
tc("TC-52", "Expired session", "Call /orders with an expired token", "401, session expired message",
   lambda c: (lambda r: (brief(r), r.status_code == 401))(c.get("/orders", headers={"Authorization": "Bearer expired"})))

# Output table
lines = ["| ID | Group | Steps | Expected result | Actual result | Pass? |", "| --- | --- | --- | --- | --- | --- |"]
for case_id, group, steps, expected, actual, passed in cases:
    actual = actual.replace("|", "\\|")
    lines.append(f"| {case_id} | {group} | {steps} | {expected} | {actual} | {'Pass' if passed else '**Fail**'} |")
n_pass = sum(1 for x in cases if x[5])
print("\n".join(lines))
print(f"\nTotal: {len(cases)} — passed: {n_pass} — failed: {len(cases) - n_pass}")
json.dump([dict(zip(["id", "group", "steps", "expected", "actual", "passed"], x)) for x in cases],
          open(Path(__file__).parent / "tier2.json", "w"), ensure_ascii=False, indent=1)
