#!/bin/bash

# Test script for auto-kill functionality
# This will start a dummy server, then test if our scripts can kill it

echo "🧪 Testing auto-kill functionality..."

# Start a dummy Python HTTP server on port 8080
echo "🚀 Starting dummy server on port 8080..."
python3 -m http.server 8080 --bind localhost > /dev/null 2>&1 &
DUMMY_PID=$!

echo "📝 Dummy server PID: $DUMMY_PID"

# Wait a moment
sleep 2

# Check if it's running
if lsof -Pi :8080 -sTCP:LISTEN -t >/dev/null ; then
    echo "✅ Dummy server is running on port 8080"
    
    # Now test our auto-kill functionality
    echo "🔥 Testing auto-kill via start_server.sh..."
    
    # This should kill the dummy server and try to start our server
    timeout 10s ./scripts/start_server.sh &
    TEST_PID=$!
    
    # Wait a moment
    sleep 3
    
    # Kill the test
    kill $TEST_PID 2>/dev/null || true
    
    echo "✅ Auto-kill test completed"
else
    echo "❌ Dummy server failed to start"
fi

# Clean up any remaining processes
echo "🧹 Cleaning up..."
lsof -ti :8080 2>/dev/null | xargs kill -9 2>/dev/null || true

echo "✅ Test completed"