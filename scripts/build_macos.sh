#!/bin/bash

echo "========================================"
echo "iDevice Manager - macOS Build Script"
echo "========================================"
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_error() {
    echo -e "${RED}ERROR: $1${NC}"
}

print_success() {
    echo -e "${GREEN}SUCCESS: $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}WARNING: $1${NC}"
}

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed"
    echo "Please install Python 3.8+ from https://python.org or use Homebrew:"
    echo "brew install python"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "Found Python version: $PYTHON_VERSION"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    print_error "pip3 is not installed"
    echo "Please install pip3"
    exit 1
fi

# Check for Xcode Command Line Tools (required for some dependencies)
if ! xcode-select -p &> /dev/null; then
    print_warning "Xcode Command Line Tools not found"
    echo "Installing Xcode Command Line Tools..."
    xcode-select --install
    echo "Please complete the installation and run this script again"
    exit 1
fi

echo "Setting up virtual environment..."
if [ -d "build_env" ]; then
    echo "Removing existing build environment..."
    rm -rf build_env
fi

python3 -m venv build_env
if [ $? -ne 0 ]; then
    print_error "Failed to create virtual environment"
    exit 1
fi

echo "Activating virtual environment..."
source build_env/bin/activate

echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    print_error "Failed to install dependencies"
    exit 1
fi

echo "Installing PyInstaller..."
pip install pyinstaller
if [ $? -ne 0 ]; then
    print_error "Failed to install PyInstaller"
    exit 1
fi

echo "Building macOS application bundle..."
mkdir -p dist

pyinstaller --onefile \
    --windowed \
    --name "iDevice Manager" \
    --distpath dist \
    --workpath build \
    --specpath build \
    --osx-bundle-identifier "com.idevicemanager.app" \
    idevice_manager/main.py

if [ $? -ne 0 ]; then
    print_error "Build failed"
    exit 1
fi

echo
echo "========================================"
print_success "Build completed successfully!"
echo "========================================"
echo "Application bundle location: dist/iDevice Manager.app"
echo
echo "To test the build:"
echo "1. Copy 'dist/iDevice Manager.app' to Applications folder"
echo "2. Run the application from Applications or Finder"
echo
echo "To create a DMG installer:"
echo "1. Install create-dmg: brew install create-dmg"
echo "2. Run: create-dmg --volname 'iDevice Manager' --window-pos 200 120 --window-size 600 300 --icon-size 100 --icon 'iDevice Manager.app' 175 120 --hide-extension 'iDevice Manager.app' --app-drop-link 425 120 'iDevice Manager.dmg' dist/"
echo

echo "Deactivating virtual environment..."
deactivate

print_success "Build process completed!"