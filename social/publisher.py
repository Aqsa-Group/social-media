import logging
import requests
from pathlib import Path
from urllib.parse import urlparse

from config import IMAGE_URL, PLATFORMS, PUBLIC_IMAGE_BASE_URL
from social.facebook import post_to_facebook
from social.instagram import post_to_instagram
from social.instagram_story import post_to_instagram_story
from social.telegram import post_to_telegram

logger = logging.getLogger(__name__)

print("=" * 60)
print("✅ NEW publisher.py LOADED")
print("=" * 60)


def to_public_image_url(image_url):
    """Convert a project image path to the HTTPS URL Instagram can fetch."""
    if image_url is None:
        if IMAGE_URL:
            return IMAGE_URL
        raise ValueError("No image was selected and IMAGE_URL is not configured")

    parsed_url = urlparse(str(image_url))
    if parsed_url.scheme in {"http", "https"} and parsed_url.netloc:
        return str(image_url)

    image_path = Path(str(image_url).replace("\\", "/"))
    path_parts = image_path.parts
    for directory in ("uploads", "ai_generated", "posted"):
        try:
            directory_index = path_parts.index(directory)
        except ValueError:
            continue

        filename_parts = path_parts[directory_index + 1:]
        if filename_parts:
            return f"{PUBLIC_IMAGE_BASE_URL}/images/{directory}/{Path(*filename_parts).as_posix()}"

    raise ValueError(f"Unsupported local image path: {image_url}")


def post_to_all_platforms(caption, image_url=None):
    """
    Post to all enabled platforms.
    Returns:
        {
            "facebook": True/False,
            "instagram": True/False,
            "instagram_story": True/False,
            "telegram": True/False
        }
    """

    image_url = to_public_image_url(image_url)

    try:
        image_response = requests.get(image_url, stream=True, timeout=15)
        content_type = image_response.headers.get("Content-Type", "").lower()
        if image_response.status_code != 200 or not content_type.startswith("image/"):
            logger.error(
                "❌ Public image is not reachable: %s (status %s, content type %s)",
                image_url,
                image_response.status_code,
                content_type or "missing",
            )
            return {platform: False for platform, enabled in PLATFORMS.items() if enabled}
    except requests.RequestException as e:
        logger.error("❌ Could not validate public image URL %s: %s", image_url, e)
        return {platform: False for platform, enabled in PLATFORMS.items() if enabled}

    logger.info("==========================================")
    logger.info("🚀 Starting social media publishing")
    logger.info(f"📷 Image: {image_url}")
    logger.info(f"⚙️ Platforms: {PLATFORMS}")
    logger.info("==========================================")

    results = {}

    # -------------------------------------------------------
    # Facebook
    # -------------------------------------------------------
    if PLATFORMS.get("facebook", True):
        try:
            logger.info("📤 Posting to Facebook...")
            results["facebook"] = post_to_facebook(caption, image_url)
        except Exception as e:
            logger.exception(f"❌ Facebook exception: {e}")
            results["facebook"] = False

    # -------------------------------------------------------
    # Instagram Feed
    # -------------------------------------------------------
    if PLATFORMS.get("instagram", True):
        try:
            logger.info("📤 Posting to Instagram Feed...")
            results["instagram"] = post_to_instagram(caption, image_url)
        except Exception as e:
            logger.exception(f"❌ Instagram Feed exception: {e}")
            results["instagram"] = False

    # -------------------------------------------------------
    # Instagram Story
    # -------------------------------------------------------
    if PLATFORMS.get("instagram_story", True):
        try:
            logger.info("📤 Posting to Instagram Story...")
            results["instagram_story"] = post_to_instagram_story(image_url)
        except Exception as e:
            logger.exception(f"❌ Instagram Story exception: {e}")
            results["instagram_story"] = False

    # -------------------------------------------------------
    # Telegram
    # -------------------------------------------------------
    if PLATFORMS.get("telegram", False):
        try:
            logger.info("📤 Posting to Telegram...")
            results["telegram"] = post_to_telegram(caption, image_url)
        except Exception as e:
            logger.exception(f"❌ Telegram exception: {e}")
            results["telegram"] = False

    # -------------------------------------------------------
    # Summary
    # -------------------------------------------------------
    logger.info("==========================================")
    logger.info("📊 Publishing Summary")

    for platform, status in results.items():
        logger.info(f"   {platform}: {'✅ Success' if status else '❌ Failed'}")

    success_count = sum(results.values())

    logger.info(
        f"📊 Results: {success_count}/{len(results)} successful"
    )
    logger.info("==========================================")

    return results