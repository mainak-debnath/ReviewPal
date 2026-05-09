from __future__ import annotations

from langchain_google_genai import GoogleGenerativeAIEmbeddings

from src.core.config import load_settings


def normalize_lang(ext: str) -> str:
    mapping = {
        ".py": "python",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".js": "javascript",
        ".cs": "csharp",
    }
    return mapping.get(ext.lower(), "general")


def get_embeddings():
    settings = load_settings()
    settings.require("gemini_api_key")
    return GoogleGenerativeAIEmbeddings(
        model=settings.embeddings_model,
        google_api_key=settings.gemini_api_key,
    )
