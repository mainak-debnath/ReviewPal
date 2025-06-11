import logging
import os
from typing import Dict, List, Optional

import httpx
from dotenv import load_dotenv
from langchain_core.tools import tool
from typing_extensions import TypedDict

# --- Load environment variables ---
load_dotenv()

# --- Setup logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# --- TypedDict for inline comments ---
class Comment(TypedDict):
    path: str
    line: int
    body: str


class GitHubPRReviewer:
    """
    A class to interact with GitHub PR API for code review automation.
    """

    def __init__(self, token: str, repo: str, pr_number: str):
        if not token:
            raise ValueError("TOKEN_GITHUB is not set.")
        if not repo:
            raise ValueError("GITHUB_REPO is not set.")
        if not pr_number:
            raise ValueError("PR_NUMBER is not set.")
        self.token = token
        self.repo = repo
        self.pr_number = pr_number
        self.base_url = (
            f"https://api.github.com/repos/{self.repo}/pulls/{self.pr_number}"
        )

    @property
    def headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
        }

    def fetch_pr_files(self) -> List[Dict[str, str]]:
        """Fetches PR files with their patches."""
        try:
            response = httpx.get(f"{self.base_url}/files", headers=self.headers)
            response.raise_for_status()
            try:
                files = response.json()
                return [
                    {"filename": f["filename"], "patch": f.get("patch", "")}
                    for f in files
                    if f.get("patch")
                ]
            except ValueError:
                logger.error("Failed to parse JSON response while fetching files.")
                return []
        except httpx.RequestError as e:
            logger.error(f"Error fetching PR files: {e}")
            return []

    def post_inline_comments(self, comments: List[Comment]) -> str:
        """Posts a batch of inline comments as a GitHub PR review."""
        if not comments:
            return "No comments to post."

        review_url = (
            f"https://api.github.com/repos/{self.repo}/pulls/{self.pr_number}/reviews"
        )
        review_payload = {
            "body": "AI Code Review",
            "event": "COMMENT",
            "comments": comments,
        }
        try:
            response = httpx.post(review_url, headers=self.headers, json=review_payload)
            response.raise_for_status()
            return "Inline comments posted successfully."
        except httpx.RequestError as e:
            logger.error(f"Failed to post comments: {e}")
            return "Failed to post comments."
        except ValueError:
            logger.error("Error decoding JSON response when posting comments.")
            return "Error decoding JSON response when posting comments."


# --- Lazy Instantiation Helper ---
def get_reviewer() -> Optional[GitHubPRReviewer]:
    try:
        return GitHubPRReviewer(
            os.getenv("TOKEN_GITHUB"), os.getenv("GITHUB_REPO"), os.getenv("PR_NUMBER")
        )
    except ValueError as e:
        logger.error(f"GitHubPRReviewer initialization failed: {e}")
        return None


# --- LangChain Tool Wrappers ---


@tool
def fetch_pr_files_tool() -> List[Dict[str, str]]:
    """
    LangChain tool to fetch PR files and their patches.
    """
    reviewer = get_reviewer()
    if reviewer:
        return reviewer.fetch_pr_files()
    logger.warning("Reviewer not available.")
    return []


@tool
def post_inline_comments_tool(comments: List[Comment]) -> str:
    """
    LangChain tool to post inline review comments to a PR.
    """
    reviewer = get_reviewer()
    if reviewer:
        return reviewer.post_inline_comments(comments)
    return "Reviewer not available. Cannot post comments."


# --- Direct CLI Testing Block ---

if __name__ == "__main__":
    logger.info("--- CLI: Testing GitHubPRReviewer ---")
    reviewer = get_reviewer()
    if reviewer:
        files = reviewer.fetch_pr_files()
        logger.info(
            f"Fetched {len(files)} files from PR."
        ) if files else logger.warning("No files fetched.")

        example_comments: List[Comment] = [
            {"path": "README.md", "line": 1, "body": "Sample test comment."},
            {"path": "README.md", "line": 2, "body": "Another sample comment."},
        ]
        # Uncomment below to actually post to GitHub (be careful!)
        result = reviewer.post_inline_comments(example_comments)
        # logger.info(result)
    else:
        logger.error("GitHubPRReviewer not initialized. Check .env values.")
