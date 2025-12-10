"""
Main entry point for PPE Detection System.
"""

import sys
import os
import argparse
from PyQt6.QtWidgets import QApplication

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.config_loader import ConfigLoader
from utils.logger import setup_logger
from utils.model_downloader import ModelDownloader
from models.model_config import ModelConfig
from core.pose_based_detector import PoseBasedDetector
from gui.main_window import MainWindow


def check_models(config):
    """
    Check if required models are available.

    Args:
        config: Configuration dictionary

    Returns:
        True if all models are available
    """
    print("\n🔍 Checking models...")

    pose_model_path = config["models"]["yolov9_pose"]["path"]
    ppe_model_path = config["models"]["ppe_detection"]["path"]

    pose_exists = os.path.exists(pose_model_path)
    ppe_exists = os.path.exists(ppe_model_path)

    print(f"{'✅' if pose_exists else '❌'} Pose Model: {pose_model_path}")
    print(f"{'✅' if ppe_exists else '❌'} PPE Model: {ppe_model_path}")

    if not pose_exists or not ppe_exists:
        print("\n⚠️  Some models are missing!")
        print("You can download models using:")
        print("  python main.py --download-models")
        return False

    return True


def download_models():
    """Download required models."""
    print("\n📥 Downloading models...\n")

    downloader = ModelDownloader()

    # Download YOLOv9-Pose
    print("Downloading YOLOv9-Pose model...")
    downloader.download_model("yolov9c-pose")

    print("\n⚠️  Note: PPE detection model must be trained and placed in models/")
    print("   You can train your own model or obtain a pre-trained one.")

    print("\n✅ Download complete!")


def main():
    """Main application entry point."""
    parser = argparse.ArgumentParser(description="PPE Detection System")

    parser.add_argument(
        "--config",
        type=str,
        default="config.yaml",
        help="Path to configuration file"
    )

    parser.add_argument(
        "--download-models",
        action="store_true",
        help="Download required models"
    )

    parser.add_argument(
        "--check-models",
        action="store_true",
        help="Check model availability"
    )

    parser.add_argument(
        "--no-gui",
        action="store_true",
        help="Run without GUI (CLI mode - not yet implemented)"
    )

    parser.add_argument(
        "--camera",
        type=int,
        default=None,
        help="Camera ID to use"
    )

    parser.add_argument(
        "--video",
        type=str,
        default=None,
        help="Video file to process"
    )

    args = parser.parse_args()

    # Download models if requested
    if args.download_models:
        download_models()
        return

    # Load configuration
    try:
        config_loader = ConfigLoader(args.config)
        config = config_loader.config
    except Exception as e:
        print(f"❌ Failed to load configuration: {e}")
        return

    # Setup logger
    logger = setup_logger(
        log_path=config["logging"]["path"],
        level=config["logging"]["level"]
    )

    logger.info("=" * 60)
    logger.info("PPE Detection System Starting...")
    logger.info("=" * 60)

    # Check models
    if args.check_models:
        check_models(config)
        return

    if not check_models(config):
        return

    # CLI mode (not yet implemented)
    if args.no_gui:
        print("❌ CLI mode not yet implemented")
        print("   Please run in GUI mode (without --no-gui flag)")
        return

    # Create Qt Application
    app = QApplication(sys.argv)

    # Create main window
    window = MainWindow(config)

    # Initialize detector
    try:
        detector = PoseBasedDetector(
            pose_model_path=config["models"]["yolov9_pose"]["path"],
            ppe_model_path=config["models"]["ppe_detection"]["path"],
            config=config,
        )

        # Set detector to camera widget
        window.camera_widget.set_detector(detector)

        logger.info("✅ Detection system initialized successfully")

    except Exception as e:
        logger.error(f"❌ Failed to initialize detector: {e}")
        print(f"\n❌ Failed to initialize detector: {e}")
        print("\nPossible solutions:")
        print("  1. Make sure model files are in the correct location")
        print("  2. Check if CUDA is available (if use_gpu=True)")
        print("  3. Try setting use_gpu=False in config.yaml")
        return

    # Auto-start camera if specified
    if args.camera is not None:
        window.camera_widget.start_camera(args.camera)
    elif args.video is not None:
        window.camera_widget.open_video_file(args.video)

    # Show window
    window.show()

    logger.info("✅ Application started")
    print("\n✅ PPE Detection System is ready!")
    print(f"   Configuration: {args.config}")
    print(f"   Log file: {config['logging']['path']}")
    print("\n")

    # Run application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
