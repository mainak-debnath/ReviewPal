# ReviewPal

ReviewPal is an AI-powered GitHub pull request reviewer that combines diff analysis, repository retrieval, coding standards, and validation guardrails to produce higher-signal inline review comments.

This branch upgrades the project toward a more production-oriented shape with:
- repo-scoped incremental indexing for code and standards
- structured comment generation with typed schemas
- a verification pass for filtering speculative comments
- strict added-line validation before posting to GitHub
- repeatable unit tests and a lightweight benchmark harness

## Problem

Most LLM code reviewers break down in a few common ways:
- they comment on the wrong lines
- they ignore repository-specific context
- they produce generic or low-confidence feedback
- they are hard to evaluate offline

ReviewPal is designed as a staged review pipeline instead of a single prompt so those failure modes can be controlled more explicitly.

## Architecture

![ReviewPal architecture](images/ReviewPal_architecture.png)

### Indexing pipeline

The indexing flow prepares repository context for retrieval:
- parse supported source files
- attach `repo_id`, language, and content hashes
- incrementally upsert Chroma collections
- remove stale documents when files disappear
- index standards independently from source code

### Review pipeline

The review flow processes PR diffs in stages:
1. fetch changed files from GitHub
2. parse hunks into structured diff chunks
3. retrieve relevant code context and standards
4. generate candidate comments using a typed schema
5. verify each candidate comment with a second pass
6. validate line accuracy, deduplicate, and apply confidence thresholds
7. post approved comments back to GitHub

## Core components

- [src/pipeline/pipeline.py](src/pipeline/pipeline.py) orchestrates the end-to-end review run
- [src/agents/review_agent.py](src/agents/review_agent.py) performs retrieval, generation, and verification
- [src/core/processors.py](src/core/processors.py) parses unified diffs into structured chunks
- [src/core/validator.py](src/core/validator.py) enforces posting safety rules
- [src/rag/code_retriever.py](src/rag/code_retriever.py) handles repo-aware code retrieval and incremental code indexing
- [src/rag/standards_retriever.py](src/rag/standards_retriever.py) handles standards retrieval and incremental standards indexing
- [scripts/run_eval.py](scripts/run_eval.py) runs a deterministic benchmark harness for core review constraints

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
```

### 4. Build the retrieval index

```bash
python scripts/index_repo.py --path . --repo-id owner/repo-name --standards-path ./standards
```

### 5. Run the review pipeline

```bash
python src/pipeline/pipeline.py
```

## Verification

Run unit tests:

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
