import unittest

from src.core.models import ReviewComment
from src.core.processors import chunk_diffs
from src.core.validator import validate_comments


class ValidateCommentsTests(unittest.TestCase):
    def test_validate_comments_drops_duplicates_invalid_lines_and_low_confidence(self):
        chunks = chunk_diffs(
            [
                {
                    "filename": "src/example.py",
                    "patch": """@@ -1,1 +1,3 @@
+line_one
+line_two
 context_line
""",
                }
            ]
        )
        comments = [
            ReviewComment(
                path="src/example.py",
                line=1,
                body="Possible null handling issue.",
                confidence=0.8,
            ),
            ReviewComment(
                path="src/example.py",
                line=1,
                body="Possible null handling issue.",
                confidence=0.9,
            ),
            ReviewComment(
                path="src/example.py",
                line=3,
                body="This is a context line.",
                confidence=0.9,
            ),
            ReviewComment(
                path="src/example.py",
                line=2,
                body="Low confidence suggestion.",
                confidence=0.3,
            ),
        ]

        valid = validate_comments(comments, chunks, min_confidence=0.65)

        self.assertEqual(1, len(valid))
        self.assertEqual(1, valid[0].line)

    def test_validate_comments_returns_ranked_comments_without_dropping_valid_ones(self):
        chunks = chunk_diffs(
            [
                {
                    "filename": "src/example.py",
                    "patch": """@@ -1,1 +1,4 @@
+line_one
+line_two
+line_three
+line_four
""",
                }
            ]
        )
        comments = [
            ReviewComment(
                path="src/example.py",
                line=1,
                body="Low value maintainability note.",
                confidence=0.95,
                severity="low",
                category="maintainability",
            ),
            ReviewComment(
                path="src/example.py",
                line=2,
                body="Potential payment integrity bug.",
                confidence=0.85,
                severity="high",
                category="bug",
            ),
            ReviewComment(
                path="src/example.py",
                line=3,
                body="Security-sensitive credential handling issue.",
                confidence=0.8,
                severity="high",
                category="security",
            ),
            ReviewComment(
                path="src/example.py",
                line=4,
                body="Another low value maintainability note.",
                confidence=0.7,
                severity="low",
                category="maintainability",
            ),
        ]

        valid = validate_comments(comments, chunks, min_confidence=0.65)

        self.assertEqual(4, len(valid))
        self.assertEqual([2, 3, 1, 4], [comment.line for comment in valid])


if __name__ == "__main__":
    unittest.main()
