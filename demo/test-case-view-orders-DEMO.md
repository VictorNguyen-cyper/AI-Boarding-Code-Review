# Test cases — View orders (DEMO)

> DEMO — not research data. Generated with `python run_tier2.py`.

| ID | Group | Steps | Expected result | Actual result | Pass? |
| --- | --- | --- | --- | --- | --- |
| TC-01 | Main flow | Alice views her order list | 200, Alice's 2 non-deleted orders | 200, 2 orders | Pass |
| TC-02 | Main flow | Alice views order 1 | 200, order 1 | 200 {"deleted":0,"id":1,"note":"Alice's order","status":"done","user_id":1 | Pass |
| TC-03 | Main flow | Alice creates a new order | 201, with id | 201 {"id":5} | Pass |
| TC-04 | Main flow | Alice views her completion rate | total=2, rate=50.0 (deleted orders excluded) | 200 total=3 rate=33.3 | **Fail** |
| TC-11 | Empty data | New account views the order list | 200, empty list | 200 [] | Pass |
| TC-12 | Empty data | New account views stats | 200, rate=0 or a no-data message | 500 <!doctype html> <html lang=en> <title>500 Internal Server Error</title | **Fail** |
| TC-21 | Invalid data | Alice opens order 4 (Bob's) by changing the ID | 403 or 404 | 200 {"deleted":0,"id":4,"note":"Bob's order","status":"done","user_id":2} | **Fail** |
| TC-22 | Invalid data | Create an order without the note field | 400, missing field message | 500 <!doctype html> <html lang=en> <title>500 Internal Server Error</title | **Fail** |
| TC-23 | Invalid data | Create an order with a 100,000-character note | 400, too long message | 201 {"id":5} | **Fail** |
| TC-31 | Slow network | Shipping service refuses the connection | 502/503, generic message, no internal address | 500 {"error":"<urlopen error [Errno 61] Connection refused>","url":"http:/ (internal URL leaked) | **Fail** |
| TC-32 | Slow network | Shipping service hangs without answering | Error returned within a few seconds | still waiting after 8 seconds, no timeout | **Fail** |
| TC-41 | Duplicate actions | Click Submit twice with the same content | Only 1 order created | 2 orders created | **Fail** |
| TC-51 | Expired session | Call /orders without a token | 401, login required message | 500 <!doctype html> <html lang=en> <title>500 Internal Server Error</title | **Fail** |
| TC-52 | Expired session | Call /orders with an expired token | 401, session expired message | 500 <!doctype html> <html lang=en> <title>500 Internal Server Error</title | **Fail** |

Total: 14 — passed: 4 — failed: 10
