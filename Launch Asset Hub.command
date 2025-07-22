#!/bin/bash

# Vital Planet Asset Hub - Desktop Launcher
cd "$(dirname "$0")"

echo "🌱 Launching Vital Planet Asset Hub..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup first:"
    echo "   ./scripts/setup.sh"
    read -p "Press any key to exit..."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if asset index exists
if [ ! -f "assets_index.json" ]; then
    echo "📊 No asset index found. Running initial scan..."
    ./scripts/scan_assets.sh
fi

echo "🚀 Starting Asset Hub server..."
echo "🌐 Dashboard will open at: http://localhost:8080"
echo "🛑 Press Ctrl+C to stop the server"
echo ""

# Start the server
python3 backend/api/server.py
