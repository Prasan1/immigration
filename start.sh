#!/bin/bash

echo "==============================================="
echo "Immigration Documents Portal - Setup & Start"
echo "==============================================="
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt
echo "✓ Dependencies installed"

# Check if .env exists
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠️  WARNING: .env file not found!"
    echo "Please create a .env file based on .env.example"
    echo "You need to configure:"
    echo "  - Clerk API keys (for authentication)"
    echo "  - Stripe API keys (for payments)"
    echo ""
    cp .env.example .env
    echo "✓ Created .env file from template"
    echo "Please edit .env and add your API keys before continuing."
    echo ""
    read -p "Press Enter to continue when ready..."
fi

# Check if database exists
if [ ! -f "immigration.db" ]; then
    echo ""
    echo "Initializing database..."
    python init_db.py
    echo "✓ Database initialized with sample data"
fi

echo ""
echo "==============================================="
echo "Starting Flask application..."
echo "==============================================="
echo ""
echo "Application will be available at:"
echo "  👉 http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python app.py
