"""
Check where YOLOv8 models are stored and download them if needed.
"""

import os
from pathlib import Path


def check_yolov8_models():
    """Check YOLOv8 model locations and status."""
    print("\n" + "=" * 70)
    print("📦 YOLOv8 Model Storage Information")
    print("=" * 70)

    # Check different possible locations
    print("\n🔍 Checking model locations...\n")

    # 1. Project models directory
    project_models = Path("models")
    print(f"1️⃣  Project models directory: {project_models.absolute()}")
    if project_models.exists():
        models_in_project = list(project_models.glob("*.pt"))
        if models_in_project:
            print(f"   Found {len(models_in_project)} model(s):")
            for model in models_in_project:
                size = model.stat().st_size / (1024 * 1024)  # MB
                print(f"   - {model.name} ({size:.1f} MB)")
        else:
            print("   ⚠️  No .pt files found")
    else:
        print("   ❌ Directory does not exist")

    # 2. Ultralytics cache directory
    print("\n2️⃣  Ultralytics cache directory:")

    # Different locations for different OS
    if os.name == 'nt':  # Windows
        cache_dirs = [
            Path.home() / '.cache' / 'ultralytics',
            Path.home() / 'AppData' / 'Local' / 'Ultralytics',
            Path(os.getenv('LOCALAPPDATA', '')) / 'Ultralytics' if os.getenv('LOCALAPPDATA') else None,
        ]
    else:  # Linux/Mac
        cache_dirs = [
            Path.home() / '.cache' / 'ultralytics',
            Path('/tmp') / 'ultralytics',
        ]

    cache_dirs = [d for d in cache_dirs if d is not None]

    found_cache = False
    for cache_dir in cache_dirs:
        if cache_dir.exists():
            print(f"   ✅ {cache_dir}")

            # List models in cache
            models_in_cache = list(cache_dir.rglob("*.pt"))
            if models_in_cache:
                print(f"   Found {len(models_in_cache)} model(s):")
                for model in models_in_cache:
                    size = model.stat().st_size / (1024 * 1024)  # MB
                    print(f"   - {model.name} ({size:.1f} MB)")
                    print(f"     Path: {model}")
                found_cache = True
            else:
                print("   ⚠️  Cache directory exists but no models found")
        else:
            print(f"   ❌ Not found: {cache_dir}")

    if not found_cache:
        print("\n   💡 Models will be downloaded here on first use")

    # 3. Current working directory
    print("\n3️⃣  Current working directory:")
    cwd_models = list(Path(".").glob("*.pt"))
    if cwd_models:
        print(f"   Found {len(cwd_models)} model(s) in current directory:")
        for model in cwd_models:
            size = model.stat().st_size / (1024 * 1024)  # MB
            print(f"   - {model.name} ({size:.1f} MB)")
    else:
        print("   No .pt files in current directory")

    print("\n" + "=" * 70)
    print("\n💡 How Ultralytics YOLO Works:")
    print("   1. When you use 'yolov8m-pose.pt', Ultralytics checks its cache")
    print("   2. If not found, it downloads from GitHub automatically")
    print("   3. Saves to cache directory (NOT in your project)")
    print("   4. Reuses the cached model for all projects")
    print("\n   This is NORMAL behavior - you don't need models in project folder!")

    print("\n" + "=" * 70)
    print("\n🧪 Testing YOLOv8 Model Download...")
    print("-" * 70)

    try:
        from ultralytics import YOLO
        print("✅ Ultralytics library imported successfully")

        # Try to load a model (this will download if not exists)
        print("\n📥 Loading yolov8n-pose.pt (smallest model for testing)...")
        print("   This may take a minute if downloading for the first time...")

        model = YOLO('yolov8n-pose.pt')
        print("✅ Model loaded successfully!")

        # Show where it was loaded from
        if hasattr(model, 'ckpt_path'):
            print(f"\n📍 Model loaded from: {model.ckpt_path}")

        print("\n📊 Model Information:")
        print(f"   Model type: {model.task}")
        print(f"   Model name: {model.model_name if hasattr(model, 'model_name') else 'N/A'}")

        # Check cache location
        print("\n🗂️  Ultralytics Cache Location:")
        try:
            from ultralytics.utils import SETTINGS
            cache_dir = SETTINGS.get('datasets_dir', 'Unknown')
            print(f"   Datasets: {cache_dir}")
            weights_dir = Path.home() / '.config' / 'Ultralytics' if os.name != 'nt' else Path.home() / 'AppData' / 'Roaming' / 'Ultralytics'
            print(f"   Weights: {weights_dir}")
        except:
            print("   Could not determine cache location")

    except ImportError:
        print("❌ Ultralytics not installed")
        print("   Install with: pip install ultralytics")
    except Exception as e:
        print(f"❌ Error: {e}")

    print("\n" + "=" * 70)
    print("\n✅ Summary:")
    print("   - YOLOv8 models are auto-downloaded to system cache")
    print("   - NOT stored in your project's models/ folder")
    print("   - Only PPE detection model needs to be in models/")
    print("\n📁 Required in models/ folder:")
    print("   ✅ models/ppe_detection_best.pt (your custom PPE model)")
    print("   ❌ NOT needed: yolov8*-pose.pt (auto-cached by Ultralytics)")
    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    check_yolov8_models()
