# ai_poster.py
import requests
import json
import time
import os
import shutil
import logging
<<<<<<< HEAD
import random
from datetime import datetime
from pathlib import Path
=======
from datetime import datetime
from pathlib import Path
import openai
>>>>>>> 991c44e90d4fae9759c637b63fb5909da2503cc6
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import configuration
from config import *
<<<<<<< HEAD
from memory_manager import MemoryManager
=======
>>>>>>> 991c44e90d4fae9759c637b63fb5909da2503cc6

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

<<<<<<< HEAD
# Initialize Memory
memory = MemoryManager(MEMORY_FILE, LEARNING_FILE)

# ============================================================
# SMART CAPTION GENERATION (NO DATE)
# ============================================================

def generate_smart_caption(prompt, image_source):
    """
    Generate a smart advertising caption based on the prompt/image
    """
    from config import AD_TEMPLATES, HASHTAGS, CAPTION_TEMPLATE
    
    # Determine the type of image from prompt
    prompt_lower = prompt.lower() if prompt else ""
    
    # Check for keywords in prompt
    ad_type = "default"
    keywords = {
        "office": ["office", "workspace", "desk", "meeting room", "boardroom", "corporate"],
        "business": ["business", "professional", "corporate", "company", "enterprise"],
        "technology": ["technology", "tech", "digital", "innovation", "futuristic", "holographic"],
        "team": ["team", "collaborating", "working", "employees", "staff", "together"],
        "success": ["success", "achievement", "goal", "growth", "leadership", "vision"]
    }
    
    # Find matching type
    for key, words in keywords.items():
        if any(word in prompt_lower for word in words):
            ad_type = key
            break
    
    # Select random ad text from the matching template
    ad_text = random.choice(AD_TEMPLATES.get(ad_type, AD_TEMPLATES["default"]))
    
    # Determine content based on image source
    if "User uploaded" in image_source:
        content = "📸 Check out this amazing photo from our team!"
    else:
        # Use the prompt as content
        content = f"🤖 {prompt[:200]}..." if len(prompt) > 200 else f"🤖 {prompt}"
    
    # Generate the full caption (NO DATE)
    caption = CAPTION_TEMPLATE.format(
        ad_text=ad_text,
        content=content,
        HASHTAGS=HASHTAGS
    )
    
    return caption

# ============================================================
# HUMAN-LIKE DELAYS (To avoid bot detection)
# ============================================================

def human_like_delay():
    """Add random delays between actions to look human"""
    # Random delay between 2-8 seconds
    delay = random.uniform(2, 8)
    logger.info(f"⏳ Waiting {delay:.1f} seconds (human-like delay)...")
    time.sleep(delay)

def random_typing_speed():
    """Simulate human typing speed"""
    return random.uniform(0.05, 0.2)

# ============================================================
# POST TO FACEBOOK
# ============================================================

def post_to_facebook(image_path, caption):
    """Post image to Facebook Feed with human-like delays"""
    logger.info("📤 Posting to Facebook Feed...")
    
    # Human-like delay before posting
    human_like_delay()
=======
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
    """Generate an image using free Pollinations.ai API"""
    try:
        logger.info("Generating AI image using free service...")
        
        import urllib.parse
        encoded_prompt = urllib.parse.quote(prompt)
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true"
        
        logger.info("AI image generated successfully!")
        return image_url
        
    except Exception as e:
        logger.error(f"AI generation failed: {e}")
        # Return a placeholder image
        return "https://via.placeholder.com/1024x1024/4A90D9/FFFFFF?text=AQSA+GROUP"
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
>>>>>>> 991c44e90d4fae9759c637b63fb5909da2503cc6

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

<<<<<<< HEAD
# ============================================================
# POST TO INSTAGRAM - FIXED TO USE PROMPTS
# ============================================================

def post_to_instagram(image_path, caption):
    """Post image to Instagram Feed with human-like delays"""
    logger.info("📤 Posting to Instagram Feed...")
    
    # Human-like delay
    human_like_delay()

    # Get the filename and create a public URL
    filename = os.path.basename(image_path)
    
    # OPTION 1: If images are in public_html/images/ via symlink
    image_url = f"https://aqsagroup.af/images/{filename}"
    
    # OPTION 2: If images are in ai_generated folder
    # image_url = f"https://aqsagroup.af/ai_generated_images/{filename}"
    
    # OPTION 3: Fallback to temp URL
    # image_url = f"https://temp.aqsagroup.af/{filename}"
    
    logger.info(f"📸 Image URL: {image_url}")
