"""AI Service provider integration with Google Gemini and transparent deterministic Demo Mode fallback.

Handles:
- API key validation
- Real API calls via google.genai SDK
- Timeouts and network error recovery
- JSON extraction and sanitization
- Explicit labeling of AI vs Demo outputs
"""

import os
import json
import re
import logging
from typing import Dict, Any, Optional
from config import Config
from .prompt_templates import SYSTEM_PROMPT

logger = logging.getLogger(__name__)

class AIService:
    """Manages AI LLM interactions and transparent demo mode fallbacks."""

    FALLBACK_MODELS = ["gemini-3.5-flash", "gemini-3.5-flash-lite", "gemini-3.8-flash"]

    def __init__(self):
        self.api_key = ""
        self.model_name = "gemini-3.5-flash"
        self.timeout = 15
        self._client = None
        self._active_model = None
        self._last_error = None
        self._current_key = None
        self.sync_config()

    def sync_config(self, force: bool = False):
        """Dynamically synchronize state with Config and .env."""
        try:
            Config.reload(force=force)
        except Exception as e:
            logger.warning("Could not reload Config: %s", e)

        new_key = Config.GEMINI_API_KEY
        new_model = Config.GEMINI_MODEL
        new_timeout = Config.AI_TIMEOUT_SECONDS
        force_demo = Config.FORCE_DEMO_MODE

        expected_has_client = bool(new_key) and not force_demo
        has_client = self._client is not None

        needs_reinit = (
            has_client != expected_has_client
            or self._current_key != new_key
            or self.model_name != new_model
        )

        self.api_key = new_key
        self.model_name = new_model
        self.timeout = new_timeout

        if needs_reinit:
            self._initialize_client()

    def _initialize_client(self):
        """Attempt to initialize the Google GenAI client if an API key is available."""
        if self.api_key and not Config.FORCE_DEMO_MODE:
            try:
                from google import genai
                self._client = genai.Client(api_key=self.api_key)
                self._current_key = self.api_key
                self._active_model = self.model_name
                self._last_error = None
                logger.info("Google GenAI client initialized successfully.")
            except Exception as e:
                sanitized = self._sanitize_error(str(e))
                logger.warning("Could not initialize Google GenAI client: %s. Falling back to Demo Mode.", sanitized)
                self._client = None
                self._last_error = sanitized
        else:
            self._client = None
            self._current_key = None
            self._active_model = None

    def get_status(self) -> Dict[str, Any]:
        """Return the current operational status of the AI provider."""
        self.sync_config()

        has_key = bool(self.api_key and len(self.api_key.strip()) > 5)
        is_live = bool(self._client is not None and not Config.FORCE_DEMO_MODE)
        model_display = self._active_model or self.model_name

        if Config.FORCE_DEMO_MODE:
            notice = "Demo Mode explicitly enabled via DEMO_MODE=true in .env."
        elif is_live:
            notice = f"Connected to Google Gemini API ({model_display})"
        elif has_key and not is_live:
            notice = f"API key configured, but live client initialization failed: {self._last_error or 'Unknown error'}. Running in Demo Mode."
        else:
            notice = "Running in offline Demo Mode. Add GEMINI_API_KEY to your local .env to activate live generative AI."

        return {
            "is_live_ai": is_live,
            "mode": "Live AI (Google Gemini)" if is_live else "Demo Mode (Deterministic Rule Engine)",
            "provider": "Google Gemini" if is_live else "Deterministic Local Engine",
            "model": model_display if is_live else "Rule-Based Mock/Fallback",
            "has_api_key": has_key,
            "notice": notice
        }

    def _get_candidate_models(self) -> list:
        """Return prioritized list of model candidates to attempt."""
        candidates = [self.model_name]
        for m in self.FALLBACK_MODELS:
            if m not in candidates:
                candidates.append(m)
        return candidates

    def generate_json(self, prompt: str, system_prompt: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Request structured JSON from Gemini, or return None if live AI is unavailable."""
        self.sync_config()
        if not self._client:
            return None

        sys_instruction = system_prompt or SYSTEM_PROMPT
        candidates = self._get_candidate_models()

        try:
            from google.genai import types
        except ImportError:
            logger.error("google.genai SDK not installed.")
            return None

        config = types.GenerateContentConfig(
            system_instruction=sys_instruction,
            temperature=0.2,  # Low temperature for factual consistency
            response_mime_type="application/json"
        )

        for candidate_model in candidates:
            try:
                response = self._client.models.generate_content(
                    model=candidate_model,
                    contents=prompt,
                    config=config
                )

                if response and response.text:
                    if candidate_model != self.model_name:
                        logger.info("Primary model '%s' unavailable; succeeded with fallback '%s'.", self.model_name, candidate_model)
                    self._active_model = candidate_model
                    self._last_error = None
                    cleaned_text = self._extract_json_text(response.text)
                    return json.loads(cleaned_text)

            except Exception as e:
                err_msg = self._sanitize_error(str(e))
                self._last_error = err_msg

                # Fatal auth errors: don't loop through other models
                if any(code in err_msg for code in ["API_KEY_INVALID", "401", "403", "PERMISSION_DENIED"]):
                    logger.error("Gemini API authentication failed: %s. Falling back to Demo Mode.", err_msg)
                    break

                logger.warning("Gemini JSON generation failed on model '%s': %s", candidate_model, err_msg)
                continue

        return None

    def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> Optional[str]:
        """Request freeform text generation from Gemini, or return None if unavailable."""
        self.sync_config()
        if not self._client:
            return None

        sys_instruction = system_prompt or SYSTEM_PROMPT
        candidates = self._get_candidate_models()

        try:
            from google.genai import types
        except ImportError:
            logger.error("google.genai SDK not installed.")
            return None

        config = types.GenerateContentConfig(
            system_instruction=sys_instruction,
            temperature=0.3
        )

        for candidate_model in candidates:
            try:
                response = self._client.models.generate_content(
                    model=candidate_model,
                    contents=prompt,
                    config=config
                )

                if response and response.text:
                    if candidate_model != self.model_name:
                        logger.info("Primary model '%s' unavailable; succeeded with fallback '%s'.", self.model_name, candidate_model)
                    self._active_model = candidate_model
                    self._last_error = None
                    return response.text.strip()

            except Exception as e:
                err_msg = self._sanitize_error(str(e))
                self._last_error = err_msg

                # Fatal auth errors: don't loop through other models
                if any(code in err_msg for code in ["API_KEY_INVALID", "401", "403", "PERMISSION_DENIED"]):
                    logger.error("Gemini API authentication failed: %s. Falling back to Demo Mode.", err_msg)
                    break

                logger.warning("Gemini Text generation failed on model '%s': %s", candidate_model, err_msg)
                continue

        return None

    @staticmethod
    def _sanitize_error(error_msg: str) -> str:
        """Strip sensitive credentials from error messages."""
        if not error_msg:
            return ""
        # Redact any API key queries or strings resembling credentials
        cleaned = re.sub(r'key=[A-Za-z0-9_\-]+', 'key=***', error_msg)
        cleaned = re.sub(r'AIza[0-9A-Za-z-_]{35}', 'AIza***', cleaned)
        return cleaned

    @staticmethod
    def _extract_json_text(text: str) -> str:
        """Strip markdown code block fences and return raw JSON."""
        text = text.strip()
        # Remove ```json ... ``` or ``` ... ```
        if text.startswith("```"):
            lines = text.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            text = "\n".join(lines).strip()

        # Match outermost curly braces if extra text exists
        match = re.search(r'(\{[\s\S]*\})', text)
        if match:
            return match.group(1)
        return text

# Global singleton
ai_service = AIService()
