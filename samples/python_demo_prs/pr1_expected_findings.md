# PR 1 Expected Findings

Title: `Bad checkout flow pricing and state sequencing`

This PR is intended to demonstrate that ReviewPal can use code context and standards to catch high-signal workflow issues.

Likely good findings:

1. The PR bypasses `PricingService` and recalculates totals inline.
Reason:
- quantity is ignored
- discount logic is lost
- the existing pricing abstraction already exists in [pricing.py](/C:/Projects/ReviewPal/samples/python_demo_repo/src/checkout/pricing.py:1)

2. `payload["customer"]["id"]` bypasses the existing validated `customer` object.
Reason:
- it can raise raw `KeyError`
- it duplicates logic already handled by `_build_customer`

3. The order is marked `PAID` before payment capture succeeds.
Reason:
- persisted state can become incorrect if `capture_payment` fails
- this breaks the intended `RESERVED -> PAID` workflow

Weak findings to avoid:
- generic comments about "refactor this function"
- style-only comments
- low-value remarks about line length or formatting