=======
def post_to_instagram(image_path, caption):
    """Post image to Instagram Feed"""
    logger.info("Posting to Instagram Feed...")

    # For production, you need to host the image
    image_url = "https://temp.aqsagroup.af/office.jpg"
>>>>>>> 991c44e90d4fae9759c637b63fb5909da2503cc6

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

<<<<<<< HEAD
    # Longer human-like delay for processing
    processing_delay = random.uniform(5, 12)
    logger.info(f"⏳ Waiting {processing_delay:.1f} seconds for Instagram processing...")
    time.sleep(processing_delay)
=======
    time.sleep(5)
>>>>>>> 991c44e90d4fae9759c637b63fb5909da2503cc6

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

<<<<<<< HEAD
# ============================================================
# POST TO INSTAGRAM STORY - FIXED TO USE PROMPTS
# ============================================================

def post_instagram_story(image_path, caption):
    """Post image to Instagram Story with human-like delays"""
    logger.info("📤 Posting to Instagram Story...")
    
    # Human-like delay
    human_like_delay()
    
    # Get the filename and create a public URL
    filename = os.path.basename(image_path)
    
    # OPTION 1: If images are in public_html/images/ via symlink
    image_url = f"https://aqsagroup.af/images/{filename}"
    
    # OPTION 2: If images are in ai_generated folder
    # image_url = f"https://aqsagroup.af/ai_generated_images/{filename}"
    
    # OPTION 3: Fallback to temp URL
    # image_url = f"https://temp.aqsagroup.af/{filename}"
    
    logger.info(f"📸 Story Image URL: {image_url}")
=======
def post_instagram_story(image_path, caption):
    """Post image to Instagram Story"""
    logger.info("Posting to Instagram Story...")
    
    image_url = "https://temp.aqsagroup.af/office.jpg"
>>>>>>> 991c44e90d4fae9759c637b63fb5909da2503cc6
    
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
    
<<<<<<< HEAD
    # Human-like delay
    story_delay = random.uniform(4, 8)
    logger.info(f"⏳ Waiting {story_delay:.1f} seconds...")
    time.sleep(story_delay)
=======
    time.sleep(5)
>>>>>>> 991c44e90d4fae9759c637b63fb5909da2503cc6
    
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
<<<<<<< HEAD
# READ AND CONSUME PROMPT
# ============================================================

