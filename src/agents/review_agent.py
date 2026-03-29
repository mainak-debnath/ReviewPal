import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# from langgraph.prebuilt import create_react_agent
from src.infra.tools import fetch_pr_files_tool, post_inline_comments_tool


class PRReviewAgent:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.llm = self._init_llm()
        self.tools = [fetch_pr_files_tool, post_inline_comments_tool]
        self.standards = self._load_combined_standards()
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

    def review_diff(self, file, diff_chunk):
        formatted_diff = "\n".join(
            f"{l['ln']}: {l['content']}"
            if l["type"] == "context"
            else f"{l['ln']}: + {l['content']}"
            for l in diff_chunk
        )
        prompt = f"""
        Review this code diff chunk.
        Follow {self._load_standards_file("instructions.md")}
        Review ONLY lines marked with '+'.

        File: {file}
        Diff:
        {formatted_diff}

        Follow all review rules:
        {self.standards}

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
