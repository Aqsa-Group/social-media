# social/telegram.py
import requests
import json
import time
import random
import logging
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, IMAGE_URL

logger = logging.getLogger(__name__)

def post_to_telegram(caption, image_url=None):
    """
    Post image to Telegram using URL
    """
    try:
        if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
            logger.warning("⚠️ Telegram credentials not configured, skipping...")
            return False
        
        logger.info(f"📋 Telegram Chat ID: {TELEGRAM_CHAT_ID}")
        
        # Use the provided URL or default
        if image_url is None:
            image_url = IMAGE_URL
        
        logger.info(f"📸 Image URL: {image_url}")
        
        # Human-like delay
        time.sleep(random.uniform(1, 3))
        
        # Send photo using URL
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "photo": image_url,
            "caption": caption
        }
        
        logger.info("📬 Sending to Telegram...")
        response = requests.post(url, data=payload, timeout=30)
        result = response.json()
        
        logger.info(f"📬 Telegram Response: {json.dumps(result, indent=2)}")
        
        if result.get('ok'):
            logger.info(f"✅ Telegram post successful!")
            return True
        
        logger.error(f"❌ Telegram failed: {result.get('description', 'Unknown error')}")
        return False
        
    except Exception as e:
        logger.error(f"❌ Telegram error: {e}")
        return False