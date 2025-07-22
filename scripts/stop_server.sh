#!/bin/bash

# Vital Planet Asset Hub - Stop Server Script
# Stops the running dashboard server

echo "🛑 Stopping Vital Planet Asset Hub..."

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check for PID file
if [ -f "temp/server.pid" ]; then
    SERVER_PID=$(cat temp/server.pid)
    
    if kill -0 $SERVER_PID 2>/dev/null; then
        print_status "Stopping server (PID: $SERVER_PID)..."
        kill $SERVER_PID
        
        # Wait for graceful shutdown
        sleep 2
        
        # Force kill if still running
        if kill -0 $SERVER_PID 2>/dev/null; then
            print_status "Force stopping server..."
            kill -9 $SERVER_PID 2>/dev/null || true
        fi
        
        print_status "Server stopped"
    else
        print_status "Server was not running (PID file exists but process not found)"
    fi
    
    rm -f temp/server.pid
else
    print_status "No PID file found, checking for running processes..."
    
    # Try to find and kill any Python servers on our ports
    DEFAULT_PORT=8080
    PIDS=$(lsof -ti :$DEFAULT_PORT 2>/dev/null || true)
    
    if [ ! -z "$PIDS" ]; then
        print_status "Found processes on port $DEFAULT_PORT, stopping..."
        echo $PIDS | xargs kill 2>/dev/null || true
        sleep 1
        echo $PIDS | xargs kill -9 2>/dev/null || true
        print_status "Processes stopped"
    else
        print_status "No server processes found"
    fi
fi

print_status "Dashboard stopped successfully"