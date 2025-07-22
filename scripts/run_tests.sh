#!/bin/bash

# Vital Planet Asset Hub - Test Runner
# Runs all tests and validates system functionality

set -e

echo "🧪 Vital Planet Asset Hub - Test Suite"
echo "======================================"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[TEST]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Ensure virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    print_status "Activating virtual environment..."
    source venv/bin/activate
fi

# Check if Python modules are available
python3 -c "import backend.scanner.asset_scanner" 2>/dev/null || {
    print_error "Backend modules not found. Please run setup.sh first."
    exit 1
}

print_status "Running multi-directory scanner tests..."

# Run the test
python3 tests/test_multi_scan.py

if [ $? -eq 0 ]; then
    print_status "✅ All tests passed!"
else
    print_error "❌ Tests failed!"
    exit 1
fi

print_status "Test suite completed successfully!"