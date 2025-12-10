"""
Check GPU availability and recommend settings.
"""

import torch
import sys


def check_gpu_support():
    """Check GPU support and print recommendations."""
    print("\n" + "=" * 70)
    print("🖥️  GPU/CPU Check")
    print("=" * 70)

    # Check PyTorch
    print(f"\n✅ PyTorch Version: {torch.__version__}")

    # Check CUDA availability
    cuda_available = torch.cuda.is_available()

    if cuda_available:
        print("✅ CUDA is available!")
        print(f"   GPU Count: {torch.cuda.device_count()}")

        for i in range(torch.cuda.device_count()):
            gpu_name = torch.cuda.get_device_name(i)
            print(f"   GPU {i}: {gpu_name}")

        # Check CUDA version
        print(f"   CUDA Version: {torch.version.cuda}")

        # Recommended settings
        print("\n📋 Recommended Settings:")
        print("   config.yaml:")
        print("     detection:")
        print("       use_gpu: true")
        print("     models:")
        print("       yolov8_pose:")
        print("         path: yolov8m-pose.pt  # Medium - good balance")
        print("         device: cuda:0")

        print("\n   .env:")
        print("     USE_GPU=True")

        # Performance estimate
        print("\n⚡ Expected Performance:")
        print("   Resolution: 1280x720")
        print("   Estimated FPS: 30-60 (depends on GPU)")

    else:
        print("⚠️  CUDA is NOT available")
        print("   Running on CPU only")

        # Check why
        if not torch.backends.cudnn.enabled:
            print("\n   Possible reasons:")
            print("   1. No NVIDIA GPU")
            print("   2. CUDA toolkit not installed")
            print("   3. PyTorch installed without CUDA support")

        # Recommended settings for CPU
        print("\n📋 Recommended Settings for CPU:")
        print("   config.yaml:")
        print("     detection:")
        print("       use_gpu: false")
        print("     models:")
        print("       yolov8_pose:")
        print("         path: yolov8n-pose.pt  # Nano - fastest for CPU")
        print("         device: cpu")

        print("\n   .env:")
        print("     USE_GPU=False")

        # Performance estimate
        print("\n⚡ Expected Performance (CPU):")
        print("   Resolution: 640x480 (lower for better FPS)")
        print("   Estimated FPS: 5-10")

        print("\n💡 Tips for CPU:")
        print("   1. Use smaller model (yolov8n-pose)")
        print("   2. Lower resolution in config.yaml")
        print("   3. Enable frame_skip for real-time")

    print("\n" + "=" * 70)

    # Test tensor creation
    print("\n🧪 Testing GPU/CPU tensor creation...")
    try:
        if cuda_available:
            device = torch.device("cuda:0")
            x = torch.randn(1000, 1000, device=device)
            print(f"✅ Successfully created tensor on GPU")
            print(f"   Tensor device: {x.device}")
        else:
            device = torch.device("cpu")
            x = torch.randn(1000, 1000, device=device)
            print(f"✅ Successfully created tensor on CPU")
            print(f"   Tensor device: {x.device}")
    except Exception as e:
        print(f"❌ Error creating tensor: {e}")

    print("\n" + "=" * 70)

    return cuda_available


if __name__ == "__main__":
    has_gpu = check_gpu_support()

    print("\n🎯 Next Steps:")
    if has_gpu:
        print("   1. GPU detected - You're ready to go!")
        print("   2. Run: python main.py")
        print("   3. System will use GPU automatically")
    else:
        print("   1. No GPU - Will use CPU")
        print("   2. Update config.yaml with CPU settings (above)")
        print("   3. Use yolov8n-pose for better CPU performance")
        print("   4. Run: python main.py")

    print()
    sys.exit(0 if has_gpu else 1)
