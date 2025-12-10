"""
Configuration loader utility.
"""

import yaml
import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv


class ConfigLoader:
    """
    Load and manage application configuration from YAML and environment variables.
    """

    def __init__(self, config_path: str = "config.yaml", env_path: Optional[str] = ".env"):
        """
        Initialize configuration loader.

        Args:
            config_path: Path to YAML configuration file
            env_path: Path to .env file (optional)
        """
        self.config_path = config_path
        self.env_path = env_path
        self.config: Dict[str, Any] = {}

        self.load()

    def load(self):
        """Load configuration from files."""
        # Load environment variables
        if self.env_path and os.path.exists(self.env_path):
            load_dotenv(self.env_path)

        # Load YAML configuration
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)

        # Override with environment variables
        self._override_from_env()

    def _override_from_env(self):
        """Override configuration with environment variables."""
        # Camera settings
        if os.getenv("DEFAULT_CAMERA_ID"):
            self.config["camera"]["default_id"] = int(os.getenv("DEFAULT_CAMERA_ID"))

        # Detection settings
        if os.getenv("CONFIDENCE_THRESHOLD"):
            self.config["detection"]["confidence_threshold"] = float(
                os.getenv("CONFIDENCE_THRESHOLD")
            )

        if os.getenv("USE_GPU"):
            use_gpu = os.getenv("USE_GPU").lower() == "true"
            self.config["detection"]["use_gpu"] = use_gpu
            device = "cuda:0" if use_gpu else "cpu"
            self.config["models"]["yolov9_pose"]["device"] = device
            self.config["models"]["ppe_detection"]["device"] = device

        # Model paths
        if os.getenv("YOLOV9_POSE_MODEL"):
            self.config["models"]["yolov9_pose"]["path"] = os.getenv("YOLOV9_POSE_MODEL")

        if os.getenv("PPE_DETECTION_MODEL"):
            self.config["models"]["ppe_detection"]["path"] = os.getenv("PPE_DETECTION_MODEL")

        # Database
        if os.getenv("DATABASE_PATH"):
            self.config["database"]["path"] = os.getenv("DATABASE_PATH")

        # Logging
        if os.getenv("LOG_LEVEL"):
            self.config["logging"]["level"] = os.getenv("LOG_LEVEL")

        if os.getenv("LOG_PATH"):
            self.config["logging"]["path"] = os.getenv("LOG_PATH")

    def get(self, key: str = None, default: Any = None) -> Any:
        """
        Get configuration value.

        Args:
            key: Dot-separated key path (e.g., "camera.width")
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        if key is None:
            return self.config

        keys = key.split(".")
        value = self.config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any):
        """
        Set configuration value.

        Args:
            key: Dot-separated key path
            value: Value to set
        """
        keys = key.split(".")
        config = self.config

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value

    def save(self, path: Optional[str] = None):
        """
        Save configuration to file.

        Args:
            path: Path to save (default: original config_path)
        """
        save_path = path or self.config_path

        with open(save_path, 'w', encoding='utf-8') as f:
            yaml.safe_dump(self.config, f, default_flow_style=False, allow_unicode=True)

    def __getitem__(self, key: str) -> Any:
        """Allow dict-like access."""
        return self.get(key)

    def __setitem__(self, key: str, value: Any):
        """Allow dict-like assignment."""
        self.set(key, value)
