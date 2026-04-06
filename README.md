# 🧠 ReviewPal: AI-Powered Pull Request Review System

> 🚀 Automated, context-aware GitHub PR reviews using **RAG, LLMs, and parallel processing** — designed for real-world codebases.

## 📌 Overview

ReviewPal is an intelligent code review system that analyzes GitHub Pull Requests and generates **high-quality, standards-compliant inline feedback**.

Unlike basic LLM tools, it uses a **Retrieval-Augmented Generation (RAG) pipeline** to incorporate:

- 📂 Repository code context  
- 📐 Organization-specific coding standards  
- 🧠 Language-aware understanding  

## ✨ Key Features

- 🤖 **AI-powered PR reviews** using Gemini LLM  
- 🧠 **RAG-based architecture** (ChromaDB) for context-aware suggestions  
- ⚡ **Parallel diff processing** for fast reviews (~1–2 minutes)  
- 🎯 Comments only on **newly added lines** (zero noise)  
- 📐 **Standards-driven reviews** (customizable per repo)  
- 🌍 **Language-aware retrieval** (Python, TypeScript, C#)  
- 🔁 **Incremental indexing with content hashing** (cost-efficient)  
- 💾 **CI-integrated vector caching** for persistent performance  
- 🧪 Robust **validation layer** (deduplication + correctness checks)  


## 🧱 Architecture

![ReviewPal architecture img](images/ReviewPal_architecture.png)

### 🔹 System Overview

The system consists of two major flows:

---

### ⚙️ 1. Indexing Pipeline (RAG Setup)

Runs in CI to prepare context:

- Parses repository source code  
- Indexes coding standards  
- Generates embeddings using Gemini  
- Stores vectors in ChromaDB  
- Uses **content hashing** to avoid re-indexing unchanged files  
- Supports **multi-repo isolation via `repo_id`**  

---

### ⚡ 2. Review Pipeline

Triggered on Pull Requests:

1. Fetch PR diffs via GitHub API  
2. Chunk diffs for efficient processing  
3. Process chunks in **parallel threads**  
4. Retrieve relevant:
   - Code context  
   - Coding standards  
5. Generate review comments using LLM  
6. Validate comments:
   - Only on added lines  
   - Remove duplicates  
   - Enforce format  
7. Post inline comments to GitHub

## 🧠 Core Concepts

### 🔍 Retrieval-Augmented Generation (RAG)

ReviewPal enhances LLM outputs by retrieving:

- Relevant code snippets from the repository  
- Applicable coding standards  

This significantly reduces hallucinations and improves accuracy.

---

### ⚡ Parallel Processing

Diff chunks are processed concurrently using multithreading, enabling:

- Faster review times  
- Scalability for large PRs  

---

### 🧩 Language-Aware Filtering

Retrieval is scoped by file type:
E.g.
- .py → Python context
- .ts → TypeScript context
- .cs → C# context
---

### 🔁 Incremental Indexing

Uses content hashing to:

- Detect changed files  
- Re-embed only modified content  
- Reduce API usage and cost  

---

## 🚀 Getting Started

### 1\. Clone the repository

```bash
git clone https://github.com//ReviewPal.git  cd ReviewPal
```

### 2\. Install dependencies

```bash
pip install -r requirements.txt
```

### 3\. Set up environment variables

Create a .env file with the following keys:

```bash
 GEMINI_API_KEY=your_gemini_api_key
 TOKEN_GITHUB=your_github_pat
 GITHUB_REPO=username/repo-name
 PR_NUMBER=your_pull_request_number
```

## 🧪 Usage

Run indexing (RAG setup)
```bash
python scripts/index_repo.py --path . --repo-id your-org/repo standards-path ./standards
```

To run the review pipeline:V

```bash
python src/pipeline/pipeline.py
```
## ⚙️ CI Integration (GitHub Actions)

ReviewPal integrates directly into PR workflows:

 - Runs indexing with caching
 - Executes review pipeline automatically
 - Posts inline comments on PRs

## 📌 Technologies Used

- Python 3.10+
- LangGraph
- LangChain
- [Gemini (Google Generative AI)](https://ai.google.dev/)
- [httpx](https://www.python-httpx.org/)
- ChromaDB (Vector Store)
- GitHub REST API
- ThreadPoolExecutor (parallelism)

## 🔮 Future Scope

- Multi-agent reviewers (security, performance, style)
- Semantic duplicate detection
- PR summary + risk scoring
- Connecting PRs to JIRA and validating against acceptance criteria
