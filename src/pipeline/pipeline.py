from concurrent.futures import ThreadPoolExecutor, as_completed

from src.agents.review_agent import PRReviewAgent
from src.core.processors import chunk_diffs
from src.core.validator import validate_comments
from src.infra.tools import fetch_pr_files_tool, post_inline_comments_tool


class ReviewPipeline:
    def __init__(self):
        self.reviewer = PRReviewAgent()

    def run(self):
        print("🚀 Starting PR review pipeline...")

        # Step 1: Fetch PR files
        files = fetch_pr_files_tool.invoke({})
        if not files:
            print("No files to review.")
            return

        # Step 2: Chunk diffs
        chunks = chunk_diffs(files)

        all_comments = []

        # Step 3: Review each chunk
        print(f"🧵 Processing {len(chunks)} chunks in parallel...")

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(
                    self.reviewer.review_diff, chunk["file"], chunk["lines"]
                )
                for chunk in chunks
            ]

            for future in as_completed(futures):
                try:
                    all_comments.extend(future.result())
                except Exception as e:
                    print("❌ Error:", e)

        # Step 4: Validate comments
        valid_comments = validate_comments(all_comments, chunks)

        # Step 5: Post comments
        result = post_inline_comments_tool.invoke({"comments": valid_comments})

        print("✅ Review completed:", result)


if __name__ == "__main__":
    ReviewPipeline().run()
