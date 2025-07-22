#!/bin/bash

# Vital Planet Asset Hub - Asset Scanning Script
# Scans packaging assets and builds the index

set -e

echo "🔍 Vital Planet Asset Hub - Asset Scanner"
echo "========================================"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    print_status "Activating virtual environment..."
    source venv/bin/activate
fi

# Check if Python modules are available
python3 -c "import backend.scanner.asset_scanner" 2>/dev/null || {
    print_error "Backend modules not found. Please run setup.sh first."
    exit 1
}

# Create timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

print_status "Starting asset scan..."
print_status "Timestamp: $TIMESTAMP"

# Run the multi-directory scanner
python3 -c "
import sys
sys.path.append('.')
from backend.scanner.asset_scanner import AssetScanner

print('🔍 Starting multi-directory asset scan...')
scanner = AssetScanner(scan_mode='all')
asset_index = scanner.scan_multiple_directories()
scanner.save_index(asset_index)

print(f'✅ Multi-directory scan completed!')
print(f'📊 Results: {asset_index.metadata.total_products} products, {asset_index.metadata.total_assets:,} assets')
print(f'⏱️  Duration: {asset_index.metadata.scan_duration:.2f} seconds')
" 2>&1 | tee "logs/scan_$TIMESTAMP.log"

SCAN_RESULT=$?

if [ $SCAN_RESULT -eq 0 ]; then
    print_status "Asset scan completed successfully!"
    
    # Check if index was created
    if [ -f "assets_index.json" ]; then
        INDEX_SIZE=$(stat -f%z assets_index.json 2>/dev/null || stat -c%s assets_index.json 2>/dev/null || echo "unknown")
        print_status "Index file created: assets_index.json (${INDEX_SIZE} bytes)"
        
        # Create backup
        mkdir -p backups
        cp assets_index.json "backups/assets_index_$TIMESTAMP.json"
        print_status "Backup created: backups/assets_index_$TIMESTAMP.json"
        
        # Show summary
        python3 -c "
import json
try:
    with open('assets_index.json', 'r') as f:
        data = json.load(f)
    print(f'📊 Scan Summary:')
    print(f'   Products: {data[\"metadata\"][\"total_products\"]}')
    print(f'   Assets: {data[\"metadata\"][\"total_assets\"]:,}')
    print(f'   Source: {data[\"metadata\"][\"source_directory\"]}')
except Exception as e:
    print(f'Could not read summary: {e}')
"
    else
        print_error "Index file was not created!"
        exit 1
    fi
else
    print_error "Asset scan failed with exit code $SCAN_RESULT"
    print_error "Check logs/scan_$TIMESTAMP.log for details"
    exit 1
fi

print_status "Ready to start dashboard!"
echo "Next: ./scripts/start_server.sh"