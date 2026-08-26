# scheduler.py
import schedule
import time
import logging
from datetime import datetime
import os

logger = logging.getLogger(__name__)

def run_scheduler(post_time="09:00"):
    """Run the scheduler with daily posts"""
    
    from ai_poster import publish_daily
    
    def run_post():
        logger.info(f"⏰ Running scheduled post at {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        publish_daily()
    
    # Schedule daily at specified time
    schedule.every().day.at(post_time).do(run_post)
    
    # Run once on startup (optional - set to False if you want to start fresh)
    # run_post()  # Uncomment to run on startup
    
    logger.info(f"🔄 Scheduler started. Will post daily at {post_time}")
    logger.info(f"Next run: {schedule.next_run()}")
    
    # Check if we should run immediately
    logger.info("💡 To run once, use: python run.py --mode once")
    logger.info("💡 To watch folder, use: python run.py --mode watch")
    logger.info("💡 To schedule, use: python run.py --mode scheduler")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        logger.info("👋 Scheduler stopped")