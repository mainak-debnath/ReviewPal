from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field


load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[2]
STANDARDS_DIR = PROJECT_ROOT / "standards"
DB_DIR = PROJECT_ROOT / "db"


class Settings(BaseModel):
    github_repo: str = Field(default_factory=lambda: os.getenv("GITHUB_REPO", ""))
    github_token: str = Field(default_factory=lambda: os.getenv("TOKEN_GITHUB", ""))
    pr_number: str = Field(default_factory=lambda: os.getenv("PR_NUMBER", ""))
    gemini_api_key: str = Field(default_factory=lambda: os.getenv("GEMINI_API_KEY", ""))
    llm_model: str = Field(default_factory=lambda: os.getenv("REVIEW_MODEL", "gemini-2.5-flash"))
    embeddings_model: str = Field(
        default_factory=lambda: os.getenv(
            "EMBEDDINGS_MODEL", "models/gemini-embedding-001"
        )
    )
    max_workers: int = Field(
        default_factory=lambda: int(os.getenv("MAX_REVIEW_WORKERS", "4")), ge=1, le=16
    )
    generation_context_limit: int = Field(
        default_factory=lambda: int(os.getenv("REVIEW_CONTEXT_RESULTS", "4")), ge=1, le=10
    )
    min_comment_confidence: float = Field(
        default_factory=lambda: float(os.getenv("MIN_COMMENT_CONFIDENCE", "0.65")),
        ge=0.0,
        le=1.0,
    )
    code_chunk_size_lines: int = Field(
        default_factory=lambda: int(os.getenv("CODE_CHUNK_SIZE_LINES", "60")),
        ge=10,
        le=400,
    )
    code_chunk_overlap_lines: int = Field(
        default_factory=lambda: int(os.getenv("CODE_CHUNK_OVERLAP_LINES", "12")),
        ge=0,
        le=200,
    )
    max_chunks_per_file: int = Field(
        default_factory=lambda: int(os.getenv("MAX_CHUNKS_PER_FILE", "12")),
        ge=1,
        le=200,
    )

    def require(self, *fields: str) -> None:
        missing = [field for field in fields if not getattr(self, field)]
        if missing:
            raise ValueError(f"Missing required settings: {', '.join(missing)}")


def load_settings() -> Settings:
    return Settings()
