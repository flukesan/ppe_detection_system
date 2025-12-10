"""
Control panel for starting/stopping detection and configuring settings.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QGroupBox, QLabel, QSlider, QComboBox, QCheckBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from typing import Dict, Any


class ControlPanel(QWidget):
    """
    Control panel widget for system controls and settings.
    """

    # Signals
    start_requested = pyqtSignal(int)  # Emits camera ID
    stop_requested = pyqtSignal()
    settings_changed = pyqtSignal(dict)

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize control panel.

        Args:
            config: Application configuration
        """
        super().__init__()

        self.config = config
        self.is_running = False

        self.setup_ui()

    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)

        # Camera controls
        camera_group = QGroupBox("Camera Controls")
        camera_layout = QVBoxLayout()

        # Start/Stop button
        self.start_stop_btn = QPushButton("▶ Start Detection")
        self.start_stop_btn.clicked.connect(self.on_start_stop_clicked)
        camera_layout.addWidget(self.start_stop_btn)

        # Camera selection
        camera_select_layout = QHBoxLayout()
        camera_select_layout.addWidget(QLabel("Camera:"))
        self.camera_combo = QComboBox()
        self.camera_combo.addItems(["Camera 0", "Camera 1", "Camera 2", "Video File"])
        camera_select_layout.addWidget(self.camera_combo)
        camera_layout.addLayout(camera_select_layout)

        camera_group.setLayout(camera_layout)
        layout.addWidget(camera_group)

        # Detection settings
        detection_group = QGroupBox("Detection Settings")
        detection_layout = QVBoxLayout()

        # Confidence threshold
        conf_layout = QHBoxLayout()
        conf_layout.addWidget(QLabel("Confidence:"))
        self.conf_slider = QSlider(Qt.Orientation.Horizontal)
        self.conf_slider.setRange(0, 100)
        self.conf_slider.setValue(int(self.config["detection"]["confidence_threshold"] * 100))
        self.conf_slider.valueChanged.connect(self.on_settings_changed)
        conf_layout.addWidget(self.conf_slider)
        self.conf_label = QLabel(f"{self.conf_slider.value()}%")
        conf_layout.addWidget(self.conf_label)
        detection_layout.addLayout(conf_layout)

        # Violation threshold
        viol_layout = QHBoxLayout()
        viol_layout.addWidget(QLabel("Violation Threshold:"))
        self.viol_slider = QSlider(Qt.Orientation.Horizontal)
        self.viol_slider.setRange(0, 100)
        self.viol_slider.setValue(
            int(self.config["temporal_filter"]["violation_threshold"] * 100)
        )
        self.viol_slider.valueChanged.connect(self.on_settings_changed)
        viol_layout.addWidget(self.viol_slider)
        self.viol_label = QLabel(f"{self.viol_slider.value()}%")
        viol_layout.addWidget(self.viol_label)
        detection_layout.addLayout(viol_layout)

        detection_group.setLayout(detection_layout)
        layout.addWidget(detection_group)

        # Alert settings
        alert_group = QGroupBox("Alert Settings")
        alert_layout = QVBoxLayout()

        self.sound_checkbox = QCheckBox("Enable Sound Alerts")
        self.sound_checkbox.setChecked(self.config["alerts"]["sound"])
        self.sound_checkbox.stateChanged.connect(self.on_settings_changed)
        alert_layout.addWidget(self.sound_checkbox)

        self.record_checkbox = QCheckBox("Record Violations")
        self.record_checkbox.setChecked(self.config["video_recording"]["enabled"])
        self.record_checkbox.stateChanged.connect(self.on_settings_changed)
        alert_layout.addWidget(self.record_checkbox)

        alert_group.setLayout(alert_layout)
        layout.addWidget(alert_group)

        # Spacer
        layout.addStretch()

    def on_start_stop_clicked(self):
        """Handle start/stop button click."""
        if not self.is_running:
            # Start detection
            camera_id = self.camera_combo.currentIndex()
            self.start_requested.emit(camera_id)
            self.start_stop_btn.setText("⏸ Stop Detection")
            self.is_running = True
        else:
            # Stop detection
            self.stop_requested.emit()
            self.start_stop_btn.setText("▶ Start Detection")
            self.is_running = False

    def on_settings_changed(self):
        """Handle settings changes."""
        # Update labels
        self.conf_label.setText(f"{self.conf_slider.value()}%")
        self.viol_label.setText(f"{self.viol_slider.value()}%")

        # Emit new settings
        new_settings = {
            "detection": {
                "confidence_threshold": self.conf_slider.value() / 100.0,
            },
            "temporal_filter": {
                "violation_threshold": self.viol_slider.value() / 100.0,
            },
            "alerts": {
                "sound": self.sound_checkbox.isChecked(),
            },
            "video_recording": {
                "enabled": self.record_checkbox.isChecked(),
            },
        }

        self.settings_changed.emit(new_settings)
