#!/usr/bin/env python3
"""
GPU and Performance Diagnostic Tool
ตรวจสอบว่าระบบใช้ GPU หรือไม่ และหาสาเหตุที่ FPS ต่ำ
"""

import sys
import os

print("=" * 60)
print("  PPE Detection System - GPU Diagnostic Tool")
print("=" * 60)
print()

# Check PyTorch and CUDA
print("1. PyTorch & CUDA Status:")
try:
    import torch
    print(f"   PyTorch Version: {torch.__version__}")
    print(f"   CUDA Available: {torch.cuda.is_available()}")
    
    if torch.cuda.is_available():
        print(f"   ✅ CUDA Version: {torch.version.cuda}")
        print(f"   ✅ GPU Count: {torch.cuda.device_count()}")
        for i in range(torch.cuda.device_count()):
            name = torch.cuda.get_device_name(i)
            mem = torch.cuda.get_device_properties(i).total_memory / 1024**3
            print(f"   ✅ GPU {i}: {name} ({mem:.1f} GB)")
    else:
        print("   ❌ CUDA NOT AVAILABLE - Using CPU (VERY SLOW!)")
        print()
        print("   Install GPU support:")
        print("   pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu118")
except ImportError:
    print("   ❌ PyTorch not installed")
print()

# Check config
print("2. Configuration:")
try:
    import yaml
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    use_gpu = config['detection']['use_gpu']
    pose_dev = config['models']['yolov8_pose']['device']
    ppe_dev = config['models']['ppe_detection']['device']
    
    print(f"   use_gpu: {use_gpu}")
    print(f"   Pose device: {pose_dev}")
    print(f"   PPE device: {ppe_dev}")
    
    if 'cuda' in pose_dev:
        print(f"   ✅ Configured to use GPU")
    else:
        print(f"   ❌ Configured to use CPU")
except Exception as e:
    print(f"   Error: {e}")
print()

# Recommendations
print("=" * 60)
print("DIAGNOSIS:")
try:
    import torch
    if not torch.cuda.is_available():
        print("❌ GPU NOT AVAILABLE - This is why FPS is low!")
        print()
        print("Install NVIDIA driver & CUDA PyTorch:")
        print("  sudo ubuntu-drivers autoinstall")
        print("  sudo reboot")
        print("  pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu118")
    else:
        print("✅ GPU is available")
        print()
        print("If FPS still low, try:")
        print("  1. Lower resolution: 960x540")
        print("  2. Lower RTSP FPS to 10-15")
        print("  3. Disable multi-camera mode for testing")
except:
    print("Install PyTorch with GPU support")
print("=" * 60)
