"""
Detection configuration manager for saving and loading detection settings.
"""

import json
from typing import Dict, Any, Optional, List
from pathlib import Path


class DetectionConfigManager:
    """
    Manager for saving and loading detection configurations.
    """

    def __init__(self, config_file: str = "detection_config.json"):
        """
        Initialize detection config manager.

        Args:
            config_file: Path to configuration file
        """
        # Use app data directory
        app_dir = Path.home() / ".ppe_detection_system"
        app_dir.mkdir(exist_ok=True)

        self.config_file = app_dir / config_file
        self.config: Dict[str, Any] = {}
        self.load_config()

    def load_config(self):
        """Load detection configuration from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                print(f"✅ Loaded detection configuration")
            except Exception as e:
                print(f"⚠️ Failed to load detection config: {e}")
                self.config = self._get_default_config()
        else:
            self.config = self._get_default_config()

    def save_config(self):
        """Save detection configuration to file."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            print(f"✅ Saved detection configuration")
            return True
        except Exception as e:
            print(f"❌ Failed to save detection config: {e}")
            return False

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default detection configuration."""
        return {
            "keypoints": {
                "enabled_keypoints": list(range(17)),  # All keypoints enabled
                "show_all": True,
            },
            "ppe_classes": {
                "enabled_classes": ["helmet", "vest", "gloves", "boots", "goggles", "mask"],
                "required_classes": ["helmet", "vest"],
                "custom_ppe_classes": {},
            },
            "version": "1.0"
        }

    def get_config(self) -> Dict[str, Any]:
        """
        Get current detection configuration.

        Returns:
            Detection configuration dictionary
        """
        return self.config.copy()

    def update_config(self, config: Dict[str, Any]) -> bool:
        """
        Update detection configuration.

        Args:
            config: New configuration dictionary

        Returns:
            True if successful
        """
        self.config.update(config)
        return self.save_config()

    def get_keypoints_config(self) -> Dict[str, Any]:
        """Get keypoints configuration."""
        return self.config.get("keypoints", {
            "enabled_keypoints": list(range(17)),
            "show_all": True,
        })

    def get_ppe_classes_config(self) -> Dict[str, Any]:
        """Get PPE classes configuration."""
        return self.config.get("ppe_classes", {
            "enabled_classes": ["helmet", "vest", "gloves", "boots", "goggles", "mask"],
            "required_classes": ["helmet", "vest"],
            "custom_ppe_classes": {},
        })

    def set_keypoints_config(self, keypoints_config: Dict[str, Any]) -> bool:
        """
        Set keypoints configuration.

        Args:
            keypoints_config: Keypoints configuration

        Returns:
            True if successful
        """
        self.config["keypoints"] = keypoints_config
        return self.save_config()

    def set_ppe_classes_config(self, ppe_config: Dict[str, Any]) -> bool:
        """
        Set PPE classes configuration.

        Args:
            ppe_config: PPE classes configuration

        Returns:
            True if successful
        """
        self.config["ppe_classes"] = ppe_config
        return self.save_config()

    def reset_to_defaults(self) -> bool:
        """
        Reset configuration to defaults.

        Returns:
            True if successful
        """
        self.config = self._get_default_config()
        return self.save_config()

    def get_enabled_keypoints(self) -> List[int]:
        """Get list of enabled keypoints."""
        return self.config.get("keypoints", {}).get("enabled_keypoints", list(range(17)))

    def get_enabled_ppe_classes(self) -> List[str]:
        """Get list of enabled PPE classes."""
        return self.config.get("ppe_classes", {}).get(
            "enabled_classes",
            ["helmet", "vest", "gloves", "boots", "goggles", "mask"]
        )

    def get_required_ppe_classes(self) -> List[str]:
        """Get list of required PPE classes."""
        return self.config.get("ppe_classes", {}).get("required_classes", ["helmet", "vest"])

    def get_custom_ppe_classes(self) -> Dict[str, Any]:
        """Get custom PPE classes."""
        return self.config.get("ppe_classes", {}).get("custom_ppe_classes", {})
