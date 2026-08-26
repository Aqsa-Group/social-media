# run.py
#!/usr/bin/env python3
import sys
import os
import argparse
import logging
from datetime import datetime

# Setup logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description='Social Media Automation')
    parser.add_argument('--mode', choices=['scheduler', 'watch', 'once'], 
                       default='scheduler', help='Run mode')
    parser.add_argument('--post-time', default='09:00', 
                       help='Post time (HH:MM format)')
    
    args = parser.parse_args()
    
    logger.info(f"🚀 Starting Social Media Automation - Mode: {args.mode}")
    logger.info(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if args.mode == 'once':
        from ai_poster import publish_daily
        publish_daily()
    
    elif args.mode == 'watch':
        from watch_folder import watch_and_post
        watch_and_post()
    
    else:  # scheduler (default)
        from scheduler import run_scheduler
        run_scheduler(args.post_time)

if __name__ == "__main__":
    main()