#!/bin/bash

echo "🚀 Social Media Automation Setup (Native)"
echo "========================================="
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Installing..."
    sudo apt-get update
    sudo apt-get install -y python3 python3-pip python3-venv
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create directories
echo "📁 Creating directories..."
mkdir -p images posted ai_generated logs

# Create .env if not exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << 'EOF'
# Social Media Credentials
OPENAI_API_KEY=your-api-key-here

FACEBOOK_PAGE_ID=your-page-id
FACEBOOK_PAGE_ACCESS_TOKEN=your-token

IG_USER_ID=your-ig-user-id
IG_ACCESS_TOKEN=your-ig-token
EOF
    echo "⚠️ Please edit .env with your credentials!"
fi

# Create prompts.txt if not exists
if [ ! -f prompts.txt ]; then
    echo "📝 Creating prompts.txt..."
    cat > prompts.txt << 'EOF'
# prompts.txt - Add your prompts here (one per line)
# Lines starting with # are ignored

A modern professional office with employees collaborating, warm lighting, clean minimalist design, business atmosphere, 4K quality

A professional business team meeting with laptops and coffee, modern conference room, natural lighting, corporate style

A futuristic business technology concept with holographic displays and data visualization, sleek modern office

A professional woman giving a presentation with confident body language, modern boardroom, bright professional lighting
EOF
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file: nano .env"
echo "2. Edit prompts.txt: nano prompts.txt"
echo "3. Run: python run.py --mode scheduler"
echo "   or: python run.py --mode watch"
echo "   or: python run.py --mode once"