"""
Model configuration and management.
"""

import os
from typing import Dict, Any


class ModelConfig:
    """
    Configuration for detection models.
    """

    # Default model configurations
    MODELS = {
        "yolov9_pose": {
            "name": "YOLOv9-Pose",
            "filename": "yolov9c-pose.pt",
            "input_size": 640,
            "description": "Pose detection model for human keypoint detection",
            "url": "https://github.com/WongKinYiu/yolov9/releases/download/v0.1/yolov9-c-pose-converted.pt",
        },
        "ppe_detection": {
            "name": "PPE Detection",
            "filename": "ppe_detection_best.pt",
            "input_size": 640,
            "description": "Custom trained model for PPE detection",
            "url": None,  # Replace with your model URL
        },
    }

    @classmethod
    def get_model_path(cls, model_key: str, models_dir: str = "models") -> str:
        """
        Get full path to model file.

        Args:
            model_key: Model key (e.g., "yolov9_pose")
            models_dir: Models directory

        Returns:
            Full path to model file
        """
        if model_key not in cls.MODELS:
            raise ValueError(f"Unknown model: {model_key}")

        filename = cls.MODELS[model_key]["filename"]
        return os.path.join(models_dir, filename)

    @classmethod
    def check_model_exists(cls, model_key: str, models_dir: str = "models") -> bool:
        """
        Check if model file exists.

        Args:
            model_key: Model key
            models_dir: Models directory

        Returns:
            True if model exists
        """
        path = cls.get_model_path(model_key, models_dir)
        return os.path.exists(path)

    @classmethod
    def get_missing_models(cls, models_dir: str = "models") -> list:
        """
        Get list of missing models.

        Args:
            models_dir: Models directory

        Returns:
            List of missing model keys
        """
        missing = []

        for model_key in cls.MODELS.keys():
            if not cls.check_model_exists(model_key, models_dir):
                missing.append(model_key)

        return missing

    @classmethod
    def print_model_status(cls, models_dir: str = "models"):
        """
        Print status of all models.

        Args:
            models_dir: Models directory
        """
        print("\n📦 Model Status:")
        print("=" * 60)

        for model_key, model_info in cls.MODELS.items():
            exists = cls.check_model_exists(model_key, models_dir)
            status = "✅" if exists else "❌"
            path = cls.get_model_path(model_key, models_dir)

            print(f"{status} {model_info['name']}")
            print(f"   Path: {path}")
            print(f"   Exists: {exists}")
            print()
