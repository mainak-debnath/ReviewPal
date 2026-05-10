import unittest

from src.rag.chunking import lexical_overlap_score, tokenize_for_retrieval


class RetrievalHelperTests(unittest.TestCase):
    def test_tokenize_for_retrieval_keeps_meaningful_identifiers(self):
        tokens = tokenize_for_retrieval(
            "customer_id = payload['customer']['id']; return customer_id"
        )

        self.assertIn("customer_id", tokens)
        self.assertIn("payload", tokens)
        self.assertNotIn("return", tokens)

    def test_lexical_overlap_score_prefers_documents_with_more_term_overlap(self):
        close_score = lexical_overlap_score(
            query_text="customer payload id validation",
            document_text="customer_id = payload['customer']['id']",
            chunk_kind="chunk",
        )
        far_score = lexical_overlap_score(
            query_text="customer payload id validation",
            document_text="total_amount = pricing_service.calculate_total(subtotal, discount)",
            chunk_kind="chunk",
        )

        self.assertGreater(close_score, far_score)
        self.assertGreater(close_score, 0)


if __name__ == "__main__":
    unittest.main()
