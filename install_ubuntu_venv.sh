#!/bin/bash
# Installation script with virtual environment support

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "================================================"
echo "  PPE Detection System - Ubuntu Installation"
echo "  (with Virtual Environment)"
echo "================================================"
echo ""

# Check Python version
echo -e "${YELLOW}Step 1: Checking Python...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 not found!${NC}"
    exit 1
fi

python3 --version
echo ""

# Install system packages
echo -e "${YELLOW}Step 2: Installing system packages...${NC}"
sudo apt-get update
sudo apt-get install -y \
    python3-venv \
    python3-dev \
    python3-pip \
    ffmpeg \
    libavcodec-extra \
    libxcb-xinerama0 \
    libxcb-cursor0 \
    libxkbcommon-x11-0

echo ""

# Create virtual environment
echo -e "${YELLOW}Step 3: Creating virtual environment...${NC}"
if [ -d "venv" ]; then
    echo "Virtual environment already exists"
else
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

echo ""

# Activate and install packages
echo -e "${YELLOW}Step 4: Installing Python packages...${NC}"
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install PyTorch (CPU version first for compatibility)
echo "Installing PyTorch..."
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Install other packages
echo "Installing other dependencies..."
pip install -r requirements.txt

echo ""

# Verify installation
echo -e "${YELLOW}Step 5: Verifying installation...${NC}"
python3 << EOF
import sys
try:
    import cv2
    print("✓ OpenCV:", cv2.__version__)
except ImportError:
    print("✗ OpenCV not found")
    sys.exit(1)

try:
    import PyQt6
    print("✓ PyQt6:", PyQt6.QtCore.qVersion())
except ImportError:
    print("✗ PyQt6 not found")
    sys.exit(1)

try:
    import torch
    print("✓ PyTorch:", torch.__version__)
except ImportError:
    print("✗ PyTorch not found")
    sys.exit(1)

print("\n✅ All dependencies installed successfully!")
EOF

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}================================================${NC}"
    echo -e "${GREEN}  Installation completed successfully!${NC}"
    echo -e "${GREEN}================================================${NC}"
    echo ""
    echo "Virtual environment created at: ./venv"
    echo ""
    echo "To activate the virtual environment:"
    echo -e "${GREEN}  source venv/bin/activate${NC}"
    echo ""
    echo "To run the application:"
    echo -e "${GREEN}  ./run_ubuntu.sh${NC}"
    echo ""
    echo "Or with venv activated:"
    echo "  python3 main.py"
    echo ""
else
    echo ""
    echo -e "${RED}Installation verification failed.${NC}"
    exit 1
fi
