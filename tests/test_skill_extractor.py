"""Unit tests for the skill extractor module."""

import unittest
from src.skill_extractor import extract_skills, compare_skills, load_taxonomy, _match_skill


class TestSkillExtractor(unittest.TestCase):
    """Test cases for skill extraction and matching."""

    @classmethod
    def setUpClass(cls):
        cls.taxonomy = load_taxonomy()

    def test_load_taxonomy(self):
        """Test taxonomy loads properly with expected categories."""
        self.assertIsInstance(self.taxonomy, dict)
        expected_categories = [
            "Programming",
            "Machine Learning",
            "Data",
            "Databases",
            "Cloud and DevOps",
            "Web Development",
            "Soft Skills"
        ]
        for cat in expected_categories:
            self.assertIn(cat, self.taxonomy)
            self.assertIn("skills", self.taxonomy[cat])

    def test_extract_skills_direct_match(self):
        """Test extraction of canonical skill names."""
        text = "Experienced software engineer proficient in Python, SQL, and Docker."
        result = extract_skills(text, self.taxonomy)
        self.assertIn("Python", result["skills"])
        self.assertIn("SQL", result["skills"])
        self.assertIn("Docker", result["skills"])
        self.assertNotIn("Java", result["skills"])

    def test_extract_skills_aliases(self):
        """Test that aliases map to their canonical skill names."""
        text = "Strong background in ML, NLP, and K8s with expertise in JS."
        result = extract_skills(text, self.taxonomy)
        self.assertIn("Machine Learning", result["skills"])
        self.assertIn("Natural Language Processing", result["skills"])
        self.assertIn("Kubernetes", result["skills"])
        self.assertIn("JavaScript", result["skills"])

    def test_word_boundary_safety(self):
        """Test that substring matches don't produce false positives."""
        # 'Go' should not match 'Good' or 'Going'
        text_negative = "Good morning, we are going to the market."
        result_neg = extract_skills(text_negative, self.taxonomy)
        self.assertNotIn("Go", result_neg["skills"])

        # 'Java' should not trigger purely because of 'JavaScript'
        text_js = "Specialist in JavaScript development."
        result_js = extract_skills(text_js, self.taxonomy)
        self.assertIn("JavaScript", result_js["skills"])
        self.assertNotIn("Java", result_js["skills"])

    def test_special_characters_skills(self):
        """Test skills with special symbols such as C++, C#, Node.js."""
        text = "Proficient in C++, C#, and Node.js for backend systems."
        result = extract_skills(text, self.taxonomy)
        self.assertIn("C++", result["skills"])
        self.assertIn("C#", result["skills"])
        self.assertIn("Node.js", result["skills"])

    def test_empty_text(self):
        """Test extraction on empty text."""
        result = extract_skills("", self.taxonomy)
        self.assertEqual(result["skills"], set())
        self.assertEqual(result["categorized"], {})
        self.assertEqual(result["details"], [])

    def test_compare_skills(self):
        """Test skill comparison logic between resume and job description."""
        resume_text = "Proficient in Python, SQL, and Docker with AWS experience."
        job_text = "Looking for an engineer skilled in Python, Kubernetes, Docker, and PyTorch."

        resume_skills = extract_skills(resume_text, self.taxonomy)
        job_skills = extract_skills(job_text, self.taxonomy)

        comparison = compare_skills(resume_skills, job_skills)

        # Matched: Python, Docker
        self.assertIn("Python", comparison["matched"])
        self.assertIn("Docker", comparison["matched"])

        # Missing: Kubernetes, PyTorch
        self.assertIn("Kubernetes", comparison["missing"])
        self.assertIn("PyTorch", comparison["missing"])

        # Additional: SQL, AWS
        self.assertIn("SQL", comparison["additional"])
        self.assertIn("AWS", comparison["additional"])

        # Coverage: 2 matched out of 4 required = 0.5 (50%)
        self.assertEqual(comparison["coverage"], 0.5)
        self.assertEqual(comparison["coverage_percentage"], "50%")


if __name__ == "__main__":
    unittest.main()
