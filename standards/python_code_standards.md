# Python Service Review Standards

This document defines the review standards for the Python demo codebase. The goal is to bias ReviewPal toward high-value backend findings instead of style comments.

## 1. Input validation and failure handling

- Validate external input before indexing into nested dictionaries.
- Raise explicit domain-friendly errors instead of leaking raw `KeyError`, `TypeError`, or `ValueError` from deep inside service code.
- When handling lists of external objects, validate required fields before use.
- Avoid partially completed workflows when a downstream operation can fail. Code should make failure states explicit.

## 2. Business logic integrity

- Monetary calculations must preserve domain meaning and should not duplicate pricing logic in multiple places.
- Discounting, tax, and fee calculations should flow through existing pricing abstractions instead of being reimplemented ad hoc.
- Do not silently skip invalid order lines if that changes business outcomes. Reject bad input or surface a clear error.

## 3. Side effects and sequencing

- External side effects such as payment capture, inventory reservation, and event publication should happen in a deliberate order.
- Avoid mutating persistent state before critical validation is complete.
- If a workflow includes multiple side effects, make compensation or rollback expectations clear.

## 4. Repository and service boundaries

- Keep orchestration in service classes and persistence details in repositories.
- Prefer reusing an existing domain service over duplicating the same rule in controllers or handlers.
- Avoid coupling request-shape assumptions directly to lower-level infrastructure classes.

## 5. Async and I/O safety

- Await all async I/O explicitly.
- Avoid serial I/O inside loops when batched or grouped behavior already exists.
- Network or payment clients should surface actionable failures with enough context for debugging.

## 6. Maintainability

- Split code when one function mixes validation, pricing, persistence, and side-effect orchestration.
- Prefer expressive value names over short transport-oriented names.
- Add comments only when the reasoning is non-obvious; code should otherwise remain self-explanatory.
