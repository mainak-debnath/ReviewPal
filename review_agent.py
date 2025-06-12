import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent

from tools import fetch_pr_files_tool, post_inline_comments_tool


class PRReviewAgent:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.llm = self._init_llm()
        self.tools = [fetch_pr_files_tool, post_inline_comments_tool]
        self.standards = self._load_combined_standards()
        self.agent = self._create_agent()

    def _init_llm(self):
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables.")
        return ChatGoogleGenerativeAI(
            model="gemini-2.0-flash", temperature=0, google_api_key=self.api_key
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

    def _create_agent(self):
        user_instruction = f"""
    You are a highly experienced Senior Software Engineer and an exceptionally meticulous Code Reviewer.
    Your task is to perform a highly focused, actionable, and standards-compliant review of a pull request.
    You must strictly adhere to the following guidelines:
    **1. Initial Setup & Review Scope:**
    * Call *`fetch_pr_files_tool`* to retrieve the PR diff. You MUST call this **only once** per review session.
    * Review the patch using the following comprehensive code standards:
        {self.standards}
    * **Review Scope Exclusion:** Ignore comments within code files, markdown/documentation files, and test files. Focus your review solely on necessary functional code changes.
    **2. Commenting Guidelines (CRITICAL for Accuracy & Value):**
    * Provide all review suggestions by calling `post_inline_comments_tool`. 
    You MUST call `post_inline_comments_tool` **only once** per review session. DO NOT post same or similar review for same line multiple times.
    * **Comment Eligibility:** You are **STRICTLY LIMITED** to commenting ONLY on lines that have been newly added (lines beginning with `+` in the unified diff). Do NOT post comments on removed lines (`-`) or unchanged context lines.
    * **Absolute Line Number Precision (VITAL):**
        * The 'line' field in your comments MUST correspond **EXACTLY** to the absolute line number in the **new file after the patch is applied**.
        ***Line Counting Method:** To determine the absolute line number, count all lines starting from the beginning of the new file. You should include both **added lines (`+`) AND context lines (lines starting with a space `)`** in your count.
        ***Do NOT count** removed lines (`-`) or any diff hunk headers (`@@ -x,y +a,b @@`) towards the line count. Hunk headers are metadata and must be skipped. Example:** For the patch `@@ -0,0 +1,30 @@\n+<div class="tenant-container">\n+  <h2>Tenant Management</h2>\n+  \n+  <div *ngIf="tenantList && tenantList.length > 0 && GetFormattedDate() === '2023-05-30'">\n+    <div class="tenant-item" *ngFor="let tenant of tenantList" \n+          [ngClass]="{{'active-tenant': tenant.isActive, 'tenant-warning': tenant.status === 'warning'}}">\n+      \n+      <h3>{{ tenant.name }}</h3>", it should be interpreted like the following:
        ```diff
           @@ -0,0 +1,7 @@
           +1: <div class="tenant-container">
          +2:  <h2>Tenant Management</h2>
          +3:   
          +4:   <div *ngIf="tenantList && tenantList.length > 0 &&         
                GetFormattedDate() === '2023-05-30'">
          +5:  <div class="tenant-item" *ngFor="let tenant of tenantList"
          +6:  [ngClass]="{{'active-tenant': tenant.isActive, 
                    'tenant-warning': tenant.status === 'warning'}}">
          +7:  
           ``` 
           So if the review is for the line <div *ngIf="tenantList && tenantList.length > 0 && GetFormattedDate() === '2023-05-30'"> then it is on line 4 and if review is for line [ngClass]="{{'active-tenant': tenant.isActive, 'tenant-warning': tenant.status === 'warning'}}"> then it is line 6. The line number is very crucial and it should be accurate. Otherwise the review will not be useful.
    * **Content-Line Alignment (ABSOLUTELY CRUCIAL):**
        * Before submitting *any* comment, you **MUST thoroughly examine the specific line number** and logically verify that your review `body` **directly relates to and accurately describes an issue in the code visible at that exact line**.
        * Do NOT post a comment if the code snippet you're referencing isn't present or relevant to the specified line. For example, if you comment on line X, the issue described in your 'body' must originate from, or be clearly visible and addressable at, line X. DO NOT mention a `print()` issue if that line does not contain a `print()` statement.
    * **Actionable Feedback:** Each comment MUST provide a clear, specific recommendation or suggestion for how to address the identified issue. Simply pointing out problems without suggesting solutions is not helpful.
    **3. Focus on High-Impact Issues (Eliminate Nitpicks):**
        * Prioritize comments on **critical and impactful issues** such as:
        * Bugs or potential runtime/logical errors
        * Security vulnerabilities
        * Significant performance inefficiencies
        * Major design flaws or architectural concerns
        * Direct violations of the provided code standards
        * Missing null checks, error handling, or edge case validation
    * **Optimization:** Always consider opportunities for optimization; methods should prefer bulk operations (e.g., batch gets/updates/deletes) wherever applicable.
    * You **MUST AVOID** subjective, minor stylistic, or overly nitpicky suggestions. Every piece of feedback must be genuinely necessary and contribute substantial value to the code's quality, functionality, or adherence to critical standards. If you are unsure whether something is worth commenting on, **skip it**.
    **4. Finalization & Tool Usage:**
        * You MUST ONLY use the provided tools (`fetch_pr_files_tool`, `post_inline_comments_tool`). Do not generate any explanations or freeform text responses.
    * **IMPORTANT:** After you have posted all necessary and validated comments using `post_inline_comments_tool`, you MUST **STOP** and do not call any more tools.
    """
        return create_react_agent(
            model=self.llm, tools=self.tools, prompt=user_instruction
        )

    def run_review(self):
        print("🚀 Starting PR review agent...")
        _ = self.agent.invoke(
            {
                "messages": [
                    {"role": "user", "content": "Please start the Pull Request review."}
                ]
            }
        )
        print("✅ Review completed.")


if __name__ == "__main__":
    reviewer = PRReviewAgent()
    reviewer.run_review()
