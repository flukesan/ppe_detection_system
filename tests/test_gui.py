"""
Unit tests for GUI components.
"""

import pytest
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow
from utils.config_loader import ConfigLoader
import sys


@pytest.fixture
def app():
    """Create QApplication instance."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app


@pytest.fixture
def config():
    """Load test configuration."""
    config_loader = ConfigLoader("config.yaml")
    return config_loader.config


def test_main_window_creation(app, config):
    """Test main window creation."""
    window = MainWindow(config)
    assert window is not None
    assert window.windowTitle() == config["application"]["name"]


def test_camera_widget_creation(app, config):
    """Test camera widget creation."""
    window = MainWindow(config)
    assert window.camera_widget is not None


def test_control_panel_creation(app, config):
    """Test control panel creation."""
    window = MainWindow(config)
    assert window.control_panel is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
