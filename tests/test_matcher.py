"""Unit tests for the semantic matcher and text preprocessor."""

import unittest
from src.text_preprocessor import preprocess_text, extract_sections
from src.semantic_matcher import calculate_semantic_similarity, _interpret_score


class TestSemanticMatcher(unittest.TestCase):
    """Test cases for text preprocessor and semantic matching."""

    def test_preprocess_text(self):
        """Test text normalization, URL removal, email removal, and whitespace."""
        raw = "Contact me at john@example.com or visit https://myportfolio.io. Python & Machine Learning!"
        cleaned = preprocess_text(raw)
        self.assertNotIn("john@example.com", cleaned)
        self.assertNotIn("https://myportfolio.io", cleaned)
        self.assertIn("Python", cleaned)
        self.assertIn("Machine Learning", cleaned)

    def test_extract_sections(self):
        """Test extraction of resume sections."""
        resume = """
SUMMARY
Senior Data Scientist with 6 years experience.

EXPERIENCE
Led AI initiatives at TechCorp.

EDUCATION
BS in Computer Science.
        """
        sections = extract_sections(resume)
        self.assertIn("summary", sections)
        self.assertIn("experience", sections)
        self.assertIn("education", sections)
        self.assertIn("TechCorp", sections["experience"])

    def test_interpret_score(self):
        """Test score interpretation strings."""
        self.assertIn("Strong alignment", _interpret_score(80.0))
        self.assertIn("Moderate alignment", _interpret_score(60.0))
        self.assertIn("Partial alignment", _interpret_score(40.0))
        self.assertIn("Low alignment", _interpret_score(20.0))

    def test_empty_semantic_similarity(self):
        """Test semantic similarity with empty inputs."""
        res = calculate_semantic_similarity("", "Some job description")
        self.assertEqual(res["percentage"], 0.0)
        self.assertEqual(res["raw_score"], 0.0)

    def test_semantic_similarity_computation(self):
        """Test semantic similarity computation on real text inputs."""
        text1 = "Senior Machine Learning Engineer specializing in PyTorch and NLP models."
        text2 = "Looking for a Machine Learning Engineer with deep learning and PyTorch experience."
        text3 = "Pastry chef with 10 years of experience baking artisan breads and cakes."

        match_relevant = calculate_semantic_similarity(text1, text2)
        match_irrelevant = calculate_semantic_similarity(text1, text3)

        self.assertGreater(match_relevant["percentage"], match_irrelevant["percentage"])
        self.assertGreater(match_relevant["raw_score"], 0.5)
        self.assertIn("percentage", match_relevant)
        self.assertIn("interpretation", match_relevant)


if __name__ == "__main__":
    unittest.main()
