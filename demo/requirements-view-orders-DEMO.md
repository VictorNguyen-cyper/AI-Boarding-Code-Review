# Requirements — View orders (DEMO)

> DEMO — not research data. Sample requirements file for trying Tier 3 (`review.sh`) on the simulated app in `demo/app/`. Written as a requirements document, not as the prompt used to generate the code (section 5.3 of the project plan).

## Purpose

Signed-in customers can see their own orders, place a new order, see a completion summary and check an order's shipping status.

## Users and sign-in

- Every request must carry a valid sign-in token (`Authorization: Bearer <token>`).
- A missing, unknown or expired token must get a clear "please sign in again" response (401), never a server error.

## Business rules

1. **Ownership.** A customer can only see and act on orders they created. Opening another customer's order, for example by changing the ID in the URL, must be refused (403 or 404).
2. **Deleted orders.** Orders marked as deleted are hidden from the customer everywhere: in the list, in the order detail and in every figure.
3. **Order note.** Optional free text, at most 500 characters. Anything longer, or a request with a missing or malformed body, is rejected with 400 and a short message.
4. **No duplicate orders.** Submitting the same order twice (double click, resent request) must create only one order.

## Functions

| # | Function | Expected behavior |
| --- | --- | --- |
| F1 | Order list | Returns the customer's non-deleted orders, each with its items. A customer with no orders sees an empty list, not an error. Must stay fast for customers with hundreds of orders. |
| F2 | Order detail | Returns one order belonging to the customer. Not found or not owned → 404. |
| F3 | Create order | Creates a `pending` order for the customer with an optional note (rules 3 and 4). Returns the new order's ID. |
| F4 | Completion summary | Shows total orders, completed orders (`status = done`) and the completion rate in percent, counting only non-deleted orders. A customer with no orders sees 0 and no error. |
| F5 | Shipping status | Asks the external shipping service for the order's tracking status. If the service is slow (no answer within 5 seconds) or unavailable, return 503 with a generic message. Never show the service's address, keys or raw error text. |

## Security and configuration

- Keys and secrets (app secret key, shipping service key) are read from environment variables, never written in the source code.
- Error messages shown to customers contain no internal details (stack traces, internal addresses, SQL).

## Out of scope

- Editing or cancelling orders.
- The sign-in screen and how tokens are issued.
