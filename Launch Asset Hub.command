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

# Auto-kill any existing processes on port 8080
echo "🔍 Checking for existing servers on port 8080..."
if lsof -Pi :8080 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  Existing server found. Auto-killing for clean startup..."
    
    # Get PIDs and kill them
    EXISTING_PIDS=$(lsof -ti :8080 2>/dev/null || true)
    if [ ! -z "$EXISTING_PIDS" ]; then
        echo "🛑 Stopping processes: $EXISTING_PIDS"
        echo $EXISTING_PIDS | xargs kill 2>/dev/null || true
        sleep 2
        
        # Force kill if needed
        REMAINING_PIDS=$(lsof -ti :8080 2>/dev/null || true)
        if [ ! -z "$REMAINING_PIDS" ]; then
            echo "🔥 Force killing: $REMAINING_PIDS"
            echo $REMAINING_PIDS | xargs kill -9 2>/dev/null || true
            sleep 1
        fi
        
        echo "✅ Port 8080 cleared successfully"
    fi
else
    echo "✅ Port 8080 is available"
fi

echo ""
echo "🚀 Starting Asset Hub server..."
echo "🌐 Dashboard will open at: http://localhost:8080"
echo "🛑 Press Ctrl+C to stop the server"
echo ""

# Start the server
python3 backend/api/server.py
