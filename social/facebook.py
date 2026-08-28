# social/facebook.py
import requests
import json
import time
import random
import logging
from config import FACEBOOK_PAGE_ID, FACEBOOK_PAGE_ACCESS_TOKEN, IMAGE_URL

logger = logging.getLogger(__name__)

def post_to_facebook(caption, image_url=None):
    """
    Post image to Facebook Feed using URL
    """
    try:
        if not FACEBOOK_PAGE_ID or not FACEBOOK_PAGE_ACCESS_TOKEN:
            logger.error("❌ Facebook credentials missing! Check .env")
            return False
        
        logger.info(f"📋 Facebook Page ID: {FACEBOOK_PAGE_ID}")
        
        # Use the provided URL or default
        if image_url is None:
            image_url = IMAGE_URL
        
        logger.info(f"📸 Image URL: {image_url}")
        logger.info(f"📝 Caption: {caption[:100]}...")
        
        # Human-like delay
        time.sleep(random.uniform(2, 5))
        
        url = f"https://graph.facebook.com/v23.0/{FACEBOOK_PAGE_ID}/photos"
        payload = {
            "url": image_url,
            "caption": caption,
            "access_token": FACEBOOK_PAGE_ACCESS_TOKEN,
        }
        
        response = requests.post(url, data=payload, timeout=30)
        result = response.json()
        
        logger.info(f"📬 Facebook Response: {json.dumps(result, indent=2)}")
        
        if "id" in result:
            logger.info(f"✅ Facebook post successful! ID: {result['id']}")
            return True
        
        error_msg = result.get('error', {}).get('message', 'Unknown error')
        logger.error(f"❌ Facebook failed: {error_msg}")
        return False
        
    except Exception as e:
        logger.error(f"❌ Facebook error: {e}")
        return False