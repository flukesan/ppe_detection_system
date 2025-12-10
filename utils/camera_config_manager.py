"""
Camera configuration manager for saving and loading camera settings.
"""

import json
import os
from typing import Dict, List, Any, Optional
from pathlib import Path


class CameraConfigManager:
    """
    Manager for saving and loading camera configurations.
    """

    def __init__(self, config_file: str = "camera_configs.json"):
        """
        Initialize camera config manager.

        Args:
            config_file: Path to configuration file
        """
        # Use app data directory
        app_dir = Path.home() / ".ppe_detection_system"
        app_dir.mkdir(exist_ok=True)

        self.config_file = app_dir / config_file
        self.cameras: Dict[str, Dict[str, Any]] = {}
        self.load_configs()

    def load_configs(self):
        """Load camera configurations from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.cameras = data.get("cameras", {})
                print(f"✅ Loaded {len(self.cameras)} camera configurations")
            except Exception as e:
                print(f"⚠️ Failed to load camera configs: {e}")
                self.cameras = {}
        else:
            self.cameras = {}

    def save_configs(self):
        """Save camera configurations to file."""
        try:
            data = {
                "cameras": self.cameras,
                "version": "1.0"
            }

            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            print(f"✅ Saved {len(self.cameras)} camera configurations")
            return True
        except Exception as e:
            print(f"❌ Failed to save camera configs: {e}")
            return False

    def add_camera(self, name: str, config: Dict[str, Any]) -> bool:
        """
        Add or update a camera configuration.

        Args:
            name: Camera name (identifier)
            config: Camera configuration

        Returns:
            True if successful
        """
        self.cameras[name] = config
        return self.save_configs()

    def remove_camera(self, name: str) -> bool:
        """
        Remove a camera configuration.

        Args:
            name: Camera name

        Returns:
            True if successful
        """
        if name in self.cameras:
            del self.cameras[name]
            return self.save_configs()
        return False

    def get_camera(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get a camera configuration by name.

        Args:
            name: Camera name

        Returns:
            Camera configuration or None
        """
        return self.cameras.get(name)

    def get_all_cameras(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all camera configurations.

        Returns:
            Dictionary of camera configurations
        """
        return self.cameras.copy()

    def get_camera_names(self) -> List[str]:
        """
        Get list of camera names.

        Returns:
            List of camera names
        """
        return list(self.cameras.keys())

    def camera_exists(self, name: str) -> bool:
        """
        Check if camera configuration exists.

        Args:
            name: Camera name

        Returns:
            True if exists
        """
        return name in self.cameras

    def clear_all(self) -> bool:
        """
        Clear all camera configurations.

        Returns:
            True if successful
        """
        self.cameras = {}
        return self.save_configs()

    def get_last_used_camera(self) -> Optional[str]:
        """
        Get the last used camera name.

        Returns:
            Camera name or None
        """
        # Could be extended to track last used
        camera_names = self.get_camera_names()
        return camera_names[0] if camera_names else None
