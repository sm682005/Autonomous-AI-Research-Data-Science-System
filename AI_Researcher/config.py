"""
Central configuration for Autonomous AI Researcher.
Loads environment variables, defines operational thresholds, and initializes Gemini client.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Find .env in current directory or project root
PROJECT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PROJECT_ROOT.parent

load_dotenv(PROJECT_ROOT / ".env")
load_dotenv(REPO_ROOT / ".env")

# Gemini Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3-flash-preview").strip()

# Operational Defaults
DEFAULT_PAPER_COUNT = int(os.getenv("DEFAULT_PAPER_COUNT", "8"))
MAX_REVISIONS = int(os.getenv("MAX_REVISIONS", "1"))
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "15"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))

# Directory Paths
REPORTS_DIR = PROJECT_ROOT / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# Academic API Endpoints
ARXIV_API_URL = "http://export.arxiv.org/api/query"
SEMANTIC_SCHOLAR_URL = "https://api.semanticscholar.org/graph/v1/paper/search"


def get_gemini_client():
    """
    Returns an initialized Google GenAI client using the official google-genai SDK.
    Raises ValueError with actionable instructions if GEMINI_API_KEY is not set.
    """
    key = os.getenv("GEMINI_API_KEY", GEMINI_API_KEY).strip()
    if not key or key == "MY_GEMINI_API_KEY":
        raise ValueError(
            "GEMINI_API_KEY is missing or unset.\n"
            "Please configure your Google AI Studio API key in AI_Researcher/.env or export GEMINI_API_KEY.\n"
            "Get a key for free from: https://aistudio.google.com/app/apikey"
        )
    
    from google import genai
    return genai.Client(api_key=key)


def get_config_status() -> dict:
    """Returns a dictionary summary of current configuration status without leaking keys."""
    key = os.getenv("GEMINI_API_KEY", GEMINI_API_KEY).strip()
    has_key = bool(key and key != "MY_GEMINI_API_KEY")
    masked_key = f"{key[:4]}...{key[-4:]}" if (has_key and len(key) > 8) else ("Configured" if has_key else "Missing")
    
    return {
        "api_key_status": "Valid/Set" if has_key else "Not Set",
        "masked_key": masked_key,
        "model": GEMINI_MODEL,
        "default_paper_count": DEFAULT_PAPER_COUNT,
        "max_revisions": MAX_REVISIONS,
        "request_timeout_seconds": REQUEST_TIMEOUT,
        "max_retries": MAX_RETRIES,
        "reports_directory": str(REPORTS_DIR),
        "arxiv_source": "Active",
        "semantic_scholar_source": "Secondary (Active)",
    }
