#!/bin/bash
# Installation script for PPE Detection System on Ubuntu/Debian

set -e  # Exit on error

echo "================================================"
echo "  PPE Detection System - Ubuntu Installation"
echo "================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo -e "${RED}Please do not run as root. Run as normal user.${NC}"
    exit 1
fi

echo -e "${YELLOW}Step 1: Updating system packages...${NC}"
sudo apt-get update

echo ""
echo -e "${YELLOW}Step 2: Installing system dependencies...${NC}"
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    build-essential \
    cmake \
    pkg-config \
    libopencv-dev \
    python3-opencv \
    libxcb-xinerama0 \
    libxcb-cursor0 \
    libxkbcommon-x11-0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-shape0 \
    libxcb-sync1 \
    libxcb-xfixes0 \
    libxcb-xkb1 \
    libxcb1 \
    libx11-xcb1 \
    libdbus-1-3 \
    ffmpeg \
    libavcodec-extra \
    libavformat-dev \
    libavutil-dev \
    libswscale-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libgtk-3-dev

echo ""
echo -e "${YELLOW}Step 3: Checking Python version...${NC}"
python3 --version

echo ""
echo -e "${YELLOW}Step 4: Upgrading pip...${NC}"
python3 -m pip install --upgrade pip

echo ""
echo -e "${YELLOW}Step 5: Installing Python packages...${NC}"

# Install PyTorch first (CPU version for compatibility)
echo "Installing PyTorch..."
python3 -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Install other requirements
echo "Installing other dependencies..."
python3 -m pip install -r requirements.txt

echo ""
echo -e "${YELLOW}Step 6: Verifying installation...${NC}"

# Check critical imports
python3 << EOF
import sys
try:
    import cv2
    print("✓ OpenCV:", cv2.__version__)
except ImportError as e:
    print("✗ OpenCV not found")
    sys.exit(1)

try:
    import PyQt6
    print("✓ PyQt6:", PyQt6.QtCore.qVersion())
except ImportError as e:
    print("✗ PyQt6 not found")
    sys.exit(1)

try:
    import torch
    print("✓ PyTorch:", torch.__version__)
except ImportError as e:
    print("✗ PyTorch not found")
    sys.exit(1)

try:
    from ultralytics import YOLO
    print("✓ Ultralytics YOLO installed")
except ImportError as e:
    print("✗ Ultralytics not found")
    sys.exit(1)

print("\nAll core dependencies installed successfully!")
EOF

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}================================================${NC}"
    echo -e "${GREEN}  Installation completed successfully!${NC}"
    echo -e "${GREEN}================================================${NC}"
    echo ""
    echo "To run the application:"
    echo "  ./run_ubuntu.sh"
    echo ""
    echo "Or directly:"
    echo "  python3 main.py"
    echo ""
else
    echo ""
    echo -e "${RED}Installation verification failed.${NC}"
    echo "Please check the error messages above."
    exit 1
fi
