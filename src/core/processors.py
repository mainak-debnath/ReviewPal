from __future__ import annotations

import re

from src.core.models import DiffChunk, DiffLine


HUNK_HEADER_RE = re.compile(
    r"^@@ -(?P<old_start>\d+)(?:,(?P<old_count>\d+))? \+(?P<new_start>\d+)(?:,(?P<new_count>\d+))? @@"
)


def chunk_diffs(files: list[dict]) -> list[DiffChunk]:
    chunks: list[DiffChunk] = []

    for file in files:
        filename = file.get("filename")
        patch = file.get("patch") or ""
        if not filename or not patch:
            continue

        chunks.extend(_parse_patch(filename, patch))

    return chunks


def build_added_line_lookup(chunks: list[DiffChunk]) -> dict[str, set[int]]:
    valid_lines_map: dict[str, set[int]] = {}

    for chunk in chunks:
        valid_lines_map.setdefault(chunk.file_path, set())
        for line in chunk.added_lines:
            if line.new_line_number is not None:
                valid_lines_map[chunk.file_path].add(line.new_line_number)

    return valid_lines_map


def _parse_patch(filename: str, patch: str) -> list[DiffChunk]:
    parsed_chunks: list[DiffChunk] = []
    current_chunk: DiffChunk | None = None
    old_line_number: int | None = None
    new_line_number: int | None = None

    for raw_line in patch.splitlines():
        header_match = HUNK_HEADER_RE.match(raw_line)
        if header_match:
            if current_chunk and current_chunk.added_lines:
                parsed_chunks.append(current_chunk)

            old_line_number = int(header_match.group("old_start"))
            new_line_number = int(header_match.group("new_start"))
            current_chunk = DiffChunk(file_path=filename, header=raw_line, lines=[])
            continue

        if current_chunk is None:
            continue

        if raw_line.startswith("\\"):
            continue

        if raw_line.startswith("+"):
            current_chunk.lines.append(
                DiffLine(
                    new_line_number=new_line_number,
                    old_line_number=None,
                    line_type="added",
                    content=raw_line[1:],
                )
            )
            new_line_number = _increment_line_number(new_line_number)
            continue

        if raw_line.startswith("-"):
            current_chunk.lines.append(
                DiffLine(
                    new_line_number=None,
                    old_line_number=old_line_number,
                    line_type="removed",
                    content=raw_line[1:],
                )
            )
            old_line_number = _increment_line_number(old_line_number)
            continue

        if raw_line.startswith(" "):
            current_chunk.lines.append(
                DiffLine(
                    new_line_number=new_line_number,
                    old_line_number=old_line_number,
                    line_type="context",
                    content=raw_line[1:],
                )
            )
            old_line_number = _increment_line_number(old_line_number)
            new_line_number = _increment_line_number(new_line_number)

    if current_chunk and current_chunk.added_lines:
        parsed_chunks.append(current_chunk)

    return parsed_chunks


def _increment_line_number(value: int | None) -> int | None:
    if value is None:
        return None
    return value + 1
