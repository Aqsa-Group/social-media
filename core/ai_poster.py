# core/ai_poster.py
import requests
import os
import random
import logging
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from config import *
from core.memory_manager import MemoryManager
from core.smart_decisions import SmartDecisionEngine

LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler(LOG_DIR / "app.log"), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

memory = MemoryManager(PROJECT_DIR / "data" / "memory.json", PROJECT_DIR / "data" / "learning.json")
decision_engine = SmartDecisionEngine(memory)

def get_user_images():
    image_files = []
    upload_dir = UPLOAD_DIR
    if upload_dir.exists():
        for ext in ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.webp']:
            image_files.extend(upload_dir.glob(ext))
    
    posted_dir = POSTED_DIR
    posted_files = set()
    if posted_dir.exists():
        for ext in ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.webp']:
            posted_files.update(posted_dir.glob(ext))
    
    return [f for f in image_files if f not in posted_files]

def get_ai_images():
    ai_dir = AI_GENERATED_DIR
    if not ai_dir.exists():
        return []
    images = []
    for ext in ['*.jpg', '*.jpeg', '*.png']:
        images.extend(ai_dir.glob(ext))
    return images

def get_prompts_from_file():
    try:
        prompts = []
        prompts_dir = PROJECT_DIR / "prompts"
        if prompts_dir.exists():
            for file in prompts_dir.glob("*.txt"):
                with open(file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            prompts.append(line)
        return prompts
    except Exception as e:
        logger.error(f"Error reading prompts: {e}")
        return []

def consume_prompt():
    try:
        prompts_dir = PROJECT_DIR / "prompts"
        if not prompts_dir.exists():
            return None
        
        for file in prompts_dir.glob("*.txt"):
            with open(file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            prompts = []
            comments = []
            for line in lines:
                stripped = line.strip()
                if stripped and not stripped.startswith('#'):
                    prompts.append(stripped)
                else:
                    comments.append(line)
            
            if prompts:
                prompt = prompts[0]
                remaining = prompts[1:]
                
                with open(file, 'w', encoding='utf-8') as f:
                    for comment in comments:
                        if comment.strip():
                            f.write(comment)
                    for p in remaining:
                        f.write(p + '\n')
                return prompt
        return None
    except Exception as e:
        logger.error(f"Error consuming prompt: {e}")
        return None

def generate_ai_image(prompt):
    try:
        import urllib.parse
        encoded = urllib.parse.quote(prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024&nologo=true"
        
        logger.info(f"🎨 Generating image from: {prompt[:100]}...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        AI_GENERATED_DIR.mkdir(parents=True, exist_ok=True)
        image_path = AI_GENERATED_DIR / f"ai_image_{timestamp}.jpg"
        
        response = requests.get(url, timeout=60)
        
        if response.status_code == 200:
            with open(image_path, 'wb') as f:
                f.write(response.content)
            
            if os.path.exists(image_path) and os.path.getsize(image_path) > 1000:
                logger.info(f"✅ AI image generated")
                return str(image_path)
            else:
                logger.error("❌ Image file is too small or corrupted")
                return None
        
        logger.error(f"❌ AI generation failed with status: {response.status_code}")
        return None
        
    except requests.exceptions.Timeout:
        logger.error("❌ AI generation timed out")
        return None
    except Exception as e:
        logger.error(f"❌ AI generation error: {e}")
        return None

def publish_daily():
    logger.info(f"🚀 Starting publish at {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    user_images = get_user_images()
    ai_images = get_ai_images()
    prompts = get_prompts_from_file()
    
    logger.info(f"📊 Available: {len(user_images)} user, {len(ai_images)} AI, {len(prompts)} prompts")
    
    decision = decision_engine.get_image_to_post(user_images, ai_images, prompts)
    logger.info(f"🧠 Decision: {decision['source']}")
    
    image_path = None
    prompt = decision.get('prompt', '')
    
    if decision['source'] == 'user_upload':
        image_path = decision.get('image_path')
        if image_path:
            logger.info(f"📸 Using user image: {os.path.basename(image_path)}")
        else:
            logger.error("❌ User image path is None")
            return False
        
    elif decision['source'] == 'ai_generated':
        image_path = decision.get('image_path')
        if image_path:
            logger.info(f"🤖 Using AI image: {os.path.basename(image_path)}")
        else:
            logger.error("❌ AI image path is None")
            return False
        
    elif decision['source'] == 'generate_ai':
        prompt = decision.get('prompt', '')
        if not prompt:
            logger.error("❌ No prompt provided for AI generation")
            return False
            
        logger.info(f"🎨 Generating AI image from prompt: {prompt[:100]}...")
        image_path = generate_ai_image(prompt)
        if image_path:
            consume_prompt()
        else:
            logger.error("❌ Failed to generate AI image")
            return False
        
    else:  # business_memory
        prompt = decision.get('prompt', '')
        if not prompt:
            logger.error("❌ No prompt from business memory")
            return False
            
        logger.info(f"🧠 Generating from business memory: {prompt[:100]}...")
        image_path = generate_ai_image(prompt)
        if not image_path:
            logger.error("❌ Failed to generate AI image from business memory")
            return False
    
    if not image_path or not os.path.exists(image_path):
        logger.error(f"❌ Image not found: {image_path}")
        return False
    
    caption = decision_engine.get_caption(prompt, decision['source'])
    logger.info(f"📝 Caption: {caption[:100]}...")
    
    # ============================================================
    # ✅ FIX: Use IMAGE_URL (public URL) for all platforms
    # ============================================================
    from social.publisher import post_to_all_platforms
    
    # Post to ALL platforms (Facebook, Instagram Feed, Instagram Story)
    # Using the public URL that works for both Feed and Story
    results = post_to_all_platforms(caption, image_path)
    
    successful = sum(1 for success in results.values() if success)

    if successful > 0 and decision.get('source') in {'user_upload', 'ai_generated', 'generate_ai', 'business_memory'}:
        posted_path = POSTED_DIR / Path(image_path).name
        posted_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            os.replace(image_path, posted_path)
            image_path = str(posted_path)
        except OSError as e:
            logger.warning(f"Could not archive AI image after posting: {e}")
    
    # Store in memory
    memory.add_post({
        "image_source": decision.get('source', 'unknown'),
        "prompt": prompt,
        "success": successful > 0,
        "platforms": [p for p, s in results.items() if s],
        "caption": caption,
        "image_path": image_path
    })
    
    if prompt and prompt != "user uploaded photo":
        memory.learn_from_prompt(prompt, image_path, successful > 0)
    
    logger.info(f"🧠 {memory.get_summary()}")
    logger.info(f"💡 {memory.understand_business()}")
    
    return successful > 0

if __name__ == "__main__":
    publish_daily()