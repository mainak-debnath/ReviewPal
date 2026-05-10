import unittest

from src.rag.indexing import batched, is_rate_limit_exception


class IndexingHelperTests(unittest.TestCase):
    def test_batched_splits_items_into_configurable_chunks(self):
        items = list(range(7))

        result = batched(items, 3)

        self.assertEqual([[0, 1, 2], [3, 4, 5], [6]], result)

    def test_batched_requires_positive_batch_size(self):
        with self.assertRaises(ValueError):
            batched([1, 2], 0)

    def test_is_rate_limit_exception_detects_common_provider_messages(self):
        self.assertTrue(is_rate_limit_exception(Exception("429 Too Many Requests")))
        self.assertTrue(is_rate_limit_exception(Exception("Resource exhausted for quota")))
        self.assertTrue(is_rate_limit_exception(Exception("Rate limit exceeded")))
        self.assertFalse(is_rate_limit_exception(Exception("connection reset by peer")))


if __name__ == "__main__":
    unittest.main()
