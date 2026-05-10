# Evaluation Dataset Guide

The repository includes two levels of evaluation:

1. `review_benchmark.json`
Purpose:
- fast deterministic checks for validation rules such as added-line enforcement

2. `review_quality_cases.json`
Purpose:
- richer, reviewer-facing quality cases built from realistic PR scenarios

## How to create a useful eval dataset

For each case, capture:
- `name`: short stable identifier
- `scenario`: what kind of defect or regression the PR introduces
- `repo_subpath`: which sample repo or codebase it belongs to
- `patch_file`: the patch that represents the PR
- `expected_findings`: the comments you want ReviewPal to be able to produce
- `forbidden_patterns`: low-value or incorrect comments it should avoid

Good expected findings should specify:
- target file
- approximate line
- category
- severity
- keywords that should appear in a good review

Example categories:
- validation
- state sequencing
- duplicated business logic
- failure handling
- async or I/O misuse
- maintainability

## Suggested workflow

1. Add a realistic PR patch under `samples/python_demo_prs/`.
2. Add a case entry in `review_quality_cases.json`.
3. Run ReviewPal on the PR or fixture.
4. Compare generated comments with expected findings.
5. Record misses, false positives, and weak comments.
6. Tune retrieval, prompting, and verification.

This gives you both a recruiter demo and an internal quality loop.
