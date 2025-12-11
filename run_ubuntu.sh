#!/bin/bash
# Launcher script for PPE Detection System on Ubuntu
# Fixes Qt/Wayland display issues

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Check if Python dependencies are installed
echo "Checking dependencies..."
python3 -c "import PyQt6" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: PyQt6 is not installed!${NC}"
    echo ""
    echo "Please run the installation script first:"
    echo -e "${GREEN}  ./install_ubuntu_venv.sh${NC}"
    echo ""
    echo "For Ubuntu 23.04+/Debian 12+, use venv version (recommended)"
    echo "For older Ubuntu, you can try: ./install_ubuntu.sh"
    echo ""
    exit 1
fi

# Check OpenCV
python3 -c "import cv2" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: OpenCV is not installed!${NC}"
    echo ""
    echo "Please run the installation script:"
    echo -e "${GREEN}  ./install_ubuntu_venv.sh${NC}"
    echo ""
    exit 1
fi

echo -e "${GREEN}✓ Dependencies OK${NC}"
echo ""

# Force Qt to use X11 instead of Wayland
export QT_QPA_PLATFORM=xcb

# Suppress FFmpeg H.264 decoding warnings
export OPENCV_FFMPEG_LOGLEVEL=quiet

# Run the application
python3 main.py "$@"
