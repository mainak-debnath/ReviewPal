from __future__ import annotations

from src.core.models import DiffChunk, ReviewComment
from src.core.processors import build_added_line_lookup


def validate_comments(
    comments: list[ReviewComment], chunks: list[DiffChunk], min_confidence: float = 0.0
) -> list[ReviewComment]:
    """
    Validates comments to ensure:
    - Only added lines are commented
    - No duplicates
    - Valid format
    - Confidence clears the configured threshold
    """

    valid: list[ReviewComment] = []
    seen: set[tuple[str, int, str]] = set()
    valid_lines_map = build_added_line_lookup(chunks)

    for comment in comments:
        body = comment.body.strip()
        filename = comment.path
        line_num = comment.line

        if not body:
            continue

        if comment.confidence < min_confidence:
            continue

        if filename not in valid_lines_map:
            print(f"Dropping: File {filename} not in PR.")
            continue

        if line_num not in valid_lines_map[filename]:
            print(f"Dropping: Line {line_num} in {filename} is not an added line.")
            continue

        key = (filename, line_num, body)
        if key in seen:
            continue

        seen.add(key)
        valid.append(comment.model_copy(update={"body": body}))

    return valid
