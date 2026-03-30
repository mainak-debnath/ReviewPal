import os

from langchain_google_genai import GoogleGenerativeAIEmbeddings


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
    return GoogleGenerativeAIEmbeddings(model="models/embedding-001")
