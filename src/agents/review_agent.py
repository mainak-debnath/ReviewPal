from __future__ import annotations

import json
import os

from langchain_google_genai import ChatGoogleGenerativeAI

from src.core.config import STANDARDS_DIR, load_settings
from src.core.models import (
    DiffChunk,
    RetrievalContext,
    ReviewComment,
    VerificationDecision,
    coerce_comment_payload,
)
from src.rag.code_retriever import CodeRetriever
from src.rag.standards_retriever import StandardsRetriever


class PRReviewAgent:
    def __init__(self, repo_id: str):
        self.settings = load_settings()
        self.settings.require("gemini_api_key")
        self.llm = self._init_llm()
        self.repo_id = repo_id
        self.instructions = self._load_standards_file("instructions.md")
        self.code_retriever = CodeRetriever()
        self.standards_retriever = StandardsRetriever()

    def _init_llm(self):
        return ChatGoogleGenerativeAI(
            model=self.settings.llm_model,
            temperature=0,
            google_api_key=self.settings.gemini_api_key,
        )

    def _load_standards_file(self, filename: str) -> str:
        path = STANDARDS_DIR / filename
        if not path.exists():
            return ""
        return path.read_text(encoding="utf-8")

    def should_skip_file(self, file_path: str) -> bool:
        skip_ext = [".md", ".css", ".scss", ".txt", ".json", ".yml", ".yaml"]
        normalized = file_path.lower()
        if "/tests/" in normalized or "\\tests\\" in normalized:
            return True
        return any(normalized.endswith(ext) for ext in skip_ext)

    def review_chunk(self, chunk: DiffChunk) -> list[ReviewComment]:
        if self.should_skip_file(chunk.file_path):
            return []

        file_ext = os.path.splitext(chunk.file_path)[1]
        if not chunk.added_lines:
            return []

        retrieval_context = self._build_retrieval_context(chunk, file_ext)
        generated_comments = self._generate_comments(chunk, retrieval_context)
        verified_comments = self._verify_comments(chunk, generated_comments)
        return verified_comments

    def _build_retrieval_context(
        self, chunk: DiffChunk, file_ext: str
    ) -> RetrievalContext:
        query = self._build_query(chunk)
        return RetrievalContext(
            code_context=self.code_retriever.get_relevant_context(
                query,
                file_ext,
                self.repo_id,
                k=self.settings.generation_context_limit,
                file_path=chunk.file_path,
                changed_lines=[
                    line.new_line_number
                    for line in chunk.added_lines
                    if line.new_line_number is not None
                ],
            ),
            standards_context=self.standards_retriever.get_relevant_rules(
                query,
                file_ext,
                self.repo_id,
                k=self.settings.generation_context_limit,
            ),
        )

    def _build_query(self, chunk: DiffChunk) -> str:
        added_lines = "\n".join(line.content for line in chunk.added_lines[:40])
        context_lines = "\n".join(line.content for line in chunk.context_lines[-20:])
        return (
            f"File: {chunk.file_path}\n\nAdded Code:\n{added_lines}\n\n"
            f"Nearby Context:\n{context_lines}"
        )

    def _generate_comments(
        self, chunk: DiffChunk, retrieval_context: RetrievalContext
    ) -> list[ReviewComment]:
        prompt = f"""
You are reviewing a pull request diff for high-signal issues only.

Return JSON only with this shape:
{{
  "comments": [
    {{
      "path": "{chunk.file_path}",
      "line": 123,
      "body": "Explain the issue and suggest a fix.",
      "severity": "low|medium|high",
      "category": "bug|security|performance|maintainability",
      "confidence": 0.0
    }}
  ]
}}

Rules:
- Only comment on newly added lines.
- Skip style nitpicks and low-confidence concerns.
- Comments must be actionable and directly tied to the line.
- Return an empty comments list if there are no worthwhile issues.

Review Instructions:
{self.instructions}

Relevant Code Context:
{retrieval_context.code_context}

Relevant Standards:
{retrieval_context.standards_context}

PR Diff:
{self._format_chunk(chunk)}
"""
        response = self.llm.invoke(prompt)
        return self._parse_comments(response.content)

    def _verify_comments(
        self, chunk: DiffChunk, comments: list[ReviewComment]
    ) -> list[ReviewComment]:
        verified: list[ReviewComment] = []

        for comment in comments:
            target_line = next(
                (
                    line
                    for line in chunk.added_lines
                    if line.new_line_number == comment.line
                ),
                None,
            )
            if target_line is None:
                continue

            decision = self._verify_comment(chunk, target_line.content, comment)
            if not decision.should_keep:
                continue

            verified.append(
                comment.model_copy(
                    update={"confidence": max(comment.confidence, decision.confidence)}
                )
            )

        return verified

    def _verify_comment(
        self, chunk: DiffChunk, line_content: str, comment: ReviewComment
    ) -> VerificationDecision:
        prompt = f"""
You are validating whether a generated review comment is accurate and worth posting.

Return JSON only:
{{
  "should_keep": true,
  "confidence": 0.0,
  "reason": "short reason"
}}

Reject comments that are speculative, low-value, duplicate in spirit, or not clearly supported by the code.

Target file: {chunk.file_path}
Target line: {comment.line}
Target content: {line_content}

Diff:
{self._format_chunk(chunk)}

Generated comment:
{comment.model_dump_json()}
"""
        response = self.llm.invoke(prompt)
        try:
            payload = self._extract_json(response.content)
            return VerificationDecision.model_validate(payload)
        except Exception:
            return VerificationDecision(
                should_keep=False, confidence=0.0, reason="verification_failed"
            )

    def _format_chunk(self, chunk: DiffChunk) -> str:
        formatted_lines = []
        for line in chunk.lines:
            marker = {
                "added": "+",
                "context": " ",
                "removed": "-",
            }[line.line_type]
            rendered_line_number = (
                line.new_line_number
                if line.new_line_number is not None
                else line.old_line_number
            )
            formatted_lines.append(
                f"{marker}{rendered_line_number if rendered_line_number is not None else '?'}: {line.content}"
            )
        return f"{chunk.header}\n" + "\n".join(formatted_lines)

    def _parse_comments(self, content: str) -> list[ReviewComment]:
        try:
            payload = self._extract_json(content)
            return coerce_comment_payload(payload)
        except Exception:
            return []

    def _extract_json(self, content: str):
        cleaned = content.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned.split("```json", 1)[1].rsplit("```", 1)[0].strip()
        elif cleaned.startswith("```"):
            cleaned = cleaned.split("```", 1)[1].rsplit("```", 1)[0].strip()
        return json.loads(cleaned)
