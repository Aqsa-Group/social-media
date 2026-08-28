# app.py
from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import json
from datetime import datetime
from werkzeug.utils import secure_filename
import logging
from config import AI_GENERATED_DIR, POSTED_DIR, PROJECT_DIR, UPLOAD_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = str(UPLOAD_DIR)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'development-only-change-me')
ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}

# Create directories
for directory in (UPLOAD_DIR, AI_GENERATED_DIR, POSTED_DIR, PROJECT_DIR / 'data', PROJECT_DIR / 'logs'):
    directory.mkdir(parents=True, exist_ok=True)

from core.memory_manager import MemoryManager
from core.smart_decisions import SmartDecisionEngine
from core.ai_poster import publish_daily

# Initialize
memory = MemoryManager(PROJECT_DIR / 'data' / 'memory.json', PROJECT_DIR / 'data' / 'learning.json')
decision_engine = SmartDecisionEngine(memory)

@app.route('/')
@app.route('/social-media/app/')
def dashboard():
    stats = memory.get_statistics()
    recent_posts = memory.get_recent_posts(10)
    business = memory.understand_business()
    
    return render_template('dashboard.html',
                         stats=stats,
                         recent_posts=recent_posts,
                         business=business)

@app.route('/prompts')
@app.route('/social-media/app/prompts')
def prompts_page():
    prompts = get_all_prompts()
    categories = get_prompt_categories()
    return render_template('prompts.html', prompts=prompts, categories=categories)

@app.route('/upload')
@app.route('/social-media/app/upload')
def upload_page():
    return render_template('upload.html')

@app.route('/analytics')
@app.route('/social-media/app/analytics')
def analytics_page():
    stats = memory.get_statistics()
    return render_template('analytics.html', stats=stats)

@app.route('/settings')
@app.route('/social-media/app/settings')
def settings_page():
    return render_template('settings.html')

@app.route('/api/stats')
@app.route('/social-media/app/api/stats')
def api_stats():
    return jsonify(memory.get_statistics())

@app.route('/api/posts')
@app.route('/social-media/app/api/posts')
def api_posts():
    return jsonify(memory.get_recent_posts(50))

