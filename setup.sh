#!/bin/bash

echo "=========================================="
echo "Social Media Automation Setup"
echo "=========================================="

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "Python3 not found. Installing..."
    sudo dnf install -y python3 python3-pip
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create directories
echo "Creating directories..."
mkdir -p images/uploads images/ai_generated images/posted logs data prompts

# Create .env if not exists
if [ ! -f .env ]; then
    echo "Creating .env file..."
    echo "OPENAI_API_KEY=your-api-key-here" > .env
    echo "FACEBOOK_PAGE_ID=your-page-id" >> .env
    echo "FACEBOOK_PAGE_ACCESS_TOKEN=your-token" >> .env
    echo "IG_USER_ID=your-ig-id" >> .env
    echo "IG_ACCESS_TOKEN=your-ig-token" >> .env
    echo "WARNING: Please edit .env with your credentials!"
fi

echo ""
echo "Setup complete!"