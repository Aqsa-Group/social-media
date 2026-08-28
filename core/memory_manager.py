# core/memory_manager.py
import json
import os
import random
from datetime import datetime
from collections import Counter
import logging

logger = logging.getLogger(__name__)

class MemoryManager:
    def __init__(self, memory_file, learning_file):
        self.memory_file = memory_file
        self.learning_file = learning_file
        self.memory = self._load_memory()
        self.learning = self._load_learning()
        
    def _load_memory(self):
        try:
            with open(self.memory_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                "total_posts": 0,
                "total_ai_generated": 0,
                "total_user_uploads": 0,
                "prompts_used": [],
                "post_history": [],
                "business_topics": [],
                "content_patterns": {}
            }
    
    def _load_learning(self):
        try:
            with open(self.learning_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                "successful_prompts": [],
                "failed_prompts": [],
                "learned_topics": [],
                "business_type": None,
                "brand_voice": None,
                "image_style_preferences": [],
                "topic_patterns": {}
            }
    
    def _save_memory(self):
        try:
            with open(self.memory_file, 'w') as f:
                json.dump(self.memory, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving memory: {e}")
    
    def _save_learning(self):
        try:
            with open(self.learning_file, 'w') as f:
                json.dump(self.learning, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving learning: {e}")
    
    def add_post(self, post_data):
        self.memory["total_posts"] += 1
        
        image_source = str(post_data.get("image_source", "")).lower().replace(" ", "_")
        if image_source in {"ai_generated", "generate_ai", "business_memory"}:
            self.memory["total_ai_generated"] += 1
        else:
            self.memory["total_user_uploads"] += 1
        
        if "prompt" in post_data and post_data["prompt"]:
            self.memory["prompts_used"].append({
                "prompt": post_data["prompt"],
                "timestamp": datetime.now().isoformat(),
                "success": post_data.get("success", False)
            })
        
        self.memory["post_history"].append({
            **post_data,
            "timestamp": datetime.now().isoformat()
        })
        
        if len(self.memory["post_history"]) > 1000:
            self.memory["post_history"] = self.memory["post_history"][-1000:]
        
        self._save_memory()
    
    def learn_from_prompt(self, prompt, image_path, success=True):
        topic = self._extract_topic(prompt)
        
        if topic:
            if topic not in self.learning["learned_topics"]:
                self.learning["learned_topics"].append(topic)
            
            if topic not in self.learning["topic_patterns"]:
                self.learning["topic_patterns"][topic] = 0
            self.learning["topic_patterns"][topic] += 1
        
        if success:
            self.learning["successful_prompts"].append({
                "prompt": prompt,
                "topic": topic,
                "image": image_path,
                "timestamp": datetime.now().isoformat()
            })
        else:
            self.learning["failed_prompts"].append({
                "prompt": prompt,
                "topic": topic,
                "timestamp": datetime.now().isoformat()
            })
        
        self._detect_business_type()
        self._save_learning()
    
    def _extract_topic(self, prompt):
        topics = ["office", "business", "technology", "team", "success", "modern", 
                 "professional", "creative", "corporate", "startup", "financial", 
                 "global", "digital", "network", "leadership", "innovation", "growth"]
        
        prompt_lower = prompt.lower()
        for topic in topics:
            if topic in prompt_lower:
                return topic
        return None
    
    def _detect_business_type(self):
        if not self.learning["successful_prompts"]:
            return
        
        topics = [p.get("topic") for p in self.learning["successful_prompts"] if p.get("topic")]
        
        if topics:
            common_topic = Counter(topics).most_common(1)[0][0]
            
            business_mapping = {
                "office": "Corporate/Office Business",
                "business": "General Business",
                "technology": "Technology/IT Business",
                "team": "HR/Team Management",
                "success": "Consulting/Coaching",
                "financial": "Financial Services",
                "digital": "Digital Marketing/IT",
                "network": "Network/IT Services",
                "global": "International Business",
                "leadership": "Leadership/Management",
                "innovation": "Innovation/Tech"
            }
            
            self.learning["business_type"] = business_mapping.get(common_topic, "General Business")
            self._save_learning()
    
    def understand_business(self):
        if self.learning["business_type"]:
            return f"Business Type: {self.learning['business_type']}"
        
        if self.learning["successful_prompts"]:
            topics = [p.get("topic") for p in self.learning["successful_prompts"] if p.get("topic")]
            if topics:
                common = Counter(topics).most_common(1)[0][0]
                return f"Focusing on: {common.capitalize()} content"
        
        return "Still learning about your business..."
    
    def generate_business_prompt(self):
        successful = self.learning["successful_prompts"]
        
        if not successful:
            return "A modern professional business environment with employees collaborating, 4K quality"
        
        topics = [p.get("topic") for p in successful if p.get("topic")]
        
        if topics:
            topic_counts = Counter(topics)
            main_topics = [t for t, _ in topic_counts.most_common(2)]
            
            if self.learning["business_type"]:
                business_prompts = {
                    "Corporate/Office Business": "Modern corporate office with professionals collaborating in a bright workspace, clean minimalist design, business atmosphere, 4K quality",
                    "General Business": "Professional business environment with modern technology and successful professionals, corporate style, 4K quality",
                    "Technology/IT Business": "Futuristic technology concept with glowing displays and data visualization, modern IT workspace, 4K quality",
                    "HR/Team Management": "Diverse professional team collaborating in modern office, warm corporate atmosphere, 4K quality",
                    "Consulting/Coaching": "Professional consulting concept with leadership and success, modern boardroom, 4K quality",
                    "Financial Services": "Professional financial concept with modern technology, sophisticated corporate style, 4K quality",
                    "Digital Marketing/IT": "Digital marketing concept with modern technology and creative professionals, 4K quality"
                }
                
                for key, prompt in business_prompts.items():
                    if key in self.learning["business_type"]:
                        return prompt
            
            main_topic = main_topics[0] if main_topics else "business"
            
            topic_prompts = {
                "office": "Modern office environment with professionals working collaboratively, minimalist workspace, 4K quality",
                "business": "Professional business setting with corporate atmosphere and modern design, 4K quality",
                "technology": "Futuristic technology concept with innovation and modern workspace, 4K quality",
                "team": "Diverse team collaborating in modern office, professional atmosphere, 4K quality",
                "success": "Professional success and achievement concept, modern corporate setting, 4K quality"
            }
            
            if main_topic in topic_prompts:
                return topic_prompts[main_topic]
        
        return "A modern professional business environment with employees collaborating, 4K quality"
    
    def get_statistics(self):
        total_posts = self.memory["total_posts"]
        
        if total_posts == 0:
            stage = "learning"
        elif total_posts < 10:
            stage = "beginner"
        elif total_posts < 30:
            stage = "intermediate"
        elif total_posts < 50:
            stage = "advanced"
        else:
            stage = "expert"
        
        failed = len([p for p in self.memory["post_history"] if not p.get("success", True)])
        
        return {
            "total_posts": total_posts,
            "ai_generated": self.memory["total_ai_generated"],
            "user_uploads": self.memory["total_user_uploads"],
            "prompts_used": len(self.memory["prompts_used"]),
            "learned_topics": len(self.learning["learned_topics"]),
            "successful_prompts": len(self.learning["successful_prompts"]),
            "failed_posts": failed,
            "evolution_stage": stage,
            "business_type": self.learning.get("business_type", "Learning...")
        }
    
    def get_recent_posts(self, limit=10):
        return self.memory["post_history"][-limit:]
    
    def get_summary(self):
        stats = self.get_statistics()
        return f"📊 Memory: {stats['total_posts']} posts, {stats['learned_topics']} topics, Stage: {stats['evolution_stage']}, Business: {stats['business_type']}"