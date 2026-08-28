import random
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class SmartDecisionEngine:
    def __init__(self, memory_manager):
        self.memory = memory_manager
        self.learning = memory_manager.learning

    def get_image_to_post(self, user_images, ai_images, prompts):
        logger.info(f"📊 Available: {len(user_images)} user, {len(ai_images)} AI, {len(prompts)} prompts")

        if user_images and len(user_images) > 0:
            try:
                user_images.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                image_path = user_images[0]
                logger.info(f"📸 Using user image: {image_path.name}")

                return {
                    "source": "user_upload",
                    "image_path": str(image_path),
                    "prompt": "user uploaded photo"
                }
            except Exception as e:
                logger.error(f"Error processing user image: {e}")

        if prompts and len(prompts) > 0:
            try:
                prompt = prompts[0]
                logger.info(f"🎨 Generating AI from prompt: {prompt[:100]}...")

                return {
                    "source": "generate_ai",
                    "prompt": prompt,
                    "image_path": None
                }
            except Exception as e:
                logger.error(f"Error getting prompt: {e}")

        if ai_images and len(ai_images) > 0:
            try:
                ai_images.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                image_path = ai_images[0]
                logger.info(f"🤖 Using AI image: {image_path.name}")

                return {
                    "source": "ai_generated",
                    "image_path": str(image_path),
                    "prompt": "AI generated image"
                }
            except Exception as e:
                logger.error(f"Error processing AI image: {e}")

        logger.info("🧠 No prompts or images - generating from business memory")
        try:
            prompt = self.memory.generate_business_prompt()
            if prompt:
                return {
                    "source": "business_memory",
                    "prompt": prompt,
                    "image_path": None
                }
        except Exception as e:
            logger.error(f"Error generating business prompt: {e}")

        logger.warning("⚠️ All options failed, using fallback")
        return {
            "source": "fallback",
            "prompt": "A modern professional business environment with employees collaborating, 4K quality",
            "image_path": None
        }

    def get_caption(self, prompt, image_source):
        from config import AD_TEMPLATES, HASHTAGS, CAPTION_TEMPLATE

        if not prompt:
            prompt = "Business content"

        prompt_lower = prompt.lower() if prompt else ""

        content_types = {
            "office": ["office", "workspace", "desk", "meeting", "boardroom", "corporate"],
            "business": ["business", "professional", "company", "enterprise"],
            "technology": ["technology", "tech", "digital", "innovation", "futuristic", "holographic"],
            "team": ["team", "collaborating", "employees", "staff", "together"],
            "success": ["success", "achievement", "goal", "growth", "leadership", "vision"]
        }

        ad_type = "default"
        for key, words in content_types.items():
            if any(word in prompt_lower for word in words):
                ad_type = key
                break

        try:
            business_type = self.memory.learning.get("business_type", "")
            if "Technology" in business_type:
                ad_type = "technology"
            elif "Financial" in business_type:
                ad_type = "business"
            elif "HR" in business_type or "Team" in business_type:
                ad_type = "team"
        except:
            pass

        ad_text = random.choice(AD_TEMPLATES.get(ad_type, AD_TEMPLATES["default"]))

        if "user" in image_source:
            content = "📸 Amazing content from our team!"
        elif "AI" in image_source or "generate" in image_source:
            content = f"🤖 {prompt[:200]}..." if len(prompt) > 200 else f"🤖 {prompt}"
        else:
            content = f"✨ {prompt[:200]}..." if prompt and len(prompt) > 200 else f"✨ {prompt}"

        return CAPTION_TEMPLATE.format(
            ad_text=ad_text,
            content=content,
            HASHTAGS=HASHTAGS
        )