from __future__ import annotations

import argparse
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.config import PROJECT_ROOT, STANDARDS_DIR
from src.rag.code_retriever import CodeRetriever
from src.rag.standards_retriever import StandardsRetriever


def main():
    parser = argparse.ArgumentParser(
        description="Index a repository into ChromaDB for AI code review RAG."
    )

    parser.add_argument(
        "--path",
        type=str,
        default=".",
        help="Path to the repository root (default: current directory)",
    )
    parser.add_argument(
        "--repo-id",
        type=str,
        required=True,
        help="Unique identifier for the repository (for example, 'my-org/backend-api')",
    )
    parser.add_argument(
        "--standards-path",
        type=str,
        default=str(STANDARDS_DIR),
        help="Path to the directory containing markdown coding standards",
    )

    args = parser.parse_args()

    repo_path = os.path.abspath(args.path)
    standards_path = os.path.abspath(args.standards_path)
    repo_id = args.repo_id

    print(f"Starting RAG indexing for repository: {repo_id}")
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Code path: {repo_path}")
    print(f"Standards path: {standards_path}\n")

    print("Indexing source code...")
    try:
        code_retriever = CodeRetriever()
        code_retriever.index_repository(path=repo_path, repo_id=repo_id)
    except Exception as exc:
        print(f"Failed to index code: {exc}")
        sys.exit(1)

    print("\nIndexing coding standards...")
    try:
        standards_retriever = StandardsRetriever()
        standards_retriever.index_standards(path=standards_path, repo_id=repo_id)
    except Exception as exc:
        print(f"Failed to index standards: {exc}")
        sys.exit(1)

    print("\nIndexing complete. The vector database is ready for reviews.")


if __name__ == "__main__":
    main()
