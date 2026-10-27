"""Tests for Resume-to-Job Matching and Skill Alignment (Features B, C, and D).

Covers:
- Taxonomy-based skill extraction
- Transparent mathematical scoring formula
- Boundary conditions (0%, 100%, empty skills)
- Grounded improvement opportunities structure
"""

import unittest
from services.matching_service import matching_service
from config import Config
from services import ai_service

class TestMatchingService(unittest.TestCase):
    """Test suite for skill extraction and transparent score calculations."""

    @classmethod
    def setUpClass(cls):
        cls._orig_demo = Config.FORCE_DEMO_MODE
        Config.FORCE_DEMO_MODE = True
        ai_service.sync_config()

    @classmethod
    def tearDownClass(cls):
        Config.FORCE_DEMO_MODE = cls._orig_demo
        ai_service.sync_config()

    def test_extract_skills_rule_based(self):
        """Verify reliable extraction of common technical skills."""
        text = "Experienced in Python, Flask, SQLite, and building REST APIs with Docker."
        skills = matching_service.extract_skills_rule_based(text)
        self.assertIn("Python", skills)
        self.assertIn("Flask", skills)
        self.assertIn("SQLite", skills)
        self.assertIn("REST APIs", skills)
        self.assertIn("Docker", skills)

    def test_calculate_match_score_full_match(self):
        """When candidate possesses all required and preferred skills, score must be 100%."""
        req = ["Python", "Flask", "SQL"]
        pref = ["Docker", "Git"]
        resume_skills = ["Python", "Flask", "SQL", "Docker", "Git", "React"]

        score, breakdown = matching_service.calculate_match_score(resume_skills, req, pref)
        self.assertEqual(score, 100)
        self.assertEqual(breakdown["required_matched"], 3)
        self.assertEqual(breakdown["preferred_matched"], 2)
        self.assertEqual(len(breakdown["all_missing_skills"]), 0)

    def test_calculate_match_score_zero_match(self):
        """When candidate has no overlapping skills, score must be 0%."""
        req = ["Python", "Flask"]
        pref = ["Docker"]
        resume_skills = ["Java", "Spring Boot", "Kotlin"]

        score, breakdown = matching_service.calculate_match_score(resume_skills, req, pref)
        self.assertEqual(score, 0)
        self.assertEqual(len(breakdown["all_missing_skills"]), 3)

    def test_calculate_match_score_weighted_partial(self):
        """Verify 75% required / 25% preferred weighting."""
        req = ["Python", "Flask"]  # Candidate has 1 of 2 -> 50% * 75% = 37.5%
        pref = ["Docker", "AWS"]   # Candidate has 1 of 2 -> 50% * 25% = 12.5%
        # Total expected: 37.5 + 12.5 = 50%
        resume_skills = ["Python", "Docker"]

        score, breakdown = matching_service.calculate_match_score(resume_skills, req, pref)
        self.assertEqual(score, 50)
        self.assertEqual(breakdown["required_matched"], 1)
        self.assertEqual(breakdown["preferred_matched"], 1)
        self.assertIn("75%", breakdown["required_weight"])
        self.assertIn("25%", breakdown["preferred_weight"])

    def test_match_missing_inputs(self):
        """Missing resume or job text must raise a ValueError."""
        with self.assertRaises(ValueError):
            matching_service.match_resume_to_job("", "Valid Job Description")
        with self.assertRaises(ValueError):
            matching_service.match_resume_to_job("Valid Resume", "")

    def test_improvement_opportunities_structure(self):
        """Verify improvement opportunities contain section, issue, wording, and verification flag."""
        resume = "Experienced in Python and SQL with 1 year developing web services."
        job = "Looking for a Python Developer with Flask, Docker, and Prompt Engineering experience."

        result = matching_service.match_resume_to_job(resume, job)
        self.assertIn("match_score", result)
        self.assertIn("score_explanation", result)
        self.assertIn("improvement_opportunities", result)

        opps = result["improvement_opportunities"]
        self.assertGreater(len(opps), 0)
        for opp in opps:
            self.assertIn("section", opp)
            self.assertIn("current_issue", opp)
            self.assertIn("suggested_wording", opp)
            self.assertIn("needs_user_verification", opp)
            self.assertIsInstance(opp["needs_user_verification"], bool)

if __name__ == "__main__":
    unittest.main()
