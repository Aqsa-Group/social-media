# core/scheduler.py
import schedule
import time
import logging
import random
from datetime import datetime, timedelta
from core.memory_manager import MemoryManager
from config import PROJECT_DIR

logger = logging.getLogger(__name__)

def run_scheduler():
    from core.ai_poster import publish_daily
    
    def run_post():
        logger.info(f"⏰ Running post at {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        publish_daily()
        schedule_next()
    
    def schedule_next():
        schedule.clear()
        
        hour = random.randint(8, 22)
        minute = random.randint(0, 59)
        random_time = f"{hour:02d}:{minute:02d}"
        
        memory = MemoryManager(PROJECT_DIR / "data" / "memory.json", PROJECT_DIR / "data" / "learning.json")
        stats = memory.get_statistics()
        
        days = 1
        if stats['total_posts'] < 5:
            days = 2
        
        post_time = datetime.now() + timedelta(days=days)
        post_time = post_time.replace(hour=hour, minute=minute, second=0)
        
        logger.info(f"⏰ Next post: {post_time.strftime('%Y-%m-%d %H:%M')} (in {days} day(s))")
        schedule.every(days).days.at(random_time).do(run_post)
    
    schedule_next()
    logger.info("🔄 Scheduler started")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        logger.info("👋 Scheduler stopped")