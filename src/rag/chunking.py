from __future__ import annotations

from pathlib import Path
import re

from langchain_core.documents import Document


SUPPORTED_CODE_SUFFIXES = {".py", ".ts", ".tsx", ".js", ".cs"}
EXCLUDED_DIRECTORIES = {
    "node_modules",
    "dist",
    "build",
    ".git",
    "venv",
    "__pycache__",
}


def build_chunked_documents(
    *,
    source: str,
    content: str,
    lang: str,
    repo_id: str,
    chunk_size_lines: int,
    chunk_overlap_lines: int,
    max_chunks_per_file: int,
) -> list[Document]:
    lines = content.splitlines()
    if not lines:
        return [
            build_document(
                source=source,
                content=content,
                lang=lang,
                repo_id=repo_id,
                start_line=1,
                end_line=1,
                chunk_kind="file",
                chunk_index=0,
            )
        ]

    stride = max(chunk_size_lines - chunk_overlap_lines, 1)
    documents: list[Document] = []
    chunk_index = 0

    for start in range(0, len(lines), stride):
        if chunk_index >= max_chunks_per_file:
            break

        end = min(start + chunk_size_lines, len(lines))
        chunk_lines = lines[start:end]
        chunk_content = "\n".join(chunk_lines).strip()
        if not chunk_content:
            continue

        documents.append(
            build_document(
                source=source,
                content=chunk_content,
                lang=lang,
                repo_id=repo_id,
                start_line=start + 1,
                end_line=end,
                chunk_kind="chunk" if len(lines) > chunk_size_lines else "file",
                chunk_index=chunk_index,
            )
        )
        chunk_index += 1

        if end >= len(lines):
            break

    return documents


def build_document(
    *,
    source: str,
    content: str,
    lang: str,
    repo_id: str,
    start_line: int,
    end_line: int,
    chunk_kind: str,
    chunk_index: int,
) -> Document:
    return Document(
        page_content=content,
        metadata={
            "source": source,
            "lang": lang,
            "repo_id": repo_id,
            "chunk_kind": chunk_kind,
            "chunk_index": chunk_index,
            "start_line": start_line,
            "end_line": end_line,
            "symbol": Path(source).stem,
        },
    )


def load_supported_source_files(root_path: str) -> list[Document]:
    root = Path(root_path)
    documents: list[Document] = []

    for file_path in root.rglob("*"):
        if not file_path.is_file():
            continue
        if file_path.suffix.lower() not in SUPPORTED_CODE_SUFFIXES:
            continue
        if any(part in EXCLUDED_DIRECTORIES for part in file_path.parts):
            continue

        documents.append(
            Document(
                page_content=file_path.read_text(encoding="utf-8"),
                metadata={"source": str(file_path)},
            )
        )

    return documents


def overlaps_changed_lines(metadata: dict, changed_lines: list[int]) -> bool:
    start_line = int(metadata.get("start_line", 0))
    end_line = int(metadata.get("end_line", 0))
    return any(start_line <= line <= end_line for line in changed_lines)


def score_same_file_chunk(metadata: dict, changed_lines: list[int]) -> int:
    score = 0
    if overlaps_changed_lines(metadata, changed_lines):
        score += 100

    start_line = int(metadata.get("start_line", 0))
    end_line = int(metadata.get("end_line", 0))
    if changed_lines and start_line and end_line:
        mid_point = (start_line + end_line) // 2
        distance = min(abs(mid_point - line) for line in changed_lines)
        score += max(0, 40 - distance)

    if metadata.get("chunk_kind") == "chunk":
        score += 10

    return score


def format_retrieved_document(document: Document) -> str:
    metadata = document.metadata
    source = metadata.get("source", "unknown")
    chunk_kind = metadata.get("chunk_kind", "file")
    start_line = metadata.get("start_line", "?")
    end_line = metadata.get("end_line", "?")
    return f"{source} [{chunk_kind} lines {start_line}-{end_line}]\n{document.page_content}"


def dedupe_documents(documents: list[Document]) -> list[Document]:
    seen: set[tuple[str, int, int, int]] = set()
    deduped: list[Document] = []

    for document in documents:
        metadata = document.metadata
        key = (
            metadata.get("source", ""),
            int(metadata.get("chunk_index", 0)),
            int(metadata.get("start_line", 0)),
            int(metadata.get("end_line", 0)),
        )
        if key in seen:
            continue
        seen.add(key)
        deduped.append(document)

    return deduped


def tokenize_for_retrieval(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[A-Za-z_][A-Za-z0-9_]{2,}", text.lower())
        if token not in STOP_WORDS
    }


def lexical_overlap_score(query_text: str, document_text: str, chunk_kind: str) -> int:
    query_tokens = tokenize_for_retrieval(query_text)
    if not query_tokens:
        return 0

    document_tokens = tokenize_for_retrieval(document_text)
    overlap = len(query_tokens & document_tokens)
    if overlap == 0:
        return 0

    score = overlap
    if chunk_kind == "chunk":
        score += 2
    return score


STOP_WORDS = {
    "the",
    "and",
    "for",
    "with",
    "from",
    "that",
    "this",
    "return",
    "class",
    "true",
    "false",
    "none",
    "line",
    "file",
    "added",
    "code",
    "context",
}
