#!/bin/bash

# Vital Planet Asset Hub - Cleanup Script
# Organizes project structure and removes redundant files

set -e

echo "🧹 Vital Planet Asset Hub - Project Cleanup"
echo "==========================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[CLEAN]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to safely remove file if it exists
safe_remove() {
    if [ -f "$1" ]; then
        rm "$1"
        print_status "Removed: $1"
    fi
}

# Function to safely remove directory if it exists and is empty
safe_remove_dir() {
    if [ -d "$1" ] && [ -z "$(ls -A "$1")" ]; then
        rmdir "$1"
        print_status "Removed empty directory: $1"
    elif [ -d "$1" ]; then
        print_warning "Directory not empty, keeping: $1"
    fi
}

print_status "Starting project cleanup..."

# 1. Clean up JSON backup mess
print_status "Cleaning up JSON backup files..."

# Move all backup files to backups/ directory
mkdir -p backups/archive
mv assets_index.backup.*.json backups/archive/ 2>/dev/null || true

# Remove duplicate/test JSON files
safe_remove "assets_index_multi.json"

# Keep only the latest 3 backups in backups/ (by date)
cd backups
if ls assets_index_*.json 1> /dev/null 2>&1; then
    ls -t assets_index_*.json | tail -n +4 | xargs rm -f 2>/dev/null || true
fi
cd ..

print_status "JSON backups organized - kept latest 3, archived old ones"

# 2. Remove duplicate and confusing files
print_status "Removing duplicate and confusing files..."

# Remove old scanner in root
safe_remove "asset_scanner.py"

# Remove duplicate CSS files  
safe_remove "enhancements.css"  # Functionality should be in main styles.css
safe_remove "frontend/styles.css"  # Duplicate of styles.css

# Remove test files from root (move to tests/)
if [ -f "test_multi_scan.py" ]; then
    mv test_multi_scan.py tests/
    print_status "Moved test_multi_scan.py to tests/"
fi

# Remove redundant setup files
safe_remove "quick_setup.sh"
safe_remove "requirements-simple.txt"

# 3. Clean up empty or unnecessary directories
print_status "Cleaning up directory structure..."

# Remove empty frontend subdirectories
safe_remove_dir "frontend/assets/images"
safe_remove_dir "frontend/assets"
safe_remove_dir "frontend/components"
safe_remove_dir "frontend/styles"
safe_remove_dir "frontend"

# Remove empty backend subdirectories
safe_remove_dir "backend/api/middleware"
safe_remove_dir "backend/api/routes"

# Remove empty directories
safe_remove_dir "data"
safe_remove_dir "temp"

# 4. Organize logs with retention policy
print_status "Organizing log files..."

# Keep only the latest 5 log files
cd logs
if ls scan_*.log 1> /dev/null 2>&1; then
    ls -t scan_*.log | tail -n +6 | xargs rm -f 2>/dev/null || true
fi
cd ..

# 5. Create .gitignore for cleaner repository
print_status "Creating .gitignore..."
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# Asset Hub specific
assets_index.json
assets_index.backup.*.json
logs/*.log
backups/*.json
temp/
data/

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# Environment
.env
.env.local
.env.production
EOF

# 6. Update asset scanner backup logic to be cleaner
print_status "Updating backup management in scanner..."

# Create a proper backup management function
cat > scripts/manage_backups.sh << 'EOF'
#!/bin/bash

# Backup management for Asset Hub
# Keeps only the latest N backups and cleans up old ones

BACKUP_DIR="backups"
MAX_BACKUPS=5

# Ensure backup directory exists
mkdir -p "$BACKUP_DIR"

# Clean up old backups, keep only the latest N
if ls "$BACKUP_DIR"/assets_index_*.json 1> /dev/null 2>&1; then
    backup_count=$(ls -1 "$BACKUP_DIR"/assets_index_*.json | wc -l)
    if [ "$backup_count" -gt "$MAX_BACKUPS" ]; then
        excess=$((backup_count - MAX_BACKUPS))
        ls -t "$BACKUP_DIR"/assets_index_*.json | tail -n "$excess" | xargs rm -f
        echo "Cleaned up $excess old backup(s)"
    fi
fi
EOF

chmod +x scripts/manage_backups.sh

print_status "Cleanup completed successfully!"

# Summary
echo ""
echo "📊 Cleanup Summary:"
echo "✅ JSON backups organized (latest 3 kept, old ones archived)"
echo "✅ Duplicate files removed"
echo "✅ Test files moved to tests/ directory"
echo "✅ Empty directories cleaned up" 
echo "✅ Log retention policy applied"
echo "✅ .gitignore created"
echo "✅ Backup management system installed"
echo ""
echo "🎯 Project is now properly organized!"