@app.route('/api/post_now', methods=['POST'])
@app.route('/social-media/app/api/post_now', methods=['POST'])
def api_post_now():
    try:
        success = publish_daily()
        return jsonify({'success': success, 'message': 'Posted successfully!' if success else 'Posting failed!'})
    except Exception as e:
        logger.error(f"Post error: {e}")
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/upload', methods=['POST'])
@app.route('/social-media/app/api/upload', methods=['POST'])
def api_upload():
    if 'image' not in request.files:
        return jsonify({'success': False, 'error': 'No image uploaded'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400
    
    if file:
        filename = secure_filename(file.filename)
        extension = os.path.splitext(filename)[1].lower()
        if extension not in ALLOWED_IMAGE_EXTENSIONS:
            return jsonify({'success': False, 'error': 'Only JPG, PNG, GIF, and WEBP images are allowed'}), 400

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return jsonify({'success': True, 'filename': filename, 'message': 'Image uploaded successfully!'})
    
    return jsonify({'success': False, 'error': 'Invalid file'}), 400

@app.route('/api/prompts', methods=['GET', 'POST'])
@app.route('/social-media/app/api/prompts', methods=['GET', 'POST'])
def api_prompts():
    if request.method == 'GET':
        return jsonify(get_all_prompts())
    
    data = request.json
    if data:
        category = data.get('category', 'default')
        prompt = data.get('prompt', '').strip()
        if prompt:
            add_prompt(category, prompt)
            return jsonify({'success': True, 'message': 'Prompt added!'})
    return jsonify({'success': False, 'error': 'No prompt provided'}), 400

@app.route('/api/prompts/<int:index>', methods=['DELETE'])
@app.route('/social-media/app/api/prompts/<int:index>', methods=['DELETE'])
def api_delete_prompt(index):
    prompts = get_all_prompts()
    if 0 <= index < len(prompts):
        prompts.pop(index)
        save_all_prompts(prompts)
        return jsonify({'success': True})
    return jsonify({'success': False}), 404

@app.route('/images/uploads/<filename>')
@app.route('/social-media/app/images/uploads/<filename>')
def serve_upload(filename):
    return send_from_directory(UPLOAD_DIR, filename)

@app.route('/images/ai_generated/<filename>')
@app.route('/social-media/app/images/ai_generated/<filename>')
def serve_ai(filename):
    return send_from_directory(AI_GENERATED_DIR, filename)

@app.route('/images/posted/<filename>')
@app.route('/social-media/app/images/posted/<filename>')
def serve_posted(filename):
    return send_from_directory(POSTED_DIR, filename)

@app.route('/social-media/app/images/<path:filename>')
def serve_repository_image(filename):
    """Serve an image through the public repository URL used by social APIs."""
    image_path = (PROJECT_DIR / 'images' / filename).resolve()
    image_directories = (UPLOAD_DIR, AI_GENERATED_DIR, POSTED_DIR)

    if '/' not in filename and '\\' not in filename:
        matching_paths = [directory / filename for directory in image_directories if (directory / filename).is_file()]
        if matching_paths:
            image_path = matching_paths[0].resolve()

    if not any(image_path.is_relative_to(directory.resolve()) for directory in image_directories):
        return jsonify({'error': 'Image not found'}), 404

    if not image_path.is_file():
        return jsonify({'error': 'Image not found'}), 404

    return send_from_directory(image_path.parent, image_path.name)

def get_all_prompts():
    prompts = []
    prompts_dir = PROJECT_DIR / 'prompts'
    if os.path.exists(prompts_dir):
        for file in os.listdir(prompts_dir):
            if file.endswith('.txt'):
                category = file.replace('.txt', '')
                with open(os.path.join(prompts_dir, file), 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            prompts.append({'category': category, 'text': line})
    return prompts

def get_prompt_categories():
    categories = []
    prompts_dir = PROJECT_DIR / 'prompts'
    if os.path.exists(prompts_dir):
        for file in os.listdir(prompts_dir):
            if file.endswith('.txt'):
                categories.append(file.replace('.txt', ''))
    if not categories:
        categories.append('default')
    return categories

def add_prompt(category, prompt):
    filepath = PROJECT_DIR / 'prompts' / f'{category}.txt'
    with open(filepath, 'a', encoding='utf-8') as f:
        f.write(f'\n{prompt}')

def save_all_prompts(prompts):
    prompts_dir = PROJECT_DIR / 'prompts'
    if os.path.exists(prompts_dir):
        for file in os.listdir(prompts_dir):
            if file.endswith('.txt'):
                os.remove(prompts_dir / file)
    
    categories = {}
    for p in prompts:
        cat = p.get('category', 'default')
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(p['text'])
    
    for cat, texts in categories.items():
        filepath = prompts_dir / f'{cat}.txt'
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# {cat.upper()} Prompts\n")
            f.write("# Add your prompts here (one per line)\n\n")
            for text in texts:
                f.write(text + '\n')

if __name__ == '__main__':
    default_prompts_file = PROJECT_DIR / 'prompts' / 'default.txt'
    if not default_prompts_file.exists():
        with open(default_prompts_file, 'w', encoding='utf-8') as f:
            f.write("# DEFAULT Prompts\n")
            f.write("# Add your prompts here (one per line)\n\n")
            f.write("Modern professional office with employees collaborating in a bright workspace, 4K quality\n")
            f.write("Professional business team meeting with laptops and coffee, modern conference room\n")
            f.write("Futuristic technology concept with holographic displays and data visualization\n")
    
    from config import WEB_HOST, WEB_PORT
    app.run(host=WEB_HOST, port=WEB_PORT, debug=False)