#!/bin/bash

# Vital Planet Asset Hub - Server Startup Script
# Starts the web dashboard server

set -e

echo "🚀 Vital Planet Asset Hub - Starting Server"
echo "==========================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_url() {
    echo -e "${BLUE}[URL]${NC} $1"
}

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    print_status "Activating virtual environment..."
    source venv/bin/activate
fi

# Check if asset index exists
if [ ! -f "assets_index.json" ]; then
    print_warning "Asset index not found!"
    print_status "Running asset scan first..."
    ./scripts/scan_assets.sh
fi

# Load environment variables
if [ -f ".env" ]; then
    source .env
    print_status "Environment loaded from .env"
else
    print_warning ".env file not found, using defaults"
fi

# Set default values
PORT=${VP_PORT:-8080}
HOST=${VP_HOST:-localhost}

# Check if port is available
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null ; then
    print_error "Port $PORT is already in use!"
    print_status "Please stop the existing service or change VP_PORT in .env"
    exit 1
fi

# Create PID file directory
mkdir -p temp

print_status "Starting Vital Planet Asset Hub..."
print_status "Host: $HOST"
print_status "Port: $PORT"

# Check if we have the Flask server
if [ ! -f "backend/api/server.py" ]; then
    print_error "Server file not found: backend/api/server.py"
    print_status "Starting simple HTTP server instead..."
    
    # Fallback to simple HTTP server for static files
    python3 -m http.server $PORT --bind $HOST 2>&1 &
    SERVER_PID=$!
    echo $SERVER_PID > temp/server.pid
else
    # Start Flask server
    python3 backend/api/server.py 2>&1 &
    SERVER_PID=$!
    echo $SERVER_PID > temp/server.pid
fi

# Wait a moment for server to start
sleep 2

# Check if server is running
if kill -0 $SERVER_PID 2>/dev/null; then
    print_status "Server started successfully! (PID: $SERVER_PID)"
    print_url "Dashboard URL: http://$HOST:$PORT"
    echo ""
    print_status "Opening dashboard in browser..."
    
    # Try to open in browser (macOS)
    if command -v open &> /dev/null; then
        open "http://$HOST:$PORT" 2>/dev/null || true
    fi
    
    echo ""
    print_status "Server is running in the background"
    print_status "Press Ctrl+C to stop, or run: ./scripts/stop_server.sh"
    echo ""
    
    # Keep script running to handle Ctrl+C
    trap 'print_status "Stopping server..."; kill $SERVER_PID 2>/dev/null; rm -f temp/server.pid; exit 0' INT
    
    # Wait for server process
    wait $SERVER_PID
else
    print_error "Failed to start server!"
    rm -f temp/server.pid
    exit 1
fi