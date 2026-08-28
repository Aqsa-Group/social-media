# social/instagram.py
import requests
import json
import time
import random
import logging
from config import IG_USER_ID, IG_ACCESS_TOKEN, IMAGE_URL

logger = logging.getLogger(__name__)

def post_to_instagram(caption, image_url=None):
    """
    Post image to Instagram Feed using URL
    """
    try:
        if not IG_USER_ID or not IG_ACCESS_TOKEN:
            logger.error("❌ Instagram credentials missing! Check .env")
            return False
        
        logger.info(f"📋 Instagram User ID: {IG_USER_ID}")
        
        # Use the provided URL or default
        if image_url is None:
            image_url = IMAGE_URL
        
        logger.info(f"📸 Image URL: {image_url}")
        logger.info(f"📝 Caption: {caption[:100]}...")
        
        # Human-like delay
        time.sleep(random.uniform(2, 5))
        
        # Step 1: Create media container
        create_url = f"https://graph.instagram.com/v24.0/{IG_USER_ID}/media"
        payload = {
            "image_url": image_url,
            "caption": caption,
            "access_token": IG_ACCESS_TOKEN,
        }
        
        logger.info("📬 Creating Instagram media container...")
        response = requests.post(create_url, data=payload, timeout=30)
        result = response.json()
        
        logger.info(f"📬 Instagram Response: {json.dumps(result, indent=2)}")
        
        if "id" not in result:
            error_msg = result.get('error', {}).get('message', 'Unknown error')
            logger.error(f"❌ Instagram media creation failed: {error_msg}")
            return False
        
        creation_id = result["id"]
        logger.info(f"✅ Media container created: {creation_id}")
        
        # Wait for processing
        wait_time = random.uniform(5, 12)
        logger.info(f"⏳ Waiting {wait_time:.1f} seconds for Instagram processing...")
        time.sleep(wait_time)
        
        # Step 2: Publish the media
        publish_url = f"https://graph.instagram.com/v24.0/{IG_USER_ID}/media_publish"
        publish_payload = {
            "creation_id": creation_id,
            "access_token": IG_ACCESS_TOKEN,
        }
        
        logger.info("📬 Publishing Instagram post...")
        publish_response = requests.post(publish_url, data=publish_payload, timeout=30)
        publish_result = publish_response.json()
        
        logger.info(f"📬 Instagram Publish Response: {json.dumps(publish_result, indent=2)}")
        
        if "id" in publish_result:
            logger.info(f"✅ Instagram post successful! ID: {publish_result['id']}")
            return True
        
        error_msg = publish_result.get('error', {}).get('message', 'Unknown error')
        logger.error(f"❌ Instagram publish failed: {error_msg}")
        return False
        
    except Exception as e:
        logger.error(f"❌ Instagram error: {e}")
        return False