def read_and_consume_prompt():
    """
    Reads the first prompt from prompts.txt, removes it from the file,
    and returns the prompt.
    If no prompts available, generates a smart prompt from memory.
    """
    try:
        # Read all prompts
        with open(PROMPTS_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Filter out empty lines and comments
        prompts = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                prompts.append(line)
        
        if prompts:
            # Use first prompt from file
            prompt = prompts[0]
            logger.info(f"📝 Using prompt from file: {prompt[:100]}...")
            
            # Remove the first prompt
            remaining_prompts = prompts[1:]
            
            # Write remaining prompts back to file
            with open(PROMPTS_FILE, 'w', encoding='utf-8') as f:
                comment_lines = []
                for line in lines:
                    line_stripped = line.strip()
                    if line_stripped.startswith('#') or line_stripped == '':
                        comment_lines.append(line)
                
                for comment in comment_lines:
                    if comment.strip():
                        f.write(comment)
                
                for p in remaining_prompts:
                    f.write(p + '\n')
            
            logger.info(f"✅ Prompt consumed. {len(remaining_prompts)} prompts remaining.")
            return prompt
        
        else:
            # No prompts in file - Generate from memory!
            logger.info("📝 No prompts in file. Generating smart prompt from memory...")
            smart_prompt = memory.generate_smart_prompt()
            logger.info(f"🧠 Smart prompt: {smart_prompt}")
            return smart_prompt
            
    except FileNotFoundError:
        logger.warning(f"{PROMPTS_FILE} not found. Generating from memory...")
        return memory.generate_smart_prompt()
    except Exception as e:
        logger.error(f"Error reading prompts: {e}")
        return memory.generate_smart_prompt()

# ============================================================
# GENERATE AI IMAGE
# ============================================================

def generate_ai_image_from_prompt(prompt, size="1024x1024"):
    """Generate an image using free Pollinations.ai API"""
    try:
        logger.info("🎨 Generating AI image...")
        
        import urllib.parse
        encoded_prompt = urllib.parse.quote(prompt)
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true"
        
        logger.info("✅ AI image generated successfully!")
        return image_url
        
    except Exception as e:
        logger.error(f"❌ AI generation failed: {e}")
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
        logger.error(f"❌ Download failed: {e}")
    return False

# ============================================================
# GET IMAGE TO POST - WITH MEMORY
# ============================================================

def get_image_to_post():
    """
    Priority: 
    1. Check for user uploaded images
    2. If no images, check prompts.txt
    3. If no prompts, generate from memory
    """
    
    # Create directories
    os.makedirs(WATCH_DIRECTORY, exist_ok=True)
    os.makedirs(POSTED_DIRECTORY, exist_ok=True)
    os.makedirs(AI_IMAGE_DIRECTORY, exist_ok=True)
    
    # ============================================================
    # STEP 1: Check for user uploaded images
    # ============================================================
    
    image_files = []
    for ext in ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.webp']:
        image_files.extend(Path(WATCH_DIRECTORY).glob(ext))
    
    posted_files = set()
    for ext in ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.webp']:
        posted_files.update(Path(POSTED_DIRECTORY).glob(ext))
    
    new_images = [f for f in image_files if f not in posted_files]
    
    if new_images:
        image_path = new_images[0]
        logger.info(f"📸 Using uploaded photo: {image_path}")
        
        posted_path = Path(POSTED_DIRECTORY) / image_path.name
        shutil.move(str(image_path), str(posted_path))
        
        # Store in memory
        memory.add_post({
            "image_source": "User uploaded",
            "success": True,
            "id": "user_upload"
        })
        
        return str(posted_path), "User uploaded photo"
    
    # ============================================================
    # STEP 2: No user image - Get prompt (from file or memory)
    # ============================================================
    
    logger.info("No user images found. Getting prompt...")
    
    # Show learning status
    stats = memory.get_statistics()
    logger.info(f"🧠 Memory Stats: {stats['total_posts']} posts, Stage: {stats['evolution_stage']}")
    
    # Get prompt (from file or generated from memory)
    prompt = read_and_consume_prompt()
    
    if not prompt:
        logger.error("❌ No prompt available!")
        return None, None
    
    # Generate AI image
    image_url = generate_ai_image_from_prompt(prompt)
    if not image_url:
        logger.error("❌ AI image generation failed!")
        return None, None
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    image_path = Path(AI_IMAGE_DIRECTORY) / f"ai_image_{timestamp}.jpg"
    
    if download_image(image_url, image_path):
        logger.info(f"✅ AI image saved: {image_path}")
        
        # Learn from this prompt
        memory.learn_from_prompt(prompt, str(image_path))
        
        # Store in memory
        memory.add_post({
            "image_source": "AI Generated",
            "prompt": prompt,
            "success": True,
            "id": f"ai_{timestamp}"
        })
        
        # Show memory summary
        summary = memory.get_summary()
        logger.info(summary)
        
        return str(image_path), f"AI Generated: {prompt}"
    else:
        logger.error("❌ Failed to save AI image!")
        return None, None

# ============================================================
=======
>>>>>>> 991c44e90d4fae9759c637b63fb5909da2503cc6
# DAILY PUBLISH
# ============================================================

def publish_daily():
<<<<<<< HEAD
    """Main function: Daily post with smart captions (NO DATE)"""
=======
    """Main function: Daily post"""
>>>>>>> 991c44e90d4fae9759c637b63fb5909da2503cc6
    logger.info(f"🚀 Starting daily post - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    # Get image
    image_path, image_source = get_image_to_post()
    
    if not image_path:
<<<<<<< HEAD
        logger.warning("⚠️ No image available!")
        logger.warning("⚠️ Skipping today's post.")
        return False
    
    logger.info(f"📸 Image source: {image_source}")
    
    # ============================================================
    # GENERATE SMART CAPTION (NO DATE)
    # ============================================================
    
    # Get the prompt that was used
    prompt = ""
    if "AI Generated" in image_source:
        # Extract prompt from image_source
        prompt = image_source.replace("AI Generated: ", "")
    else:
        # For user uploads, use a generic description
        prompt = "user uploaded photo"
    
    # Generate smart caption
    caption = generate_smart_caption(prompt, image_source)
    
    logger.info(f"📝 Generated caption: {caption[:100]}...")
=======
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
>>>>>>> 991c44e90d4fae9759c637b63fb5909da2503cc6
    
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
    
<<<<<<< HEAD
    logger.info(f"📊 Total: {successful}/{len(results)} posts published successfully")
    
    # Show memory stats
    stats = memory.get_statistics()
    logger.info(f"🧠 Memory: {stats['total_posts']} total posts, {stats['ai_generated']} AI generated")
    logger.info(f"🧠 Evolution Stage: {stats['evolution_stage']}")
=======
    logger.info(f"Total: {successful}/{len(results)} posts published successfully")
>>>>>>> 991c44e90d4fae9759c637b63fb5909da2503cc6
    
    return successful > 0

if __name__ == "__main__":
    publish_daily()