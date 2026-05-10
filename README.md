# ReviewPal

ReviewPal is an AI-powered GitHub pull request reviewer that uses repository code context, coding standards, and validation guardrails to generate higher-signal inline review comments.
ReviewPal is an AI-powered GitHub pull request reviewer that uses repository code context, coding standards, and validation guardrails to generate higher-signal inline review comments.

It is built to answer a practical question:

Can an LLM reviewer behave more like a useful SaaS code review product and less like a generic chatbot?

## What makes ReviewPal different

Naive LLM review systems usually fail in predictable ways:
- they comment on the wrong lines
- they miss the local business flow around a change
- they ignore repository-specific standards
- they produce generic or low-confidence comments

ReviewPal addresses those problems with:
- structured diff parsing
- repository indexing with persisted vector search
- generic bounded code chunking with line-range metadata
- same-file context prioritization
- hybrid retrieval that combines semantic and lexical matching
- standards-aware prompting
- verification and validation before posting comments

## Why this project matters

This is not just an LLM wrapper. It is an engineering project around:
- retrieval quality
- review precision
- runtime reliability
- evaluation
- developer workflow integration

That is the part that makes it resume-worthy for SDE 2 roles.
- they miss the local business flow around a change
- they ignore repository-specific standards
- they produce generic or low-confidence comments

ReviewPal addresses those problems with:
- structured diff parsing
- repository indexing with persisted vector search
- generic bounded code chunking with line-range metadata
- same-file context prioritization
- hybrid retrieval that combines semantic and lexical matching
- standards-aware prompting
- verification and validation before posting comments

## Why this project matters

This is not just an LLM wrapper. It is an engineering project around:
- retrieval quality
- review precision
- runtime reliability
- evaluation
- developer workflow integration

That is the part that makes it resume-worthy for SDE 2 roles.

## Architecture

![ReviewPal architecture](images/ReviewPal_architecture.png)

### Indexing pipeline

The indexing flow prepares repository context for review:
- scan supported source files
- split code into bounded chunks with line metadata
- attach `repo_id`, language, content hash, and chunk metadata
- incrementally update vector collections
- retry and throttle indexing writes to reduce rate-limit failures
- index standards independently from code

### Review pipeline

The review flow processes a PR in stages:
1. fetch PR files from GitHub
2. parse unified diffs into structured chunks
3. retrieve relevant code and standards context
4. generate candidate comments with a typed schema
5. verify each candidate with a second-pass check
6. validate line accuracy, confidence, and duplicates
7. post approved inline comments back to GitHub

## Core components

- [src/pipeline/pipeline.py](src/pipeline/pipeline.py) orchestrates the review run
- [src/agents/review_agent.py](src/agents/review_agent.py) performs generation and verification
- [src/core/processors.py](src/core/processors.py) parses PR diffs
- [src/core/validator.py](src/core/validator.py) validates and ranks review comments
- [src/rag/code_retriever.py](src/rag/code_retriever.py) indexes code and retrieves code context
- [src/rag/chunking.py](src/rag/chunking.py) provides bounded chunking and retrieval helpers
- [src/rag/standards_retriever.py](src/rag/standards_retriever.py) indexes and retrieves standards
- [src/rag/indexing.py](src/rag/indexing.py) adds rate-limit-safe indexing helpers

## Demo proof

The repository includes a Python sample codebase and PR scenarios specifically designed to demonstrate ReviewPal’s behavior.

### Sample codebase

- [samples/python_demo_repo](samples/python_demo_repo/README.md)

This repo models a checkout workflow with:
- validation
- pricing
- inventory reservation
- payment capture
- persistence

That gives the reviewer enough context to make meaningful comments instead of toy observations.

### Demo PR scenarios

- [samples/python_demo_prs/pr1_bad_checkout_flow.patch](samples/python_demo_prs/pr1_bad_checkout_flow.patch)
- [samples/python_demo_prs/pr2_failure_handling_regression.patch](samples/python_demo_prs/pr2_failure_handling_regression.patch)

Expected findings are documented here:
- [samples/python_demo_prs/pr1_expected_findings.md](samples/python_demo_prs/pr1_expected_findings.md)
- [samples/python_demo_prs/pr2_expected_findings.md](samples/python_demo_prs/pr2_expected_findings.md)

Recommended demo path:
1. create a public GitHub repo from `samples/python_demo_repo`
2. open branches using the patch scenarios above
3. raise real GitHub PRs
4. run ReviewPal on those PRs
5. capture the inline comments and PR links for your resume, portfolio, or README

## Evaluation

Two evaluation layers are included.

### 1. Deterministic benchmark

- [evals/review_benchmark.json](evals/review_benchmark.json)
- [scripts/run_eval.py](scripts/run_eval.py)

This checks core validation behavior such as:
- commenting only on added lines
- rejecting invalid line comments

Run it with:

```bash
python scripts/run_eval.py
```

### 2. Reviewer quality cases

- [evals/review_quality_cases.json](evals/review_quality_cases.json)
- [evals/README.md](evals/README.md)

This is the starter dataset for measuring actual review usefulness using realistic PR scenarios.

## Getting started

### 1. Clone the repository

```bash
git clone https://github.com/<your-account>/ReviewPal.git
cd ReviewPal
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file:

```bash
GEMINI_API_KEY=your_gemini_api_key
TOKEN_GITHUB=your_github_pat
GITHUB_REPO=owner/repo-name
PR_NUMBER=123
REVIEW_MODEL=gemini-2.5-flash
EMBEDDINGS_MODEL=models/gemini-embedding-001
MAX_REVIEW_WORKERS=4
MIN_COMMENT_CONFIDENCE=0.65
CODE_CHUNK_SIZE_LINES=60
CODE_CHUNK_OVERLAP_LINES=12
MAX_CHUNKS_PER_FILE=12
LEXICAL_CONTEXT_LIMIT=3
INDEXING_BATCH_SIZE=12
INDEXING_BATCH_SLEEP_MS=750
INDEXING_MAX_RETRIES=5
INDEXING_BACKOFF_BASE_SECONDS=2
```

### 4. Build the retrieval index

```bash
python scripts/index_repo.py --path . --repo-id owner/repo-name --standards-path ./standards
```

### 5. Run the reviewer

```bash
python src/pipeline/pipeline.py
```

### 6. Run tests

```bash
python -m unittest discover -s tests
```

Run the benchmark harness:

```bash
python scripts/run_eval.py
```

## CI integration

The repository includes a GitHub Actions workflow that:
- installs dependencies
- restores cached vector data
- rebuilds or updates the retrieval index
- runs the PR review pipeline on `pull_request` events

See [.github/workflows/code-review.yml](.github/workflows/code-review.yml).

## Current limitations

- retrieval is semantic-first and not yet symbol-aware
- verification still relies on the same model family as generation
- benchmark coverage is intentionally small and should grow into a proper offline evaluation set
- there is not yet a dedicated UI for reviewer debugging or prompt tracing

## Next upgrades

- hybrid retrieval with lexical plus vector search
- symbol-aware and file-neighborhood context expansion
- category-specific passes for bugs, security, and performance
- richer evaluation datasets with precision and false-positive tracking
- a lightweight review console to inspect retrieved context and final comments
