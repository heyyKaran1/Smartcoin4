#!/bin/bash

echo "🚀 Starting Cryptocurrency Frontend & API Server..."
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

echo "Starting Flask server..."
echo ""
echo "=========================================="
echo "  Frontend: http://localhost:5000"
echo "  API:      http://localhost:5000/api"
echo "=========================================="
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python3 api.py
