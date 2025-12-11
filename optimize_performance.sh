#!/bin/bash
# Performance Optimization Script for PPE Detection System

echo "================================================"
echo "  Performance Optimization"
echo "================================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "Checking current performance..."
echo ""

# Run GPU check
python3 check_gpu.py

echo ""
echo "================================================"
echo "  OPTIMIZATION OPTIONS"
echo "================================================"
echo ""

echo "Choose optimization level:"
echo "  1) Enable GPU (if available)"
echo "  2) Optimize for low-end hardware (CPU mode)"
echo "  3) Optimize for RTSP cameras"
echo "  4) Optimize for multi-camera mode"
echo "  5) Reset to defaults"
echo ""
read -p "Enter choice (1-5): " choice

case $choice in
    1)
        echo -e "${GREEN}Enabling GPU mode...${NC}"
        # Update config for GPU
        sed -i 's/use_gpu: false/use_gpu: true/g' config.yaml
        sed -i 's/device: "cpu"/device: "cuda:0"/g' config.yaml
        echo "✅ GPU mode enabled in config.yaml"
        echo "Note: Make sure CUDA is installed!"
        ;;
    2)
        echo -e "${YELLOW}Optimizing for CPU mode...${NC}"
        # Lower resolution and FPS
        sed -i 's/width: 1280/width: 960/g' config.yaml
        sed -i 's/height: 720/height: 540/g' config.yaml
        sed -i 's/fps: 30/fps: 15/g' config.yaml
        sed -i 's/use_gpu: true/use_gpu: false/g' config.yaml
        sed -i 's/device: "cuda:0"/device: "cpu"/g' config.yaml
        echo "✅ CPU optimization applied:"
        echo "   - Resolution: 960x540"
        echo "   - FPS: 15"
        echo "   - Device: CPU"
        ;;
    3)
        echo -e "${YELLOW}Optimizing for RTSP cameras...${NC}"
        # RTSP-specific optimizations
        python3 << EOF
import yaml
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Lower RTSP FPS
if 'multi_camera' in config and 'camera_configs' in config['multi_camera']:
    if len(config['multi_camera']['camera_configs']) > 1:
        config['multi_camera']['camera_configs'][1]['fps'] = 10
        config['multi_camera']['camera_configs'][1]['width'] = 960
        config['multi_camera']['camera_configs'][1]['height'] = 540

with open('config.yaml', 'w') as f:
    yaml.dump(config, f, default_flow_style=False)

print("✅ RTSP optimizations applied:")
print("   - RTSP FPS: 10")
print("   - RTSP Resolution: 960x540")
EOF
        ;;
    4)
        echo -e "${YELLOW}Optimizing for multi-camera mode...${NC}"
        python3 << EOF
import yaml
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Multi-camera optimizations
config['multi_camera']['camera_configs'][0]['fps'] = 20
config['multi_camera']['camera_configs'][1]['fps'] = 10
config['detection']['frame_skip'] = 1

with open('config.yaml', 'w') as f:
    yaml.dump(config, f, default_flow_style=False)

print("✅ Multi-camera optimizations applied:")
print("   - USB FPS: 20")
print("   - RTSP FPS: 10")
print("   - Frame skip: 1")
EOF
        ;;
    5)
        echo -e "${YELLOW}Resetting to defaults...${NC}"
        git checkout config.yaml
        echo "✅ Config reset to defaults"
        ;;
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}Optimization complete!${NC}"
echo ""
echo "Test the changes:"
echo "  ./run_ubuntu.sh"
echo ""
