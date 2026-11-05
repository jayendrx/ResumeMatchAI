"""Unit tests for PDF report generator."""

import unittest
from src.report_generator import generate_report


class TestReportGenerator(unittest.TestCase):
    """Test PDF report generation."""

    def test_generate_report(self):
        """Test that report generator produces valid PDF bytes."""
        sample_results = {
            "semantic_score": {
                "raw_score": 0.78,
                "percentage": 78.0,
                "interpretation": "Strong alignment with the job description.",
            },
            "skill_comparison": {
                "matched": {"Python", "SQL", "Docker"},
                "missing": {"Kubernetes"},
                "additional": {"Git"},
                "matched_details": [
                    {"skill": "Python", "category": "Programming"},
                    {"skill": "SQL", "category": "Databases"},
                    {"skill": "Docker", "category": "Cloud and DevOps"},
                ],
                "missing_details": [
                    {"skill": "Kubernetes", "category": "Cloud and DevOps"},
                ],
                "additional_details": [
                    {"skill": "Git", "category": "Cloud and DevOps"},
                ],
                "coverage": 0.75,
                "coverage_percentage": "75%",
            },
            "gap_analysis": {
                "strengths": [
                    {"title": "Strong Skill Coverage", "detail": "Matches 3 of 4 skills."}
                ],
                "weaknesses": [
                    {"title": "Missing Kubernetes", "detail": "Kubernetes is missing."}
                ],
                "summary": "Overall good candidate match.",
            },
            "recommendations": [
                {
                    "title": "Add Kubernetes Projects",
                    "explanation": "Role requires container orchestration.",
                    "action": "Highlight any personal or lab experience with Kubernetes.",
                }
            ],
            "roasts": [
                "Your resume is pretty solid, but don't get too cocky!"
            ],
        }

        pdf_bytes = generate_report(sample_results)
        self.assertIsInstance(pdf_bytes, bytes)
        self.assertGreater(len(pdf_bytes), 1000)
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))


if __name__ == "__main__":
    unittest.main()
