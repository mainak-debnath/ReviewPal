import unittest

from langchain_core.documents import Document

from src.rag.chunking import (
    build_chunked_documents,
    dedupe_documents,
    overlaps_changed_lines,
    score_same_file_chunk,
)


class ChunkingTests(unittest.TestCase):
    def test_build_chunked_documents_splits_large_files_with_overlap(self):
        content = "\n".join([f"line_{index}" for index in range(1, 11)])

        documents = build_chunked_documents(
            source="src/example.py",
            content=content,
            lang="python",
            repo_id="demo/repo",
            chunk_size_lines=4,
            chunk_overlap_lines=1,
            max_chunks_per_file=10,
        )

        self.assertEqual(3, len(documents))
        self.assertEqual((1, 4), (documents[0].metadata["start_line"], documents[0].metadata["end_line"]))
        self.assertEqual((4, 7), (documents[1].metadata["start_line"], documents[1].metadata["end_line"]))
        self.assertEqual((7, 10), (documents[2].metadata["start_line"], documents[2].metadata["end_line"]))

    def test_build_chunked_documents_respects_max_chunks_per_file(self):
        content = "\n".join([f"line_{index}" for index in range(1, 31)])

        documents = build_chunked_documents(
            source="src/example.py",
            content=content,
            lang="python",
            repo_id="demo/repo",
            chunk_size_lines=5,
            chunk_overlap_lines=1,
            max_chunks_per_file=2,
        )

        self.assertEqual(2, len(documents))

    def test_score_same_file_chunk_prefers_overlapping_ranges(self):
        overlapping = {
            "start_line": 10,
            "end_line": 20,
            "chunk_kind": "chunk",
        }
        far_away = {
            "start_line": 80,
            "end_line": 100,
            "chunk_kind": "chunk",
        }

        self.assertTrue(overlaps_changed_lines(overlapping, [12, 13]))
        self.assertGreater(
            score_same_file_chunk(overlapping, [12, 13]),
            score_same_file_chunk(far_away, [12, 13]),
        )

    def test_dedupe_documents_removes_same_chunk_duplicates(self):
        documents = [
            Document(
                page_content="a",
                metadata={
                    "source": "src/example.py",
                    "chunk_index": 0,
                    "start_line": 1,
                    "end_line": 10,
                },
            ),
            Document(
                page_content="a",
                metadata={
                    "source": "src/example.py",
                    "chunk_index": 0,
                    "start_line": 1,
                    "end_line": 10,
                },
            ),
        ]

        deduped = dedupe_documents(documents)

        self.assertEqual(1, len(deduped))


if __name__ == "__main__":
    unittest.main()
