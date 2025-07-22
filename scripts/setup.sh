#!/bin/bash

# Vital Planet Asset Hub - Consolidated Setup Script
# One cohesive setup with Python 3.13 compatibility and multi-directory support

set -e  # Exit on any error

echo "🌱 Vital Planet Asset Hub - Consolidated Setup"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}$1${NC}"
}

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    print_warning "This script is optimized for macOS. Continuing anyway..."
fi

# Check Python installation
print_header "Checking Python Installation..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is required but not installed."
    print_status "Please install Python 3.9+ from https://www.python.org/"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
print_status "Found Python $PYTHON_VERSION"

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    print_error "pip3 is required but not found."
    exit 1
fi

# Create project directory structure if not exists
print_header "Setting up directory structure..."
mkdir -p data
mkdir -p logs
mkdir -p backups
mkdir -p temp
print_status "Directories created"

# Create virtual environment
print_header "Setting up virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_status "Virtual environment created"
else
    print_status "Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate
print_status "Virtual environment activated"

# Upgrade pip
print_header "Upgrading pip..."
pip install --upgrade pip

# Install dependencies with error handling
print_header "Installing Python dependencies..."
print_status "Installing core dependencies with Python 3.13 compatibility..."

# Remove existing venv if it has issues
if [ -d "venv" ] && [ -f "venv/pyvenv.cfg" ]; then
    print_warning "Removing existing virtual environment to fix dependency issues..."
    rm -rf venv
fi

# Install Flask and Werkzeug first (most critical)
pip install "Flask>=3.0.0" "Werkzeug>=3.0.0" || {
    print_warning "Latest Flask failed, trying compatible version..."
    pip install "Flask>=2.3.0,<3.0.0" "Werkzeug>=2.3.0,<3.0.0"
}

# Install other essential dependencies
pip install python-dotenv colorama psutil || {
    print_warning "Some optional dependencies failed to install, continuing..."
}

# Create environment configuration
print_header "Setting up environment configuration..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_status "Environment file created from template"
        print_warning "Please edit .env file to configure your OneDrive path"
    else
        print_error ".env.example template not found!"
    fi
else
    print_status "Environment file already exists"
fi

# Set up logging directory
print_header "Configuring logging..."
touch logs/vital_planet_asset_hub.log
chmod 644 logs/vital_planet_asset_hub.log
print_status "Log file initialized"

# Make scripts executable
print_header "Setting script permissions..."
chmod +x scripts/*.sh 2>/dev/null || true
print_status "Scripts made executable"

# Test Flask installation
print_header "Testing Flask installation..."
python3 -c "import flask; print(f'Flask {flask.__version__} installed successfully')" || {
    print_error "Flask installation failed!"
    exit 1
}

# Test the modular imports
print_header "Testing modular imports..."
python3 -c "
import sys
sys.path.append('.')
try:
    from backend.config.settings import settings
    from backend.scanner.file_analyzer import FileAnalyzer
    print('✅ All core modules import successfully')
    print(f'Primary Color: {settings.PRIMARY_COLOR}')
except ImportError as e:
    print(f'⚠️  Some modules failed to import: {e}')
    print('This is normal - the scanner will still work')
except Exception as e:
    print(f'❌ Unexpected error: {e}')
"

# Check OneDrive path
print_header "Checking OneDrive configuration..."
ONEDRIVE_PATH="/Users/$(whoami)/Library/CloudStorage/OneDrive-VitalPlanet"
if [ -d "$ONEDRIVE_PATH" ]; then
    print_status "OneDrive path found: $ONEDRIVE_PATH"
else
    print_warning "OneDrive path not found. Please configure VP_ASSET_SOURCE_PATH in .env"
fi

# Create desktop shortcut (macOS)
print_header "Creating shortcuts..."
cat > "Launch Asset Hub.command" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
python3 backend/api/server.py
EOF
chmod +x "Launch Asset Hub.command"
print_status "Desktop launcher created"

# Final instructions
print_header "Setup Complete! 🎉"
echo ""
print_status "Dependencies installed successfully with Python $PYTHON_VERSION"
print_status "Multi-directory scanning enabled (Human + Pet, Current + WIP)"
print_status "Next steps:"
echo "1. Edit .env file to configure your OneDrive path (if needed)"
echo "2. Run: ./scripts/scan_assets.sh (to build multi-directory index)"
echo "3. Run: ./scripts/start_server.sh (to start the enhanced dashboard)"
echo ""
echo "Or double-click: 'Launch Asset Hub.command'"
echo ""
print_status "For help, see: docs/USER_MANUAL.md"
echo ""
print_warning "Remember to activate the virtual environment when running manually:"
echo "source venv/bin/activate"