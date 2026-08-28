# social/instagram_story.py
import requests
import json
import time
import random
import logging
from config import IG_USER_ID, IG_ACCESS_TOKEN, IMAGE_URL

logger = logging.getLogger(__name__)

def post_to_instagram_story(image_url=None):
    """
    Post image to Instagram Story using URL
    """
    try:
        if not IG_USER_ID or not IG_ACCESS_TOKEN:
            logger.error("❌ Instagram credentials missing! Check .env")
            return False
        
        logger.info(f"📋 Instagram User ID: {IG_USER_ID}")
        
        # Use the provided URL or default
        if image_url is None:
            image_url = IMAGE_URL
        
        logger.info(f"📸 Story Image URL: {image_url}")
        
        # Human-like delay
        time.sleep(random.uniform(2, 5))
        
        # Step 1: Create story media container
        create_url = f"https://graph.instagram.com/v24.0/{IG_USER_ID}/media"
        payload = {
            "media_type": "STORIES",
            "image_url": image_url,
            "access_token": IG_ACCESS_TOKEN,
        }
        
        logger.info("📬 Creating Instagram story container...")
        response = requests.post(create_url, data=payload, timeout=30)
        try:
            result = response.json()
        except ValueError:
            logger.error(
                "❌ Story media creation returned non-JSON response (status %s): %s",
                response.status_code,
                response.text[:500],
            )
            return False
        
        logger.info(f"📬 Instagram Story Response: {json.dumps(result, indent=2)}")
        
        if "id" not in result:
            error_msg = result.get('error', {}).get('message', 'Unknown error')
            logger.error(f"❌ Story media creation failed: {error_msg}")
            return False
        
        creation_id = result["id"]
        logger.info(f"✅ Story container created: {creation_id}")
        
        # Wait for processing
        wait_time = random.uniform(4, 8)
        logger.info(f"⏳ Waiting {wait_time:.1f} seconds for story processing...")
        time.sleep(wait_time)
        
        # Step 2: Publish the story
        publish_url = f"https://graph.instagram.com/v24.0/{IG_USER_ID}/media_publish"
        publish_payload = {
            "creation_id": creation_id,
            "access_token": IG_ACCESS_TOKEN,
        }
        
        logger.info("📬 Publishing Instagram story...")
        publish_response = requests.post(publish_url, data=publish_payload, timeout=30)
        try:
            publish_result = publish_response.json()
        except ValueError:
            logger.error(
                "❌ Story publish returned non-JSON response (status %s): %s",
                publish_response.status_code,
                publish_response.text[:500],
            )
            return False
        
        logger.info(f"📬 Instagram Story Publish Response: {json.dumps(publish_result, indent=2)}")
        
        if "id" in publish_result:
            logger.info(f"✅ Instagram story posted! ID: {publish_result['id']}")
            return True
        
        error_msg = publish_result.get('error', {}).get('message', 'Unknown error')
        logger.error(f"❌ Story publish failed: {error_msg}")
        return False
        
    except Exception as e:
        logger.error(f"❌ Story error: {e}")
        return False