import unittest

from src.core.models import DiffChunk
from src.core.processors import build_added_line_lookup, chunk_diffs


class ChunkDiffsTests(unittest.TestCase):
    def test_chunk_diffs_parses_added_context_and_removed_lines(self):
        files = [
            {
                "filename": "src/example.py",
                "patch": """@@ -10,3 +10,4 @@
 context_before
-old_value = call_old()
+new_value = call_new()
 context_after
""",
            }
        ]

        chunks = chunk_diffs(files)

        self.assertEqual(1, len(chunks))
        chunk = chunks[0]
        self.assertIsInstance(chunk, DiffChunk)
        self.assertEqual("src/example.py", chunk.file_path)
        self.assertEqual([11], [line.new_line_number for line in chunk.added_lines])
        self.assertEqual(
            ["context_before", "context_after"],
            [line.content for line in chunk.context_lines],
        )

    def test_build_added_line_lookup_collects_added_lines_per_file(self):
        files = [
            {
                "filename": "src/example.py",
                "patch": """@@ -1,2 +1,3 @@
+line_one
+line_two
 context_line
""",
            }
        ]

        chunks = chunk_diffs(files)
        lookup = build_added_line_lookup(chunks)

        self.assertEqual({"src/example.py": {1, 2}}, lookup)


if __name__ == "__main__":
    unittest.main()
