"""
Configuration dialog for PPE detection settings.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
    QPushButton, QDialogButtonBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from typing import Dict

from .keypoint_config_widget import KeypointConfigWidget
from .ppe_class_config_widget import PPEClassConfigWidget


class ConfigDialog(QDialog):
    """
    Dialog for configuring PPE detection settings.
    """

    # Signal emitted when configuration is applied
    config_applied = pyqtSignal(dict)

    def __init__(self, parent=None, config: Dict = None):
        """
        Initialize configuration dialog.

        Args:
            parent: Parent widget
            config: Current configuration
        """
        super().__init__(parent)

        self.config = config or {}
        self.setup_ui()
        self.load_config()

    def setup_ui(self):
        """Setup the user interface."""
        self.setWindowTitle("ตั้งค่าการตรวจจับ PPE")
        self.setModal(True)
        self.resize(500, 600)

        layout = QVBoxLayout(self)

        # Create tab widget
        self.tabs = QTabWidget()

        # Keypoint configuration tab
        self.keypoint_widget = KeypointConfigWidget()
        self.tabs.addTab(self.keypoint_widget, "🦴 จุดร่างกาย")

        # PPE class configuration tab
        self.ppe_class_widget = PPEClassConfigWidget()
        self.tabs.addTab(self.ppe_class_widget, "🦺 อุปกรณ์ PPE")

        layout.addWidget(self.tabs)

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel |
            QDialogButtonBox.StandardButton.Apply
        )

        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.StandardButton.Apply).clicked.connect(
            self.on_apply
        )

        # Translate button text to Thai
        button_box.button(QDialogButtonBox.StandardButton.Ok).setText("ตกลง")
        button_box.button(QDialogButtonBox.StandardButton.Cancel).setText("ยกเลิก")
        button_box.button(QDialogButtonBox.StandardButton.Apply).setText("นำไปใช้")

        layout.addWidget(button_box)

    def load_config(self):
        """Load configuration into widgets."""
        # Load keypoint config
        if "keypoints" in self.config:
            self.keypoint_widget.set_config(self.config["keypoints"])

        # Load PPE class config
        if "ppe_classes" in self.config:
            self.ppe_class_widget.set_config(self.config["ppe_classes"])

    def get_config(self) -> Dict:
        """
        Get current configuration from widgets.

        Returns:
            Configuration dictionary
        """
        return {
            "keypoints": self.keypoint_widget.get_config(),
            "ppe_classes": self.ppe_class_widget.get_config(),
        }

    def on_apply(self):
        """Handle Apply button click."""
        config = self.get_config()
        self.config_applied.emit(config)

    def accept(self):
        """Handle OK button click."""
        self.on_apply()
        super().accept()
