from __future__ import annotations

import hashlib
import os

from langchain_chroma import Chroma

from src.core.config import DB_DIR
from src.rag.vector_store import get_embeddings, normalize_lang


def get_content_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


class StandardsRetriever:
    def __init__(self):
        self.embeddings = get_embeddings()

        self.db = Chroma(
            persist_directory=str(DB_DIR / "standards_db"),
            embedding_function=self.embeddings,
            collection_name="standards",
        )

    def index_standards(self, path: str, repo_id: str):
        if not os.path.exists(path):
            print(f"Standards path '{path}' not found.")
            return

        seen_files = set()
        updated_count = 0

        print(f"Checking standards for repo: {repo_id}")

        for file in os.listdir(path):
            if file.startswith(".") or not file.endswith(".md"):
                continue

            file_path = os.path.join(path, file)
            with open(file_path, "r", encoding="utf-8") as handle:
                content = handle.read()

            content_hash = get_content_hash(content)
            seen_files.add(file)
            existing = self.db.get(where={"repo_id": repo_id, "source": file})

            if existing.get("metadatas"):
                existing_hash = existing["metadatas"][0].get("content_hash")
                if existing_hash == content_hash:
                    continue
                existing_ids = existing.get("ids", [])
                if existing_ids:
                    self.db.delete(ids=existing_ids)

            self.db.add_texts(
                texts=[content],
                metadatas=[
                    {
                        "lang": infer_standard_language(file),
                        "repo_id": repo_id,
                        "source": file,
                        "content_hash": content_hash,
                    }
                ],
            )
            updated_count += 1

        self._cleanup_deleted_files(repo_id, seen_files)
        print(f"Indexed {updated_count} updated/new standard files.")

    def _cleanup_deleted_files(self, repo_id: str, seen_files: set[str]):
        try:
            existing = self.db.get(where={"repo_id": repo_id})
            ids = existing.get("ids", [])
            metadatas = existing.get("metadatas", [])

            stale_ids = [
                item_id
                for item_id, metadata in zip(ids, metadatas)
                if metadata.get("source") not in seen_files
            ]
            if stale_ids:
                self.db.delete(ids=stale_ids)
        except Exception as exc:
            print(f"Cleanup skipped: {exc}")

    def get_relevant_rules(self, query: str, file_ext: str, repo_id: str, k: int = 4):
        lang = normalize_lang(file_ext)

        results = self.db.similarity_search(
            query, k=k, filter={"$and": [{"lang": lang}, {"repo_id": repo_id}]}
        )

        if not results:
            results = self.db.similarity_search(
                query, k=2, filter={"$and": [{"lang": "general"}, {"repo_id": repo_id}]}
            )

        if not results:
            return "No relevant coding standards found."

        return "\n---\n".join([doc.page_content for doc in results])


def infer_standard_language(filename: str) -> str:
    filename_lower = filename.lower()
    if any(token in filename_lower for token in ["angular", "ts", "typescript"]):
        return "typescript"
    if any(token in filename_lower for token in ["csharp", "c#", "cs"]):
        return "csharp"
    if any(token in filename_lower for token in ["python", "py"]):
        return "python"
    return "general"
