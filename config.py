# config.py
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
PROJECT_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = PROJECT_DIR / "images" / "uploads"
AI_GENERATED_DIR = PROJECT_DIR / "images" / "ai_generated"
POSTED_DIR = PROJECT_DIR / "images" / "posted"
LOG_DIR = PROJECT_DIR / "logs"

# ============ SOCIAL MEDIA CREDENTIALS ============

# Facebook
FACEBOOK_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID")
FACEBOOK_PAGE_ACCESS_TOKEN = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN")

# Instagram
IG_USER_ID = os.getenv("IG_USER_ID")
IG_ACCESS_TOKEN = os.getenv("IG_ACCESS_TOKEN")

# Telegram (optional)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# ============ PUBLIC IMAGE URL ============
IMAGE_URL = os.getenv("IMAGE_URL") or None
PUBLIC_IMAGE_BASE_URL = os.getenv(
    "PUBLIC_IMAGE_BASE_URL",
    "https://aqsagroup.af/repositories/social-media",
).rstrip("/")
WATCH_DIRECTORY = os.getenv("WATCH_DIRECTORY", str(UPLOAD_DIR))
WEB_HOST = os.getenv("WEB_HOST", "127.0.0.1")
WEB_PORT = int(os.getenv("WEB_PORT", "5000"))

# ============ HASHTAGS ============
HASHTAGS = "#aqsagroup #aqsasystem #aqsapay #sarafi"

# ============ ADVERTISING TEMPLATES ============
AD_TEMPLATES = {
    "office": [
        "🏢 Elevate your workspace with AQSA GROUP!",
        "💼 Professional environment, professional results.",
        "🌟 Your success starts with the right environment."
    ],
    "business": [
        "💼 Trust AQSA GROUP for all your business needs.",
        "🚀 Growing businesses choose AQSA GROUP.",
        "📈 Your partner in business success."
    ],
    "technology": [
        "💻 Innovation at its finest with AQSA GROUP.",
        "🔬 Cutting-edge solutions for modern challenges.",
        "⚡ Technology that drives your business forward."
    ],
    "team": [
        "🤝 Together we achieve more with AQSA GROUP.",
        "👥 Building strong teams for better results.",
        "💪 United we stand, with AQSA GROUP."
    ],
    "default": [
        "✨ AQSA GROUP - Excellence in everything we do.",
        "🌟 Quality you can trust, service you can count on.",
        "💎 AQSA GROUP - Building a better future."
    ]
}

CAPTION_TEMPLATE = """{ad_text}

{content}

{HASHTAGS}"""

# ============ PLATFORM CONFIGURATION ============
# ⚠️ THIS MUST BE DEFINED
PLATFORMS = {
    "facebook": True,
    "instagram": True,
    "instagram_story": True,   # ⚠️ MUST BE True
    "telegram": False,
}