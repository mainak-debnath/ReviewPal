import os

from langchain_chroma import Chroma
from langchain_community.document_loaders.generic import GenericLoader
from langchain_community.document_loaders.parsers import LanguageParser

from src.rag.vector_store import get_embeddings, normalize_lang


class CodeRetriever:
    def __init__(self):
        self.embeddings = get_embeddings()

        self.db = Chroma(
            persist_directory="./db/code_db",
            embedding_function=self.embeddings,
            collection_name="repo_code",
        )

    def index_repository(self, path: str, repo_id: str):
        print(f"Cleaning up old indices for {repo_id}...")
        self.db.delete(where={"repo_id": repo_id})

        exclude_patterns = [
            "**/node_modules/**",
            "**/dist/**",
            "**/build/**",
            "**/.git/**",
        ]
        loader = GenericLoader.from_filesystem(
            path,
            glob="**/*",
            suffixes=[".py", ".ts", ".tsx", ".js", ".cs"],
            exclude=exclude_patterns,
            parser=LanguageParser(),
        )

        docs = loader.load()

        for doc in docs:
            ext = os.path.splitext(doc.metadata["source"])[1]
            doc.metadata["lang"] = normalize_lang(ext)
            doc.metadata["repo_id"] = repo_id
        self.db.add_documents(docs)
        print(f"Indexed {len(docs)} code chunks for {repo_id}")

    def get_relevant_context(self, query: str, file_ext: str, repo_id: str):
        lang = normalize_lang(file_ext)

        results = self.db.similarity_search(
            query, k=3, filter={"lang": lang, "repo_id": repo_id}
        )

        if not results:
            return "No relevant code context found."

        return "\n---\n".join([doc.page_content for doc in results])
