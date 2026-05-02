from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

from pydantic import BaseModel, Field


LineType = Literal["added", "context", "removed"]


@dataclass(frozen=True)
class DiffLine:
    new_line_number: int | None
    old_line_number: int | None
    line_type: LineType
    content: str


@dataclass(frozen=True)
class DiffChunk:
    file_path: str
    header: str
    lines: list[DiffLine] = field(default_factory=list)

    @property
    def added_lines(self) -> list[DiffLine]:
        return [line for line in self.lines if line.line_type == "added"]

    @property
    def context_lines(self) -> list[DiffLine]:
        return [line for line in self.lines if line.line_type == "context"]


class ReviewComment(BaseModel):
    path: str
    line: int
    body: str = Field(min_length=1)
    severity: Literal["low", "medium", "high"] = "medium"
    category: Literal["bug", "security", "performance", "maintainability"] = (
        "maintainability"
    )
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)


class GeneratedCommentSet(BaseModel):
    comments: list[ReviewComment] = Field(default_factory=list)


class RetrievalContext(BaseModel):
    code_context: str
    standards_context: str


class VerificationDecision(BaseModel):
    should_keep: bool
    confidence: float = Field(ge=0.0, le=1.0)
    reason: str = ""


def coerce_comment_payload(payload: Any) -> list[ReviewComment]:
    if isinstance(payload, dict) and "comments" in payload:
        return GeneratedCommentSet.model_validate(payload).comments
    if isinstance(payload, list):
        return [ReviewComment.model_validate(item) for item in payload]
    return []
