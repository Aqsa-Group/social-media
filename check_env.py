# test_post.py
import os
import requests
import json
from dotenv import load_dotenv
from pathlib import Path
from config import AI_GENERATED_DIR, POSTED_DIR, UPLOAD_DIR

load_dotenv()

# Get credentials
FACEBOOK_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID")
FACEBOOK_PAGE_ACCESS_TOKEN = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN")
IG_USER_ID = os.getenv("IG_USER_ID")
IG_ACCESS_TOKEN = os.getenv("IG_ACCESS_TOKEN")

def test_facebook():
    print("\n" + "="*50)
    print("📤 TESTING FACEBOOK POST")
    print("="*50)
    
    if not FACEBOOK_PAGE_ID or not FACEBOOK_PAGE_ACCESS_TOKEN:
        print("❌ Facebook credentials missing!")
        return False
    
    # First, check if we can access the page
    print(f"📋 Page ID: {FACEBOOK_PAGE_ID}")
    print("🔑 Token configured: yes")
    
    # Test page access
    url = f"https://graph.facebook.com/v23.0/{FACEBOOK_PAGE_ID}"
    params = {"access_token": FACEBOOK_PAGE_ACCESS_TOKEN}
    response = requests.get(url, params=params, timeout=30)
    
    if response.status_code != 200:
        print(f"❌ Cannot access page: {response.json()}")
        return False
    
    print(f"✅ Page accessible: {response.json().get('name')}")
    
    # Find an image to test with
    test_image = find_test_image()
    if not test_image:
        print("❌ No test image found! Please upload an image first.")
        return False
    
    print(f"📸 Using image: {test_image}")
    
    # Try to post
    url = f"https://graph.facebook.com/v23.0/{FACEBOOK_PAGE_ID}/photos"
    with open(test_image, 'rb') as img:
        files = {'source': img}
        payload = {
            'caption': 'Test post from automation system 🚀',
            'access_token': FACEBOOK_PAGE_ACCESS_TOKEN
        }
        response = requests.post(url, files=files, data=payload, timeout=30)
        result = response.json()
        
        print(f"📬 Response: {json.dumps(result, indent=2)}")
        
        if "id" in result:
            print(f"✅ Facebook post successful! ID: {result['id']}")
            return True
        else:
            print(f"❌ Facebook post failed: {result.get('error', {}).get('message')}")
            return False

def test_instagram():
    print("\n" + "="*50)
    print("📤 TESTING INSTAGRAM POST")
    print("="*50)
    
    if not IG_USER_ID or not IG_ACCESS_TOKEN:
        print("❌ Instagram credentials missing!")
        return False
    
    print(f"📋 User ID: {IG_USER_ID}")
    print("🔑 Token configured: yes")
    
    # Test user access
    url = f"https://graph.instagram.com/v24.0/{IG_USER_ID}"
    params = {"access_token": IG_ACCESS_TOKEN}
    response = requests.get(url, params=params, timeout=30)
    
    if response.status_code != 200:
        print(f"❌ Cannot access user: {response.json()}")
        return False
    
    print(f"✅ User accessible: {response.json().get('username')}")
    
    # Find an image to test with
    test_image = find_test_image()
    if not test_image:
        print("❌ No test image found! Please upload an image first.")
        return False
    
    print(f"📸 Using image: {test_image}")
    
    # For Instagram, we need a public URL
    # Try with local server URL
    filename = os.path.basename(test_image)
    
    # Option 1: Try ngrok or public URL
    from social.publisher import to_public_image_url
    image_url = to_public_image_url(test_image)
    
    # Option 2: Try ngrok URL (uncomment if using ngrok)
    # image_url = f"https://YOUR_NGROK_URL.ngrok.io/images/ai_generated/{filename}"
    
    # Option 3: Try uploads folder
    # image_url = f"http://192.168.1.171:5000/images/uploads/{filename}"
    
    print(f"📸 Image URL: {image_url}")
    
    # First create media container
    create_url = f"https://graph.instagram.com/v24.0/{IG_USER_ID}/media"
    payload = {
        "image_url": image_url,
        "caption": "Test post from automation system 🚀",
        "access_token": IG_ACCESS_TOKEN
    }
    
    print(f"📬 Creating media container...")
    response = requests.post(create_url, data=payload, timeout=30)
    result = response.json()
    
    print(f"📬 Response: {json.dumps(result, indent=2)}")
    
    if "id" not in result:
        print(f"❌ Instagram media creation failed: {result.get('error', {}).get('message')}")
        return False
    
    creation_id = result["id"]
    print(f"✅ Media container created: {creation_id}")
    
    # Now publish it
    import time
    print(f"⏳ Waiting for processing...")
    time.sleep(5)
    
    publish_url = f"https://graph.instagram.com/v24.0/{IG_USER_ID}/media_publish"
    publish_payload = {
        "creation_id": creation_id,
        "access_token": IG_ACCESS_TOKEN
    }
    
    print(f"📬 Publishing media...")
    publish_response = requests.post(publish_url, data=publish_payload, timeout=30)
    publish_result = publish_response.json()
    
    print(f"📬 Response: {json.dumps(publish_result, indent=2)}")
    
    if "id" in publish_result:
        print(f"✅ Instagram post successful! ID: {publish_result['id']}")
        return True
    else:
        print(f"❌ Instagram publish failed: {publish_result.get('error', {}).get('message')}")
        return False

def find_test_image():
    """Find an image to test with"""
    # Check ai_generated folder
    ai_dir = AI_GENERATED_DIR
    if ai_dir.exists():
        for ext in ['*.jpg', '*.jpeg', '*.png']:
            images = list(ai_dir.glob(ext))
            if images:
                return str(images[0])
    
    # Check uploads folder
    upload_dir = UPLOAD_DIR
    if upload_dir.exists():
        for ext in ['*.jpg', '*.jpeg', '*.png', '*.gif']:
            images = list(upload_dir.glob(ext))
            if images:
                return str(images[0])
    
    # Check posted folder
    posted_dir = POSTED_DIR
    if posted_dir.exists():
        for ext in ['*.jpg', '*.jpeg', '*.png', '*.gif']:
            images = list(posted_dir.glob(ext))
            if images:
                return str(images[0])
    
    return None

if __name__ == "__main__":
    print("🚀 Starting Social Media Test")
    print("="*50)
    
    # Test Facebook
    fb_success = test_facebook()
    
    # Test Instagram
    ig_success = test_instagram()
    
    # Summary
    print("\n" + "="*50)
    print("📊 TEST SUMMARY")
    print("="*50)
    print(f"Facebook: {'✅ SUCCESS' if fb_success else '❌ FAILED'}")
    print(f"Instagram: {'✅ SUCCESS' if ig_success else '❌ FAILED'}")