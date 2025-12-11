"""
Device selector utility for automatic GPU/CPU selection.
"""

import torch
import logging

logger = logging.getLogger(__name__)


def get_best_device(preferred_device: str = "auto") -> str:
    """
    Automatically select the best available device.

    Args:
        preferred_device: Preferred device string
            - "auto": Auto-detect best device
            - "cuda" or "cuda:0": Use GPU if available, else CPU
            - "cpu": Force CPU
            - "cuda:N": Specific GPU

    Returns:
        Device string (e.g., "cuda:0", "cpu")
    """
    # Force CPU if requested
    if preferred_device == "cpu":
        logger.info("Device: CPU (forced by config)")
        return "cpu"

    # Check if CUDA is available
    if not torch.cuda.is_available():
        logger.warning("CUDA not available. Falling back to CPU.")
        logger.warning("Install GPU support: pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121")
        return "cpu"

    # CUDA is available
    gpu_count = torch.cuda.device_count()

    # Auto-select or validate specific GPU
    if preferred_device == "auto" or preferred_device == "cuda":
        # Use first GPU
        device = "cuda:0"
        gpu_name = torch.cuda.get_device_name(0)
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3

        logger.info(f"✅ Auto-selected GPU: {gpu_name}")
        logger.info(f"   CUDA Version: {torch.version.cuda}")
        logger.info(f"   GPU Memory: {gpu_memory:.1f} GB")
        logger.info(f"   Device: {device}")

        return device

    elif preferred_device.startswith("cuda:"):
        # Validate specific GPU index
        gpu_idx = int(preferred_device.split(":")[1])

        if gpu_idx >= gpu_count:
            logger.warning(f"GPU {gpu_idx} not found. Available GPUs: {gpu_count}")
            logger.warning("Falling back to cuda:0")
            return "cuda:0"

        gpu_name = torch.cuda.get_device_name(gpu_idx)
        logger.info(f"✅ Using GPU {gpu_idx}: {gpu_name}")
        return preferred_device

    else:
        # Unknown device string, default to auto
        logger.warning(f"Unknown device '{preferred_device}', auto-selecting...")
        return get_best_device("auto")


def print_device_info():
    """Print detailed device information."""
    print("=" * 60)
    print("Device Information:")
    print("=" * 60)

    if torch.cuda.is_available():
        print(f"✅ CUDA Available: Yes")
        print(f"   CUDA Version: {torch.version.cuda}")
        print(f"   GPU Count: {torch.cuda.device_count()}")
        print()

        for i in range(torch.cuda.device_count()):
            name = torch.cuda.get_device_name(i)
            props = torch.cuda.get_device_properties(i)
            memory = props.total_memory / 1024**3
            capability = f"{props.major}.{props.minor}"

            print(f"GPU {i}: {name}")
            print(f"  Memory: {memory:.1f} GB")
            print(f"  Compute Capability: {capability}")
            print()

        # Show recommended device
        best = get_best_device("auto")
        print(f"Recommended Device: {best}")
    else:
        print("❌ CUDA Available: No")
        print("   Using CPU (slow performance)")
        print()
        print("To enable GPU:")
        print("  pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121")

    print("=" * 60)


if __name__ == "__main__":
    print_device_info()
