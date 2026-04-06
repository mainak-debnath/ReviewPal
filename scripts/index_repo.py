import argparse
import os
import sys

# Ensure the 'src' directory is in the Python path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.rag.code_retriever import CodeRetriever
from src.rag.standards_retriever import StandardsRetriever


def main():
    parser = argparse.ArgumentParser(
        description="Index a repository into ChromaDB for AI Code Review RAG."
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
        help="Unique identifier for the repository (e.g., 'my-org/backend-api')",
    )
    parser.add_argument(
        "--standards-path",
        type=str,
        default="./standards",
        help="Path to the directory containing markdown coding standards",
    )

    args = parser.parse_args()

    repo_path = os.path.abspath(args.path)
    standards_path = os.path.abspath(args.standards_path)
    repo_id = args.repo_id

    print(f"Starting RAG Indexing for repository: {repo_id}")
    print(f"Code path: {repo_path}")
    print(f"Standards path: {standards_path}\n")

    # 1. Index the Codebase
    print("Indexing source code...")
    try:
        code_retriever = CodeRetriever()
        code_retriever.index_repository(path=repo_path, repo_id=repo_id)
    except Exception as e:
        print(f"Failed to index code: {e}")
        sys.exit(1)

    # 2. Index the Coding Standards
    print("\nIndexing coding standards...")
    try:
        standards_retriever = StandardsRetriever()
        standards_retriever.index_standards(path=standards_path, repo_id=repo_id)
    except Exception as e:
        print(f"Failed to index standards: {e}")
        sys.exit(1)

    print("\nIndexing complete! The Vector DB is ready for reviews.")


if __name__ == "__main__":
    main()
