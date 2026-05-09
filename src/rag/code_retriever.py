from __future__ import annotations

import hashlib
import os
from pathlib import Path

from langchain_chroma import Chroma
from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.parsers import LanguageParser

from src.core.config import DB_DIR
from src.rag.vector_store import get_embeddings, normalize_lang


def get_content_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


class CodeRetriever:
    def __init__(self):
        self.embeddings = get_embeddings()

        self.db = Chroma(
            persist_directory=str(DB_DIR / "code_db"),
            embedding_function=self.embeddings,
            collection_name="repo_code",
        )

    def index_repository(self, path: str, repo_id: str):
        exclude_patterns = [
            "**/node_modules/**",
            "**/dist/**",
            "**/build/**",
            "**/.git/**",
            "**/venv/**",
            "**/__pycache__/**",
        ]
        loader = GenericLoader.from_filesystem(
            path,
            glob="**/*",
            suffixes=[".py", ".ts", ".tsx", ".js", ".cs"],
            exclude=exclude_patterns,
            parser=LanguageParser(),
        )

        docs = loader.load()
        seen_sources: set[str] = set()
        added_or_updated = 0

        for doc in docs:
            source = _normalize_source(path, doc.metadata["source"])
            seen_sources.add(source)
            ext = os.path.splitext(source)[1]
            content_hash = get_content_hash(doc.page_content)
            existing = self.db.get(
                where={"$and": [{"repo_id": repo_id}, {"source": source}]}
            )

            if existing.get("metadatas"):
                existing_hash = existing["metadatas"][0].get("content_hash")
                if existing_hash == content_hash:
                    continue
                existing_ids = existing.get("ids", [])
                if existing_ids:
                    self.db.delete(ids=existing_ids)

            doc.metadata["source"] = source
            doc.metadata["lang"] = normalize_lang(ext)
            doc.metadata["repo_id"] = repo_id
            doc.metadata["content_hash"] = content_hash
            self.db.add_documents([doc])
            added_or_updated += 1

        self._cleanup_deleted_sources(repo_id, seen_sources)
        print(f"Indexed {added_or_updated} updated/new code documents for {repo_id}")

    def get_relevant_context(self, query: str, file_ext: str, repo_id: str, k: int = 4):
        lang = normalize_lang(file_ext)

        results = self.db.similarity_search(
            query, k=k, filter={"$and": [{"lang": lang}, {"repo_id": repo_id}]}
        )

        if not results:
            results = self.db.similarity_search(query, k=2, filter={"repo_id": repo_id})

        if not results:
            return "No relevant code context found."

        return "\n---\n".join([doc.page_content for doc in results])

    def _cleanup_deleted_sources(self, repo_id: str, seen_sources: set[str]) -> None:
        existing = self.db.get(where={"repo_id": repo_id})
        ids = existing.get("ids", [])
        metadatas = existing.get("metadatas", [])

        stale_ids = [
            item_id
            for item_id, metadata in zip(ids, metadatas)
            if metadata.get("source") not in seen_sources
        ]
        if stale_ids:
            self.db.delete(ids=stale_ids)


def _normalize_source(root_path: str, source: str) -> str:
    try:
        return str(Path(source).resolve().relative_to(Path(root_path).resolve()))
    except ValueError:
        return source
