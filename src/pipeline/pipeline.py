from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed

from src.agents.review_agent import PRReviewAgent
from src.core.config import load_settings
from src.core.models import ReviewComment
from src.core.processors import chunk_diffs
from src.core.validator import validate_comments
from src.infra.tools import fetch_pr_files_tool, post_inline_comments_tool


class ReviewPipeline:
    def __init__(self):
        self.settings = load_settings()
        self.settings.require("github_repo")
        self.reviewer = PRReviewAgent(repo_id=self.settings.github_repo)

    def run(self):
        print("Starting PR review pipeline...")

        files = fetch_pr_files_tool.invoke({})
        if not files:
            print("No files to review.")
            return

        chunks = chunk_diffs(files)
        if not chunks:
            print("No diff chunks eligible for review.")
            return

        all_comments: list[ReviewComment] = []
        print(f"Processing {len(chunks)} chunks in parallel...")

        with ThreadPoolExecutor(max_workers=self.settings.max_workers) as executor:
            futures = [
                executor.submit(self.reviewer.review_chunk, chunk) for chunk in chunks
            ]

            for future in as_completed(futures):
                try:
                    all_comments.extend(future.result())
                except Exception as exc:
                    print("Error:", exc)

        valid_comments = validate_comments(
            all_comments,
            chunks,
            min_confidence=self.settings.min_comment_confidence,
        )

        result = post_inline_comments_tool.invoke({"comments": valid_comments})
        print("Review completed:", result)


if __name__ == "__main__":
    ReviewPipeline().run()
