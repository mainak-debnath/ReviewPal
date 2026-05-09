from __future__ import annotations

import hashlib
import os
from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document

from src.core.config import DB_DIR, load_settings
from src.rag.chunking import (
    build_chunked_documents,
    dedupe_documents,
    format_retrieved_document,
    load_supported_source_files,
    score_same_file_chunk,
)
from src.rag.vector_store import get_embeddings, normalize_lang


def get_content_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


class CodeRetriever:
    def __init__(self):
        self.settings = load_settings()
        self.embeddings = get_embeddings()

        self.db = Chroma(
            persist_directory=str(DB_DIR / "code_db"),
            embedding_function=self.embeddings,
            collection_name="repo_code",
        )

    def index_repository(self, path: str, repo_id: str):
        docs = load_supported_source_files(path)
        seen_sources: set[str] = set()
        docs_to_add: list[Document] = []

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

            chunk_documents = build_chunked_documents(
                source=source,
                content=doc.page_content,
                lang=normalize_lang(ext),
                repo_id=repo_id,
                chunk_size_lines=self.settings.code_chunk_size_lines,
                chunk_overlap_lines=self.settings.code_chunk_overlap_lines,
                max_chunks_per_file=self.settings.max_chunks_per_file,
            )
            for chunk_document in chunk_documents:
                chunk_document.metadata["content_hash"] = content_hash
                docs_to_add.append(chunk_document)

        if docs_to_add:
            self.db.add_documents(docs_to_add)

        self._cleanup_deleted_sources(repo_id, seen_sources)
        added_or_updated = len(docs_to_add)
        print(f"Indexed {added_or_updated} updated/new code documents for {repo_id}")

    def get_relevant_context(
        self,
        query: str,
        file_ext: str,
        repo_id: str,
        k: int = 4,
        file_path: str | None = None,
        changed_lines: list[int] | None = None,
    ) -> str:
        lang = normalize_lang(file_ext)
        results: list[Document] = []

        if file_path:
            results.extend(
                self._get_same_file_context(
                    repo_id=repo_id,
                    file_path=file_path,
                    changed_lines=changed_lines or [],
                )
            )

        results.extend(
            self.db.similarity_search(
                query, k=k, filter={"$and": [{"lang": lang}, {"repo_id": repo_id}]}
            )
        )

        if not results:
            results = self.db.similarity_search(query, k=2, filter={"repo_id": repo_id})

        if not results:
            return "No relevant code context found."

        deduped_results = dedupe_documents(results)
        return "\n---\n".join(
            [format_retrieved_document(doc) for doc in deduped_results[:k]]
        )

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

    def _get_same_file_context(
        self, *, repo_id: str, file_path: str, changed_lines: list[int]
    ) -> list[Document]:
        existing = self.db.get(
            where={"$and": [{"repo_id": repo_id}, {"source": file_path}]},
            include=["documents", "metadatas"],
        )
        ranked_documents: list[tuple[int, Document]] = []

        for content, metadata in zip(
            existing.get("documents", []), existing.get("metadatas", [])
        ):
            ranked_documents.append(
                (
                    score_same_file_chunk(metadata, changed_lines),
                    Document(page_content=content, metadata=metadata),
                )
            )

        ranked_documents.sort(key=lambda item: item[0], reverse=True)
        return [document for _, document in ranked_documents[:2]]


def _normalize_source(root_path: str, source: str) -> str:
    try:
        return str(Path(source).resolve().relative_to(Path(root_path).resolve()))
    except ValueError:
        return source
