# ai_poster.py
import requests
import json
import time
import os
import shutil
import logging
from datetime import datetime
from pathlib import Path
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import configuration
from config import *

# ============================================================
# LOGGING SETUP
# ============================================================

os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Set OpenAI API key
openai.api_key = OPENAI_API_KEY

# ============================================================
# READ PROMPTS FROM FILE
# ============================================================

def read_prompts_from_file():
    """Read prompts from prompts.txt file"""
    prompts = []
    
    try:
        with open(PROMPTS_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    prompts.append(line)
        
        logger.info(f"Loaded {len(prompts)} prompts from {PROMPTS_FILE}")
        return prompts
        
    except FileNotFoundError:
        logger.warning(f"{PROMPTS_FILE} not found. Using default prompts.")
        return [
            "A professional business image with modern technology, clean and elegant design",
            "A successful business team collaborating in a modern office environment",
            "A professional corporate workspace with natural lighting and modern furniture"
        ]

# ============================================================
# GET DAILY PROMPT
# ============================================================

def get_daily_prompt():
    """Get today's prompt from the prompts file"""
    prompts = read_prompts_from_file()
    
    if not prompts:
        logger.error("No prompts available!")
        return None
    
    # Use day of year to rotate through prompts
    day_of_year = datetime.now().timetuple().tm_yday
    prompt_index = (day_of_year - 1) % len(prompts)
    
    selected_prompt = prompts[prompt_index]
    logger.info(f"Today's prompt: {selected_prompt[:100]}...")
    
    return selected_prompt

# ============================================================
# GENERATE AI IMAGE
# ============================================================

def generate_ai_image_from_prompt(prompt, size="1024x1024"):
    """Generate an image using OpenAI API"""
    try:
        logger.info("Generating AI image...")
        
        response = openai.images.generate(
            model="dall-e-2",
            prompt=prompt,
            size=size,
            quality="standard",
            n=1,
        )
        
        image_url = response.data[0].url
        logger.info("AI image generated successfully!")
        return image_url
        
    except Exception as e:
        logger.error(f"AI generation failed: {e}")
        return None

# ============================================================
# DOWNLOAD IMAGE
# ============================================================

def download_image(url, save_path):
    """Download an image from URL and save locally"""
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                f.write(response.content)
            return True
    except Exception as e:
        logger.error(f"Download failed: {e}")
    return False

# ============================================================
# GET IMAGE TO POST
# ============================================================

def get_image_to_post():
    """Priority: User uploaded > AI generated"""
    
    # Create directories
    os.makedirs(WATCH_DIRECTORY, exist_ok=True)
    os.makedirs(POSTED_DIRECTORY, exist_ok=True)
    os.makedirs(AI_IMAGE_DIRECTORY, exist_ok=True)
    
    # Check for new images
    image_files = []
    for ext in ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.webp']:
        image_files.extend(Path(WATCH_DIRECTORY).glob(ext))
    
    posted_files = set()
    for ext in ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.webp']:
        posted_files.update(Path(POSTED_DIRECTORY).glob(ext))
    
    new_images = [f for f in image_files if f not in posted_files]
    
    if new_images:
        image_path = new_images[0]
        logger.info(f"Using user uploaded photo: {image_path}")
        
        posted_path = Path(POSTED_DIRECTORY) / image_path.name
        shutil.move(str(image_path), str(posted_path))
        
        return str(posted_path), "User uploaded photo"
    
    # No new images - generate AI
    logger.info("No new images found. Generating AI image...")
    
    prompt = get_daily_prompt()
    if not prompt:
        return None, None
    
    image_url = generate_ai_image_from_prompt(prompt)
    if not image_url:
        return None, None
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    image_path = Path(AI_IMAGE_DIRECTORY) / f"ai_image_{timestamp}.jpg"
    
    if download_image(image_url, image_path):
        logger.info(f"AI image saved: {image_path}")
        return str(image_path), f"AI Generated: {prompt[:50]}..."
    else:
        return None, None

# ============================================================
# POST TO SOCIAL MEDIA
# ============================================================

def post_to_facebook(image_path, caption):
    """Post image to Facebook Feed"""
    logger.info("Posting to Facebook Feed...")

    url = f"https://graph.facebook.com/v23.0/{FACEBOOK_PAGE_ID}/photos"
    
    with open(image_path, 'rb') as img:
        files = {'source': img}
        payload = {
            'caption': caption,
            'access_token': FACEBOOK_PAGE_ACCESS_TOKEN,
        }
        
        response = requests.post(url, files=files, data=payload)
        result = response.json()
        
        if "id" in result:
            logger.info(f"✅ Facebook post published! ID: {result['id']}")
            return True
        else:
            logger.error(f"❌ Facebook failed: {result.get('error', {}).get('message')}")
            return False

def post_to_instagram(image_path, caption):
    """Post image to Instagram Feed"""
    logger.info("Posting to Instagram Feed...")

    # For production, you need to host the image
    image_url = "https://temp.aqsagroup.af/office.jpg"

    create_url = f"https://graph.instagram.com/v24.0/{IG_USER_ID}/media"

    payload = {
        "image_url": image_url,
        "caption": caption,
        "access_token": IG_ACCESS_TOKEN,
    }

    response = requests.post(create_url, data=payload)
    result = response.json()

    if "id" not in result:
        logger.error(f"❌ Failed to create Instagram media: {result.get('error', {}).get('message')}")
        return False

    creation_id = result["id"]
    logger.info(f"✅ Media container created: {creation_id}")

    time.sleep(5)

    publish_url = f"https://graph.instagram.com/v24.0/{IG_USER_ID}/media_publish"
    publish_payload = {
        "creation_id": creation_id,
        "access_token": IG_ACCESS_TOKEN,
    }

    publish_response = requests.post(publish_url, data=publish_payload)
    publish_result = publish_response.json()
    
    if "id" in publish_result:
        logger.info(f"✅ Instagram post published! ID: {publish_result['id']}")
        return True
    else:
        logger.error(f"❌ Instagram publish failed: {publish_result.get('error', {}).get('message')}")
        return False

def post_instagram_story(image_path, caption):
    """Post image to Instagram Story"""
    logger.info("Posting to Instagram Story...")
    
    image_url = "https://temp.aqsagroup.af/office.jpg"
    
    create_url = f"https://graph.instagram.com/v24.0/{IG_USER_ID}/media"
    payload = {
        "media_type": "STORIES",
        "image_url": image_url,
        "access_token": IG_ACCESS_TOKEN,
    }
    
    response = requests.post(create_url, data=payload)
    result = response.json()
    
    if "id" not in result:
        logger.error(f"❌ Failed to create story: {result.get('error', {}).get('message')}")
        return False
    
    creation_id = result["id"]
    logger.info(f"✅ Story container created: {creation_id}")
    
    time.sleep(5)
    
    publish_url = f"https://graph.instagram.com/v24.0/{IG_USER_ID}/media_publish"
    publish_payload = {
        "creation_id": creation_id,
        "access_token": IG_ACCESS_TOKEN,
    }
    
    publish_response = requests.post(publish_url, data=publish_payload)
    publish_result = publish_response.json()
    
    if "id" in publish_result:
        logger.info(f"✅ Instagram Story published! ID: {publish_result['id']}")
        return True
    else:
        logger.error(f"❌ Story publish failed: {publish_result.get('error', {}).get('message')}")
        return False

# ============================================================
# DAILY PUBLISH
# ============================================================

def publish_daily():
    """Main function: Daily post"""
    logger.info(f"🚀 Starting daily post - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    # Get image
    image_path, image_source = get_image_to_post()
    
    if not image_path:
        logger.error("No image available to post")
        return False
    
    logger.info(f"Image source: {image_source}")
    
    # Generate caption
    date_str = datetime.now().strftime('%B %d, %Y')
    if "User uploaded" in image_source:
        content = "📸 Photo uploaded by our team!"
    else:
        content = f"🤖 AI Generated Image\n\n{image_source}"
    
    caption = CAPTION_TEMPLATE.format(content=content, date=date_str)
    
    # Post to platforms
    results = []
    
    results.append(("Facebook Feed", post_to_facebook(image_path, caption)))
    results.append(("Instagram Feed", post_to_instagram(image_path, caption)))
    results.append(("Instagram Story", post_instagram_story(image_path, caption)))
    
    # Summary
    logger.info("📊 PUBLISHING SUMMARY")
    successful = 0
    for platform, success in results:
        status = "✅" if success else "❌"
        logger.info(f"{status} {platform}: {'Published' if success else 'Failed'}")
        if success:
            successful += 1
    
    logger.info(f"Total: {successful}/{len(results)} posts published successfully")
    
    return successful > 0

if __name__ == "__main__":
    publish_daily()