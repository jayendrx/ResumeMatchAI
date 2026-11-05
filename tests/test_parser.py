"""Unit tests for the resume parser module."""

import unittest
from io import BytesIO
from src.resume_parser import extract_resume_text, _clean_extracted_text


class TestResumeParser(unittest.TestCase):
    """Test cases for PDF resume parsing and cleaning."""

    def test_clean_extracted_text(self):
        """Test unicode replacement, whitespace normalization, and cleaning."""
        raw = "Hello \u2019world\u2018  \u201cquotes\u201d \u2022 bullet item\n\n\n\nNew paragraph"
        cleaned = _clean_extracted_text(raw)
        self.assertIn("Hello 'world' \"quotes\" - bullet item", cleaned)
        self.assertNotIn("\n\n\n", cleaned)

    def test_extract_invalid_pdf(self):
        """Test handling of invalid/corrupted PDF bytes."""
        corrupted_bytes = b"This is not a PDF file content."
        result = extract_resume_text(corrupted_bytes)
        self.assertFalse(result["success"])
        self.assertIn("Failed to read the PDF file", result["error"])

    def test_extract_empty_pdf(self):
        """Test handling of empty bytes."""
        empty_bytes = b""
        result = extract_resume_text(empty_bytes)
        self.assertFalse(result["success"])


if __name__ == "__main__":
    unittest.main()
