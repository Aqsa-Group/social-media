# run.py
import sys
import argparse
import logging
import threading
from datetime import datetime
from config import WEB_HOST, WEB_PORT

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_web():
    from app import app
    logger.info(f"🌐 Starting web interface on http://{WEB_HOST}:{WEB_PORT}")
    app.run(host=WEB_HOST, port=WEB_PORT, debug=False)

def run_scheduler():
    from core.scheduler import run_scheduler
    logger.info("🔄 Starting scheduler...")
    run_scheduler()

def run_once():
    from core.ai_poster import publish_daily
    logger.info("🚀 Posting once...")
    publish_daily()

def run_all():
    web_thread = threading.Thread(target=run_web, name="web-server", daemon=True)
    web_thread.start()
    run_scheduler()

def main():
    parser = argparse.ArgumentParser(description='Social Media Automation')
    parser.add_argument('--mode', choices=['web', 'scheduler', 'once', 'all'], 
                       default='web', help='Run mode')
    
    args = parser.parse_args()
    
    if args.mode == 'web':
        run_web()
    elif args.mode == 'scheduler':
        run_scheduler()
    elif args.mode == 'once':
        run_once()
    elif args.mode == 'all':
        run_all()

if __name__ == '__main__':
    main()