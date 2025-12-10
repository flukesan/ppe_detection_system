"""
Model downloader utility for downloading pre-trained models.
"""

import os
from typing import Optional


class ModelDownloader:
    """
    Utility for managing model downloads.

    Note: YOLOv8-Pose models are automatically downloaded by Ultralytics
    when first used. This utility helps document available models.
    """

    # Available YOLO Pose models (auto-downloaded by Ultralytics)
    YOLO_POSE_MODELS = {
        "yolov8n-pose.pt": "Nano - Fastest, least accurate",
        "yolov8s-pose.pt": "Small - Good balance",
        "yolov8m-pose.pt": "Medium - Recommended",
        "yolov8l-pose.pt": "Large - High accuracy",
        "yolov8x-pose.pt": "Extra Large - Best accuracy",
    }

    def __init__(self, models_dir: str = "models"):
        """
        Initialize model downloader.

        Args:
            models_dir: Directory to save models
        """
        self.models_dir = models_dir
        os.makedirs(models_dir, exist_ok=True)

    def print_info(self):
        """
        Print information about available models.
        """
        print("\n" + "=" * 70)
        print("📦 PPE Detection System - Model Information")
        print("=" * 70)

        print("\n🎯 YOLOv8-Pose Models (Auto-downloaded by Ultralytics):")
        print("-" * 70)
        for model, desc in self.YOLO_POSE_MODELS.items():
            print(f"  • {model:20} - {desc}")

        print("\n💡 How to use:")
        print("  1. Models are automatically downloaded on first use")
        print("  2. Set model path in config.yaml:")
        print("     models:")
        print("       yolov8_pose:")
        print("         path: \"yolov8m-pose.pt\"  # Will auto-download")

        print("\n🛡️ PPE Detection Model:")
        print("-" * 70)
        print("  • Custom model required - must be trained on your PPE dataset")
        print("  • Recommended: Train YOLOv8 on PPE classes:")
        print("    - helmet, vest, gloves, boots, goggles, mask")
        print("  • Place trained model at: models/ppe_detection_best.pt")

        print("\n📚 Training Guide:")
        print("  1. Prepare dataset with PPE annotations")
        print("  2. Train using Ultralytics:")
        print("     yolo detect train data=ppe.yaml model=yolov8m.pt epochs=100")
        print("  3. Copy best.pt to models/ppe_detection_best.pt")

        print("\n" + "=" * 70)

    def check_ppe_model(self) -> bool:
        """
        Check if PPE detection model exists.

        Returns:
            True if model exists
        """
        ppe_model_path = os.path.join(self.models_dir, "ppe_detection_best.pt")
        return os.path.exists(ppe_model_path)

    def create_model_config(self, model_size: str = "m") -> dict:
        """
        Create recommended model configuration.

        Args:
            model_size: Model size (n/s/m/l/x)

        Returns:
            Configuration dictionary
        """
        valid_sizes = ["n", "s", "m", "l", "x"]
        if model_size not in valid_sizes:
            print(f"⚠️  Invalid model size: {model_size}")
            print(f"   Valid sizes: {valid_sizes}")
            model_size = "m"

        return {
            "yolov8_pose": {
                "path": f"yolov8{model_size}-pose.pt",
                "description": self.YOLO_POSE_MODELS.get(
                    f"yolov8{model_size}-pose.pt",
                    "YOLOv8 Pose model"
                ),
            },
            "ppe_detection": {
                "path": "models/ppe_detection_best.pt",
                "description": "Custom PPE detection model",
                "status": "✅ Found" if self.check_ppe_model() else "❌ Not found - must be trained",
            },
        }

    def get_recommended_model(self, gpu_available: bool = True) -> str:
        """
        Get recommended model based on hardware.

        Args:
            gpu_available: Whether GPU is available

        Returns:
            Recommended model name
        """
        if gpu_available:
            return "yolov8m-pose.pt"  # Medium - good balance
        else:
            return "yolov8n-pose.pt"  # Nano - fastest for CPU

    def setup_models(self):
        """
        Interactive setup for models.
        """
        print("\n🚀 Model Setup Wizard")
        print("=" * 70)

        # Check GPU
        try:
            import torch
            gpu_available = torch.cuda.is_available()
            if gpu_available:
                print("✅ GPU detected - Recommending YOLOv8m-pose")
            else:
                print("⚠️  No GPU detected - Recommending YOLOv8n-pose")
        except:
            gpu_available = False
            print("⚠️  PyTorch not installed - Cannot detect GPU")

        recommended = self.get_recommended_model(gpu_available)
        print(f"\n📋 Recommended model: {recommended}")

        # Check PPE model
        print("\n🛡️ Checking PPE Detection Model...")
        if self.check_ppe_model():
            print("✅ PPE detection model found!")
        else:
            print("❌ PPE detection model NOT found")
            print("\n⚠️  You need to provide a trained PPE detection model:")
            print("   1. Train your own model on PPE dataset")
            print("   2. Place it at: models/ppe_detection_best.pt")
            print("   3. Or update config.yaml with your model path")

        print("\n" + "=" * 70)
