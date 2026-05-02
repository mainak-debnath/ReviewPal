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


if __name__ == "__main__":
    unittest.main()
