#!/bin/bash

# Vital Planet Asset Hub - Maintenance Script
# Keeps the system clean and organized

set -e

echo "🔧 Vital Planet Asset Hub - System Maintenance"
echo "=============================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[MAINT]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Function to get file count in directory
count_files() {
    if [ -d "$1" ]; then
        ls -1 "$1" 2>/dev/null | wc -l | tr -d ' '
    else
        echo "0"
    fi
}

print_status "Running system maintenance..."

# 1. Clean up log files (keep latest 10)
print_status "Managing log files..."
cd logs
if ls *.log 1> /dev/null 2>&1; then
    log_count=$(ls -1 *.log | wc -l | tr -d ' ')
    if [ "$log_count" -gt 10 ]; then
        excess=$((log_count - 10))
        ls -t *.log | tail -n "$excess" | xargs rm -f
        print_status "Removed $excess old log files"
    else
        print_info "Log files within limit ($log_count/10)"
    fi
else
    print_info "No log files to clean"
fi
cd ..

# 2. Clean up backup files (keep latest 5 in main, unlimited in archive)
print_status "Managing backup files..."
cd backups
if ls assets_index_*.json 1> /dev/null 2>&1; then
    backup_count=$(ls -1 assets_index_*.json | wc -l | tr -d ' ')
    if [ "$backup_count" -gt 5 ]; then
        excess=$((backup_count - 5))
        # Move excess backups to archive instead of deleting
        mkdir -p archive
        ls -t assets_index_*.json | tail -n "$excess" | while read file; do
            mv "$file" archive/
        done
        print_status "Archived $excess old backup files"
    else
        print_info "Backup files within limit ($backup_count/5)"
    fi
else
    print_info "No backup files to manage"
fi
cd ..

# 3. Check for any stray files in root directory
print_status "Checking for stray files..."
stray_files=0

# Look for common stray file patterns
for pattern in "*.backup.*.json" "test_*.json" "*_temp.json" "*.tmp"; do
    if ls $pattern 1> /dev/null 2>&1; then
        ls $pattern | while read file; do
            print_warning "Found stray file: $file"
            rm -f "$file"
            stray_files=$((stray_files + 1))
        done
    fi
done

if [ $stray_files -eq 0 ]; then
    print_info "No stray files found"
fi

# 4. Validate project structure
print_status "Validating project structure..."

required_dirs=("backend" "backend/scanner" "backend/api" "backend/config" "scripts" "logs" "backups" "docs" "tests")
missing_dirs=0

for dir in "${required_dirs[@]}"; do
    if [ ! -d "$dir" ]; then
        print_warning "Missing directory: $dir"
        mkdir -p "$dir"
        missing_dirs=$((missing_dirs + 1))
    fi
done

if [ $missing_dirs -eq 0 ]; then
    print_info "Project structure is valid"
else
    print_status "Created $missing_dirs missing directories"
fi

# 5. Check disk usage
print_status "Checking disk usage..."
backup_size=$(du -sh backups 2>/dev/null | cut -f1)
log_size=$(du -sh logs 2>/dev/null | cut -f1)
total_size=$(du -sh . 2>/dev/null | cut -f1)

echo "   📁 Total project size: $total_size"
echo "   💾 Backups size: $backup_size"  
echo "   📝 Logs size: $log_size"

# 6. Summary report
echo ""
print_status "Maintenance Summary:"
echo "   ✅ Log files: $(count_files logs) (max 10)"
echo "   ✅ Active backups: $(count_files backups) (max 5)"  
echo "   ✅ Archived backups: $(count_files backups/archive)"
echo "   ✅ Project structure validated"

print_status "System maintenance completed!"

# Optional: Auto-run this weekly via cron
# Add to crontab: 0 2 * * 0 /path/to/this/script >/dev/null 2>&1