# Python Demo PR Scenarios

This folder contains two recruiter-friendly pull request scenarios for the Python demo codebase in [samples/python_demo_repo](/C:/Projects/ReviewPal/samples/python_demo_repo/README.md:1).

Use them like this:

1. Create a public GitHub repo from `samples/python_demo_repo`.
2. Create a branch for one scenario.
3. Apply the patch or manually make the same code changes.
4. Open a PR.
5. Point ReviewPal at that repo and PR.
6. Capture the resulting inline comments as screenshots and links for your resume or portfolio.

The goal is not to create toy mistakes. Each scenario introduces realistic reviewable problems that should benefit from:
- same-file context retrieval
- repo-wide code retrieval
- standards-aware review behavior

Files in this folder:
- `pr1_bad_checkout_flow.patch`
- `pr1_expected_findings.md`
- `pr2_failure_handling_regression.patch`
- `pr2_expected_findings.md`
