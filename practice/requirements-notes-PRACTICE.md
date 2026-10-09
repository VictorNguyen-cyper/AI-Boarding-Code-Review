# Requirements — Notes (PRACTICE)

> PRACTICE — not research data. Input for `review.sh` when trying Tier 3 on `practice/app/`.

## Purpose

Signed-in users keep short private notes: list them, read one, create one and delete one.

## Users and sign-in

- Every request must carry a valid sign-in token (`Authorization: Bearer <token>`).
- A missing or unknown token gets 401 with a "please sign in again" message, never a server error.

## Business rules

1. **Privacy.** A user can only see and delete their own notes. Another user's note, reached by changing the ID, is answered with 404.
2. **Title.** Required, at most 100 characters, surrounding spaces ignored.
3. **Body.** Optional text, at most 2,000 characters.
4. A request with a missing or malformed body is rejected with 400 and a short message.

## Functions

| # | Function | Expected behavior |
| --- | --- | --- |
| F1 | List notes | The user's notes, newest first. No notes → empty list. |
| F2 | Read note | One of the user's notes. Not found or not owned → 404. |
| F3 | Create note | Validates rules 2–4, returns the new note's ID with 201. |
| F4 | Delete note | Deletes one of the user's notes, 204. Not found or not owned → 404. |

## Security and configuration

- Secrets are read from environment variables, never written in the source code.
- Error messages contain no internal details (stack traces, file paths, SQL).

## Out of scope

- Editing notes, sharing notes, search.
- The sign-in screen and how tokens are issued.
