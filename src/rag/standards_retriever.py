import hashlib
import os

from langchain_chroma import Chroma

from rag.vector_store import get_embeddings, normalize_lang


def get_content_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


class StandardsRetriever:
    def __init__(self):
        self.embeddings = get_embeddings()

        self.db = Chroma(
            persist_directory="./db/standards_db",
            embedding_function=self.embeddings,
            collection_name="standards",
        )

    def index_standards(self, path: str, repo_id: str):
        if not os.path.exists(path):
            print(f"⚠️ Standards path '{path}' not found.")
            return

        docs_to_add = []
        seen_files = set()

        print(f"🔍 Checking standards for repo: {repo_id}")

        for file in os.listdir(path):
            if file.startswith(".") or not file.endswith(".md"):
                continue

            file_path = os.path.join(path, file)

            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            content_hash = get_content_hash(content)
            seen_files.add(file)

            # Check existing doc in DB
            existing = self.db.get(where={"repo_id": repo_id, "source": file})

            if existing["metadatas"]:
                existing_hash = existing["metadatas"][0].get("content_hash")

                if existing_hash == content_hash:
                    # ✅ Skip unchanged
                    continue

                # 🔥 Delete outdated version
                self.db.delete(where={"repo_id": repo_id, "source": file})

            # Language inference
            filename_lower = file.lower()
            if any(x in filename_lower for x in ["angular", "ts", "typescript"]):
                lang = "typescript"
            elif any(x in filename_lower for x in ["csharp", "cs"]):
                lang = "csharp"
            elif any(x in filename_lower for x in ["python", "py"]):
                lang = "python"
            else:
                lang = "general"

            docs_to_add.append(
                {
                    "content": content,
                    "metadata": {
                        "lang": lang,
                        "repo_id": repo_id,
                        "source": file,
                        "content_hash": content_hash,
                    },
                }
            )

        # Batch insert
        if docs_to_add:
            self.db.add_texts(
                texts=[d["content"] for d in docs_to_add],
                metadatas=[d["metadata"] for d in docs_to_add],
            )
            print(f"✅ Indexed {len(docs_to_add)} updated/new standard files.")
        else:
            print("✅ No changes detected in standards.")

        self._cleanup_deleted_files(repo_id, seen_files)

    def _cleanup_deleted_files(self, repo_id: str, seen_files: set):
        """
        Removes documents from DB that no longer exist in filesystem.
        """
        try:
            existing = self.db.get(where={"repo_id": repo_id})

            for meta in existing.get("metadatas", []):
                source = meta.get("source")
                if source and source not in seen_files:
                    self.db.delete(where={"repo_id": repo_id, "source": source})
                    print(f"🧹 Removed deleted standard: {source}")

        except Exception as e:
            print(f"⚠️ Cleanup skipped: {e}")

    def get_relevant_rules(self, query: str, file_ext: str, repo_id: str):
        """
        Retrieves rules filtered by language AND repo_id.
        """
        lang = normalize_lang(file_ext)

        results = self.db.similarity_search(
            query, k=3, filter={"$and": [{"lang": lang}, {"repo_id": repo_id}]}
        )

        # Fallback to general rules
        if not results:
            results = self.db.similarity_search(
                query, k=2, filter={"$and": [{"lang": "general"}, {"repo_id": repo_id}]}
            )

        if not results:
            return "No relevant coding standards found."

        return "\n---\n".join([doc.page_content for doc in results])
