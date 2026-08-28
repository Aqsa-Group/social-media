# scheduler.py
import schedule
import time
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def run_scheduler(post_time="09:00"):
    """Run the scheduler with daily posts"""
    
    from ai_poster import publish_daily
    
    def run_post():
        logger.info(f"⏰ Running scheduled post at {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        publish_daily()
    
    # Schedule daily
    schedule.every().day.at(post_time).do(run_post)
    
    # Run once on startup (optional)
    # run_post()  # Uncomment to run on startup
    
    logger.info(f"🔄 Scheduler started. Will post daily at {post_time}")
    logger.info(f"Next run: {schedule.next_run()}")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        logger.info("👋 Scheduler stopped")