import os
import secrets
from pathlib import Path
from dotenv import load_dotenv

# Base directory of the application
BASE_DIR = Path(__file__).resolve().parent

_last_env_mtime = None

def load_environment(force: bool = False) -> bool:
    """Load or reload environment variables from .env file if file was modified."""
    global _last_env_mtime
    env_path = BASE_DIR / ".env"
    if env_path.exists():
        try:
            mtime = env_path.stat().st_mtime
            if force or _last_env_mtime is None or mtime != _last_env_mtime:
                load_dotenv(env_path, override=True)
                _last_env_mtime = mtime
                return True
        except Exception:
            pass
    return False

# Initial load
load_environment(force=True)

# Secure random fallback used only when SECRET_KEY is absent from .env.
# A new random value is generated each process start — set SECRET_KEY in .env for persistence.
_FALLBACK_SECRET_KEY = secrets.token_hex(32)

class Config:
    """Application configuration settings."""
    SECRET_KEY = os.environ.get("SECRET_KEY") or _FALLBACK_SECRET_KEY

    # Upload settings
    UPLOAD_FOLDER = BASE_DIR / "uploads"
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB max file size
    ALLOWED_EXTENSIONS = {"pdf"}

    # Database
    DATABASE_PATH = BASE_DIR / "database" / "job_tracker.db"

    # AI Configuration
    # Supports Google Gemini official SDK / API key
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
    GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash").strip()
    AI_TIMEOUT_SECONDS = int(os.environ.get("AI_TIMEOUT_SECONDS", "15"))

    # Explicit demo mode override or auto-detect if API key is missing
    FORCE_DEMO_MODE = os.environ.get("DEMO_MODE", "false").lower() in ("true", "1", "yes")
    DEMO_MODE = FORCE_DEMO_MODE or (not GEMINI_API_KEY)

    # Privacy & Safety
    ALLOW_PERMANENT_RESUME_STORAGE = False

    @classmethod
    def reload(cls, force: bool = False):
        """Re-read .env and update configuration attributes dynamically if changed."""
        changed = load_environment(force=force)
        if changed or force:
            cls.SECRET_KEY = os.environ.get("SECRET_KEY") or _FALLBACK_SECRET_KEY
            cls.GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
            cls.GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash").strip()
            cls.AI_TIMEOUT_SECONDS = int(os.environ.get("AI_TIMEOUT_SECONDS", "15"))
            cls.FORCE_DEMO_MODE = os.environ.get("DEMO_MODE", "false").lower() in ("true", "1", "yes")
            cls.DEMO_MODE = cls.FORCE_DEMO_MODE or (not cls.GEMINI_API_KEY)
        return cls
