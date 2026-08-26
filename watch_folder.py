# watch_folder.py
import time
import os
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from config import WATCH_DIRECTORY

logger = logging.getLogger(__name__)

class ImageHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            if event.src_path.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                logger.info(f"📸 New image detected: {event.src_path}")
                # Wait for file to finish writing
                time.sleep(2)
                # Only post if file still exists
                if os.path.exists(event.src_path):
                    from ai_poster import publish_daily
                    publish_daily()

def watch_and_post():
    """Watch directory and post when new images are added"""
    os.makedirs(WATCH_DIRECTORY, exist_ok=True)
    
    logger.info(f"👁️ Watching directory: {WATCH_DIRECTORY}")
    logger.info("📸 Add images to auto-post")
    logger.info("🤖 AI will generate images when no new images are available")
    logger.info("🔄 Press Ctrl+C to stop")
    
    event_handler = ImageHandler()
    observer = Observer()
    observer.schedule(event_handler, WATCH_DIRECTORY, recursive=False)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        logger.info("👋 Watcher stopped")
    
    observer.join()