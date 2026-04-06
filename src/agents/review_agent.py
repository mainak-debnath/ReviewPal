import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# from langgraph.prebuilt import create_react_agent
from src.infra.tools import fetch_pr_files_tool, post_inline_comments_tool
from src.rag.code_retriever import CodeRetriever
from src.rag.standards_retriever import StandardsRetriever


class PRReviewAgent:
    def __init__(self, repo_id: str):
        load_dotenv()
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.llm = self._init_llm()
        self.tools = [fetch_pr_files_tool, post_inline_comments_tool]
        self.standards = self._load_combined_standards()
        self.code_retriever = CodeRetriever()
        self.standards_retriever = StandardsRetriever()
        self.repo_id = repo_id
        # self.agent = self._create_agent()

    def _init_llm(self):
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables.")
        return ChatGoogleGenerativeAI(
            model="gemini-2.5-flash", temperature=0, google_api_key=self.api_key
        )

    def _load_standards_file(self, filename: str) -> str:
        try:
            with open(filename, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            return ""

    def _load_combined_standards(self) -> str:
        clean_code = self._load_standards_file("clean_code_standards.md")
        angular_code = self._load_standards_file("angular_code_standards.md")
        csharp_code = self._load_standards_file("csharp_code_standards.md")
        return f"{clean_code}\n\n{angular_code}\n\n{csharp_code}"

    def should_skip_file(self, file_path: str) -> bool:
        skip_ext = [".md", ".css", ".scss", ".txt"]

        if any(file_path.endswith(ext) for ext in skip_ext):
            return True

        return False

    # def _create_agent(self):
    #     user_instruction = self._load_standards_file("instructions.md")
    #     return create_react_agent(
    #         model=self.llm, tools=self.tools, prompt=user_instruction
    #     )

    # def run_review(self):
    #     print("🚀 Starting PR review agent...")
    #     _ = self.agent.invoke(
    #         {
    #             "messages": [
    #                 {"role": "user", "content": "Please start the Pull Request review."}
    #             ]
    #         }
    #     )
    #     print("✅ Review completed.")

    def review_diff(self, file_path, diff_lines):
        if self.should_skip_file(file_path):
            return []
        file_ext = os.path.splitext(file_path)[1]

        # Extract added + context lines
        added_lines = [
            line["content"] for line in diff_lines if line["type"] == "added"
        ]

        context_lines = [
            line["content"] for line in diff_lines if line["type"] == "context"
        ]

        # If no meaningful code changes → skip
        if not added_lines:
            return []
        query = f"""
        File: {file_path}

        Added Code:
        {" ".join(added_lines)}

        Context:
        {" ".join(context_lines)}
        """
        relevant_code = self.code_retriever.get_relevant_context(
            query, file_ext, self.repo_id
        )
        relevant_rules = self.standards_retriever.get_relevant_rules(
            query, file_ext, self.repo_id
        )

        # Format diff
        formatted_diff = "\n".join(
            f"{line['ln']}: {line['content']}" for line in diff_lines
        )

        prompt = f"""
        Review this code diff chunk.
        Follow {self._load_standards_file("instructions.md")}
        Review ONLY lines marked with '+'.

        [RELEVANT CODE CONTEXT]
        {relevant_code}

        [RELEVANT CODING STANDARDS]
        {relevant_rules}

        [PR DIFF]
        File: {file_path}
        {formatted_diff}

        Instructions:
        - Review ONLY added lines
        - Do NOT comment on unchanged lines
        - Do NOT hallucinate issues
        - If no issues, return []

        Return JSON:
        [
            {{
                "path": "...",
                "line": int,
                "body": "..."
            }}
        ]
        """

        response = self.llm.invoke(prompt)

        import json

        try:
            content = response.content

            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]

            return json.loads(content)
        except:
            return []


# if __name__ == "__main__":
#     reviewer = PRReviewAgent()
#     reviewer.run_review()
