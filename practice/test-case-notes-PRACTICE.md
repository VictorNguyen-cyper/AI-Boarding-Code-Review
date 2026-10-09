# Test cases — Notes (PRACTICE)

> PRACTICE — not research data. Cases derived from `requirements-notes-PRACTICE.md`;
> *Actual result* and *Pass?* filled in automatically by `python practice/run_tier2.py`, not by a person.

## 1. Main flow

| ID | Steps | Expected result | Actual result | Pass? |
| --- | --- | --- | --- | --- |
| TC-01 | Alice creates 2 notes, then lists them | 200, both notes, newest first | 200 ['Second', 'First'] | Pass |
| TC-02 | Alice creates a note with title `  Buy milk  ` | 201 with id; title stored without surrounding spaces | 201 {"id":1}, stored title 'Buy milk' | Pass |
| TC-03 | Alice reads her own note | 200, the note | 200 {"body":"2 litres","id":1,"title":"Buy milk"} | Pass |
| TC-04 | Alice deletes her own note, then reads it | 204, then 404 | 204, read afterwards 404 | Pass |

## 2. Empty data

| ID | Steps | Expected result | Actual result | Pass? |
| --- | --- | --- | --- | --- |
| TC-11 | Bob (no notes) lists his notes | 200, empty list | 200 [] | Pass |
| TC-12 | Create a note with a title and no body | 201 (body is optional) | 201 {"id":1} | Pass |
| TC-13 | Create a note whose title is only spaces | 400, title required | 400 {"error":"Title is required."} | Pass |

## 3. Invalid data

| ID | Steps | Expected result | Actual result | Pass? |
| --- | --- | --- | --- | --- |
| TC-21 | Bob opens Alice's note by changing the ID | 404 | 404 {"error":"Note not found."} | Pass |
| TC-22 | Bob deletes Alice's note by changing the ID | 404; note still exists for Alice | 404, Alice still reads it: 200 | Pass |
| TC-23 | Title of 100, then 101 characters | 201, then 400 | 100 chars 201; 101 chars 400 {"error":"Title max 100 characters, body max 2000."} | Pass |
| TC-24 | Body of 2,000, then 2,001 characters | 201, then 400 | 2000 chars 201; 2001 chars 400 {"error":"Title max 100 characters, body max 2000."} | Pass |
| TC-25 | Send a body that is not JSON | 400, short message | 400 {"error":"Request body must be a JSON object."} | Pass |
| TC-26 | Send a title that is a number | 400 | 400 {"error":"Title is required."} | Pass |
| TC-27 | Title with HTML, SQL and Vietnamese/Chinese characters | Stored and returned unchanged; nothing else affected | stored unchanged | Pass |
| TC-28 | Read a note ID that does not exist | 404 | 404 {"error":"Note not found."} | Pass |

## 4. Slow network

Not applicable: the feature calls no external service; it only uses a local database. Slow-network behaviour on the client side is outside the requirements.

## 5. Duplicate actions

| ID | Steps | Expected result | Actual result | Pass? |
| --- | --- | --- | --- | --- |
| TC-41 | Submit the same note twice | Not specified in the requirements | 201, 201 — 2 notes created | Unclear (requirements gap) |
| TC-42 | Delete the same note twice | 204, then 404 | first 204, second 404 {"error":"Note not found."} | Pass |

## 6. Expired session

| ID | Steps | Expected result | Actual result | Pass? |
| --- | --- | --- | --- | --- |
| TC-51 | List notes without a token | 401, sign in again message | 401 {"error":"Please sign in again."} | Pass |
| TC-52 | List notes with an unknown/expired token | 401 | 401 {"error":"Please sign in again."} | Pass |
| TC-53 | Create a note with a header missing `Bearer ` | 401 | 401 {"error":"Please sign in again."} | Pass |

## Notes after testing

- Cases: 20 — passed: 19 — failed: 0 — unclear: 1
