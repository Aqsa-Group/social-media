# config.py
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================================================
# SOCIAL MEDIA CREDENTIALS
# ============================================================

FACEBOOK_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID")
FACEBOOK_PAGE_ACCESS_TOKEN = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN")

IG_USER_ID = os.getenv("IG_USER_ID")
IG_ACCESS_TOKEN = os.getenv("IG_ACCESS_TOKEN")

# ============================================================
# AI CONFIGURATION
# ============================================================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ============================================================
# DIRECTORIES
# ============================================================

WATCH_DIRECTORY = "images/"
POSTED_DIRECTORY = "posted/"
AI_IMAGE_DIRECTORY = "ai_generated/"
PROMPTS_FILE = "prompts.txt"
HISTORY_FILE = "post_history.json"
LOG_FILE = "logs/app.log"

# ============================================================
# POST SETTINGS
# ============================================================

POST_TIME = "09:00"
CAPTION_TEMPLATE = """🚀 Daily Update

{content}

📅 {date}

Powered by AQSA GROUP
"""