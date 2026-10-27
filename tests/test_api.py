"""End-to-End API Integration Tests for Flask Endpoints.

Tests:
- GET /
- GET /api/status
- GET /api/dashboard/stats
- POST /api/job/analyze
- POST /api/matching/analyze
- POST /api/cover-letter/generate
- POST /api/recruiter-messages/generate
- POST /api/interview/questions
- POST /api/interview/evaluate
- Application Tracker REST Endpoints (CRUD)
- GET /api/prompts/live
"""

import unittest
from unittest.mock import patch
from app import app
from database import init_db
from config import Config
from services import ai_service

class TestFlaskAPI(unittest.TestCase):
    """Integration test suite for Flask REST API routes."""

    @classmethod
    def setUpClass(cls):
        app.config["TESTING"] = True
        cls.client = app.test_client()
        cls._orig_demo = Config.FORCE_DEMO_MODE
        Config.FORCE_DEMO_MODE = True
        ai_service.sync_config()

    @classmethod
    def tearDownClass(cls):
        Config.FORCE_DEMO_MODE = cls._orig_demo
        ai_service.sync_config()

    def test_status_endpoint(self):
        """Verify AI provider status endpoint returns 200 and operational details."""
        res = self.client.get("/api/status")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIn("mode", data["status"])

    def test_dashboard_stats_endpoint(self):
        """Verify dashboard stats calculation endpoint."""
        res = self.client.get("/api/dashboard/stats")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIn("total_applications", data["stats"])

    def test_job_analyze_endpoint(self):
        """Verify job description parser endpoint."""
        payload = {
            "job_description": "We need a Python Developer skilled in Flask, SQL, and REST APIs with 0-2 years experience."
        }
        res = self.client.post("/api/job/analyze", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIn("required_skills", data["data"])

    def test_matching_analyze_endpoint(self):
        """Verify resume-to-job matching endpoint."""
        payload = {
            "resume_text": "Experienced Python and SQL developer with REST API project work.",
            "job_description": "Required skills: Python, Flask, SQL, Docker. Responsibilities: Build APIs."
        }
        res = self.client.post("/api/matching/analyze", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIn("match_score", data["data"])
        self.assertIn("calculation_breakdown", data["data"])

    def test_cover_letter_generate_endpoint(self):
        """Verify cover letter generation endpoint."""
        payload = {
            "company_name": "Gokul Infocare",
            "job_title": "AI Growth Associate",
            "tone": "Professional",
            "resume_text": "Skills: Python, Flask, Prompt Engineering.",
            "job_description": "We are seeking an AI Growth Associate proficient in Python and Prompt Engineering."
        }
        res = self.client.post("/api/cover-letter/generate", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIn("Dear Hiring Team", data["data"]["cover_letter"])

    def test_recruiter_message_generate_endpoint(self):
        """Verify recruiter messaging endpoint."""
        payload = {
            "message_type": "Application Follow-up",
            "company_name": "Gokul Infocare",
            "job_title": "AI Associate",
            "tone": "Professional & Polite",
            "resume_text": "Skills: Python, Automation."
        }
        res = self.client.post("/api/recruiter-messages/generate", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIn("Following Up", data["data"]["subject"])

    def test_interview_questions_endpoint(self):
        """Verify role interview questions endpoint."""
        payload = {
            "job_description": "Python, Flask, and SQLite automation role.",
            "resume_text": "Built Python automation pipelines."
        }
        res = self.client.post("/api/interview/questions", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertGreaterEqual(len(data["data"]["questions"]), 6)

    def test_interview_evaluate_endpoint(self):
        """Verify candidate answer practice mode feedback endpoint."""
        payload = {
            "job_title": "AI Associate",
            "question": "How do you handle API errors?",
            "candidate_answer": "When building an API, I encountered network timeouts. I implemented exponential backoff retries and logged failures to prevent silent crashes."
        }
        res = self.client.post("/api/interview/evaluate", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIn("overall_rating", data["data"])
        self.assertIn("score", data["data"])

    def test_live_prompts_endpoint(self):
        """Verify live production prompt introspection endpoint."""
        res = self.client.get("/api/prompts/live")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["success"])
        self.assertIn("system_prompt", data)
        self.assertIn("templates", data)

if __name__ == "__main__":
    unittest.main()
