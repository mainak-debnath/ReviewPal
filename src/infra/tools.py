from __future__ import annotations

import logging
from typing import Any

import httpx
from langchain_core.tools import tool
from typing_extensions import TypedDict

from src.core.config import load_settings
from src.core.models import ReviewComment


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.WARNING)


class PostedComment(TypedDict):
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
        self.timeout = httpx.Timeout(30.0, connect=10.0)

    @property
    def headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
        }

    def fetch_pr_files(self) -> list[dict[str, Any]]:
        """Fetches PR files with their patches."""
        files: list[dict[str, Any]] = []
        page = 1

        try:
            with httpx.Client(timeout=self.timeout) as client:
                while True:
                    response = client.get(
                        f"{self.base_url}/files",
                        headers=self.headers,
                        params={"page": page, "per_page": 100},
                    )
                    response.raise_for_status()
                    batch = response.json()
                    if not batch:
                        break

                    files.extend(
                        {
                            "filename": item["filename"],
                            "patch": item.get("patch", ""),
                            "status": item.get("status", ""),
                        }
                        for item in batch
                        if item.get("patch")
                    )
                    if len(batch) < 100:
                        break
                    page += 1
        except httpx.HTTPError as exc:
            logger.error("Error fetching PR files: %s", exc)
            return []

        return files

    def post_inline_comments(self, comments: list[ReviewComment]) -> str:
        """Posts a batch of inline comments as a GitHub PR review."""
        if not comments:
            return "No comments to post."

        review_url = (
            f"https://api.github.com/repos/{self.repo}/pulls/{self.pr_number}/reviews"
        )
        review_payload = {
            "body": "AI Code Review",
            "event": "COMMENT",
            "comments": [format_comment_for_github(comment) for comment in comments],
        }
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    review_url, headers=self.headers, json=review_payload
                )
                response.raise_for_status()
            return "Inline comments posted successfully."
        except httpx.HTTPError as exc:
            logger.error("Failed to post comments: %s", exc)
            return "Failed to post comments."


def format_comment_for_github(comment: ReviewComment) -> PostedComment:
    return {
        "path": comment.path,
        "line": comment.line,
        "body": comment.body,
    }


def get_reviewer() -> GitHubPRReviewer | None:
    settings = load_settings()
    try:
        return GitHubPRReviewer(
            settings.github_token, settings.github_repo, settings.pr_number
        )
    except ValueError as exc:
        logger.error("GitHubPRReviewer initialization failed: %s", exc)
        return None


@tool
def fetch_pr_files_tool() -> list[dict[str, Any]]:
    """
    LangChain tool to fetch PR files and their patches.
    """
    reviewer = get_reviewer()
    if reviewer:
        return reviewer.fetch_pr_files()
    logger.warning("Reviewer not available.")
    return []


@tool
def post_inline_comments_tool(comments: list[ReviewComment]) -> str:
    """
    LangChain tool to post inline review comments to a PR.
    """
    reviewer = get_reviewer()
    if reviewer:
        return reviewer.post_inline_comments(comments)
    return "Reviewer not available. Cannot post comments."
