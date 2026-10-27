"""Tests for Gemini AI Configuration, Status Reporting, and Fallback Handling.

Covers:
- Configuration loading from project .env
- Missing API key behavior (offline demo mode)
- Explicit Demo Mode override behavior
- AI service status reporting structure and consistency
- Error sanitization (preventing secret leakage)
- Integration test for real Gemini generation (when credentials available)
"""

import os
import unittest
from unittest.mock import patch, MagicMock
from config import Config
from services.ai_service import AIService, ai_service

class TestAIConfiguration(unittest.TestCase):
    """Test suite for AI configuration, demo mode switching, and status reporting."""

    def setUp(self):
        # Save original config
        self._orig_key = Config.GEMINI_API_KEY
        self._orig_model = Config.GEMINI_MODEL
        self._orig_force_demo = Config.FORCE_DEMO_MODE

    def tearDown(self):
        # Restore original config
        Config.GEMINI_API_KEY = self._orig_key
        Config.GEMINI_MODEL = self._orig_model
        Config.FORCE_DEMO_MODE = self._orig_force_demo
        ai_service.sync_config()

    def test_missing_api_key_activates_demo_mode(self):
        """When API key is empty or absent, AI service must be in Demo Mode."""
        Config.GEMINI_API_KEY = ""
        Config.FORCE_DEMO_MODE = False
        service = AIService()

        status = service.get_status()
        self.assertFalse(status["is_live_ai"])
        self.assertFalse(status["has_api_key"])
        self.assertIn("Demo Mode", status["mode"])
        self.assertIn("Deterministic Local Engine", status["provider"])

    def test_explicit_demo_mode_override(self):
        """When DEMO_MODE is true, even with an API key, Demo Mode is enforced."""
        Config.GEMINI_API_KEY = "test_dummy_key_12345"
        Config.FORCE_DEMO_MODE = True
        service = AIService()

        status = service.get_status()
        self.assertFalse(status["is_live_ai"])
        self.assertTrue(status["has_api_key"])
        self.assertIn("Demo Mode", status["mode"])
        self.assertIn("explicitly enabled", status["notice"])

    def test_status_payload_structure(self):
        """Verify all required status keys exist in get_status output."""
        status = ai_service.get_status()
        expected_keys = {"is_live_ai", "mode", "provider", "model", "has_api_key", "notice"}
        for k in expected_keys:
            self.assertIn(k, status)
            self.assertIsNotNone(status[k])

    def test_error_sanitization_removes_secrets(self):
        """Ensure secret keys are completely stripped from error strings."""
        raw_error = "Error calling https://generativelanguage.googleapis.com/v1beta/models?key=AIzaSyA1234567890abcdef1234567890abcdef"
        sanitized = AIService._sanitize_error(raw_error)
        self.assertNotIn("AIzaSyA1234567890abcdef1234567890abcdef", sanitized)
        self.assertIn("key=***", sanitized)

    def test_fallback_models_priority(self):
        """Ensure candidate models list starts with primary model and includes fallbacks."""
        service = AIService()
        service.model_name = "custom-test-model"
        candidates = service._get_candidate_models()
        self.assertEqual(candidates[0], "custom-test-model")
        for m in AIService.FALLBACK_MODELS:
            self.assertIn(m, candidates)

    def test_real_gemini_integration_generation(self):
        """Live integration test: verifies real Gemini connectivity when key is present."""
        if not self._orig_key or len(self._orig_key) < 10 or self._orig_force_demo:
            self.skipTest("No valid GEMINI_API_KEY configured for integration test.")

        ai_service.sync_config()
        status = ai_service.get_status()
        self.assertTrue(status["is_live_ai"], f"AI Service should be live. Notice: {status['notice']}")

        # Harmless, minimal real generation request
        response = ai_service.generate_text("Reply with: Integration test passed.")
        self.assertIsNotNone(response, "Real Gemini generation should return text, not None.")
        self.assertGreater(len(response.strip()), 0)
