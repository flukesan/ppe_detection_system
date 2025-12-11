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
from core.fusion_detector import FusionDetector
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

    pose_model_path = config["models"]["yolov8_pose"]["path"]
    ppe_model_path = config["models"]["ppe_detection"]["path"]

    # YOLOv8-Pose will be auto-downloaded by Ultralytics
    print(f"✅ Pose Model: {pose_model_path} (auto-downloaded by Ultralytics)")

    ppe_exists = os.path.exists(ppe_model_path)
    print(f"{'✅' if ppe_exists else '❌'} PPE Model: {ppe_model_path}")

    if not ppe_exists:
        print("\n⚠️  PPE detection model is missing!")
        print("You need to:")
        print("  1. Train a YOLOv8 model on your PPE dataset")
        print("  2. Place the trained model at: models/ppe_detection_best.pt")
        print("\nFor model information, run:")
        print("  python main.py --model-info")
        return False

    return True


def show_model_info():
    """Show model information."""
    downloader = ModelDownloader()
    downloader.print_info()
    downloader.setup_models()


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
        "--model-info",
        action="store_true",
        help="Show model information and setup guide"
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

    # Show model info if requested
    if args.model_info:
        show_model_info()
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

    # Initialize detector (single or fusion based on config)
    try:
        multi_camera_enabled = config.get("multi_camera", {}).get("enabled", False)

        if multi_camera_enabled:
            # Multi-camera fusion detector
            num_cameras = config.get("multi_camera", {}).get("num_cameras", 2)
            logger.info(f"🎥 Initializing {num_cameras}-camera fusion detector...")

            detector = FusionDetector(
                pose_model_path=config["models"]["yolov8_pose"]["path"],
                ppe_model_path=config["models"]["ppe_detection"]["path"],
                config=config,
                num_cameras=num_cameras,
            )
        else:
            # Single camera detector
            logger.info("📹 Initializing single camera detector...")

            detector = PoseBasedDetector(
                pose_model_path=config["models"]["yolov8_pose"]["path"],
                ppe_model_path=config["models"]["ppe_detection"]["path"],
                config=config,
            )

        # Load detection zones if configured
        zones_file = config.get("detection", {}).get("zones_file", "data/detection_zones.json")
        if os.path.exists(zones_file):
            logger.info(f"📍 Loading detection zones from {zones_file}")
            try:
                if multi_camera_enabled:
                    # For fusion detector, load zones for each camera detector
                    for cam_detector in detector.detectors:
                        cam_detector.zone_manager.load_from_file(zones_file)
                else:
                    # For single detector
                    detector.zone_manager.load_from_file(zones_file)
                logger.info(f"✅ Detection zones loaded successfully")
            except Exception as e:
                logger.warning(f"⚠️ Failed to load detection zones: {e}")
        else:
            logger.info("📍 No detection zones configured (detecting everywhere)")

        # Set detector to window (which will set to camera widget)
        window.set_detector(detector)

        # Apply detection configuration if available
        if "detection_config" in config:
            det_config = config["detection_config"]

            if "keypoints" in det_config:
                enabled_keypoints = det_config["keypoints"].get("enabled_keypoints", [])
                if enabled_keypoints:
                    detector.set_enabled_keypoints(enabled_keypoints)

            if "ppe_classes" in det_config:
                enabled_classes = det_config["ppe_classes"].get("enabled_classes", [])
                required_classes = det_config["ppe_classes"].get("required_classes", [])

                if enabled_classes:
                    detector.set_enabled_ppe_classes(enabled_classes)
                if required_classes:
                    detector.set_required_ppe(required_classes)

        logger.info("✅ Detection system initialized successfully")

    except Exception as e:
        logger.error(f"❌ Failed to initialize detector: {e}")
        print(f"\n❌ Failed to initialize detector: {e}")
        print("\nPossible solutions:")
        print("  1. Make sure model files are in the correct location")
        print("  2. Check if CUDA is available (if use_gpu=True)")
        print("  3. Try setting use_gpu=False in config.yaml")
        import traceback
        traceback.print_exc()
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
