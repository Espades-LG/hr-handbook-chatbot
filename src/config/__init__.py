"""
Configuration module for HR Handbook Chatbot
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ==================== ENVIRONMENT VARIABLES ====================

# OpenAI API
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")

# System settings
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# ==================== CHATBOT CONFIGURATION ====================

# Handbook source
HANDBOOK_DIR = "docs/handbook-content"

HANDBOOK_FILES = {
    "policies": f"{HANDBOOK_DIR}/policies.md",
    "benefits": f"{HANDBOOK_DIR}/benefits.md",
    "leave": f"{HANDBOOK_DIR}/leave.md",
    "compensation": f"{HANDBOOK_DIR}/compensation.md",
    "other": f"{HANDBOOK_DIR}/other.md",
}

# Chatbot behavior
TEMPERATURE = 0.3  # Lower = more factual, less creative
MAX_TOKENS = 1000  # Max response length

# Response defaults
DEFAULT_RESPONSE = """
I don't have that information in the handbook. 
Please contact HR for help:
- Email: hr@company.com
- Phone: [PHONE]
- Hours: [BUSINESS HOURS]
"""

ESCALATION_TOPICS = [
    "personal salary",
    "individual claim",
    "disciplinary",
    "harassment",
    "accommodation",
    "contract",
]

# ==================== VECTOR SEARCH CONFIGURATION ====================

EMBEDDING_MODEL = "text-embedding-3-small"
SIMILARITY_THRESHOLD = 0.7  # Minimum relevance score
MAX_RESULTS = 3  # Top K results to retrieve

# ==================== LOGGING ====================

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
