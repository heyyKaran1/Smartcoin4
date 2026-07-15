#!/bin/bash

echo "🚀 CCI Coin - Production Deployment Script"
echo "=========================================="

if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please create .env file from .env.example"
    exit 1
fi

echo "✓ Environment file found"

echo "\n📦 Installing dependencies..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✓ Dependencies installed"

echo "\n🗄️  Checking database..."
if [ ! -f blockchain.db ]; then
    echo "Creating new blockchain database..."
    python3 -c "from database import Database; db = Database('blockchain.db'); print('Database created')"
fi

echo "✓ Database ready"

echo "\n🔐 Generating production secret key..."
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
echo "Generated: $SECRET_KEY"
echo "Add this to your .env file as JWT_SECRET_KEY"

echo "\n🧪 Running tests..."
if [ -d "tests" ]; then
    python3 -m pytest tests/ -v
fi

echo "\n🚀 Starting production server..."
echo "=========================================="

if command -v gunicorn &> /dev/null; then
    exec gunicorn -c gunicorn.conf.py --worker-class eventlet -w 1 api_production:app
else
    echo "⚠️  Gunicorn not found. Using Flask dev server (NOT for production!)"
    exec python3 api_production.py
fi
