"""
Keypoint configuration widget for selecting which body keypoints to display.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QCheckBox, QPushButton, QLabel
)
from PyQt6.QtCore import pyqtSignal
from typing import Dict, List


class KeypointConfigWidget(QWidget):
    """
    Widget for configuring which pose keypoints to display.
    """

    # Signal emitted when keypoint selection changes
    config_changed = pyqtSignal(dict)

    # COCO Pose keypoints
    KEYPOINT_GROUPS = {
        "หัว (Head)": {
            "nose": 0,
        },
        "ตา (Eyes)": {
            "left_eye": 1,
            "right_eye": 2,
        },
        "หู (Ears)": {
            "left_ear": 3,
            "right_ear": 4,
        },
        "ไหล่ (Shoulders)": {
            "left_shoulder": 5,
            "right_shoulder": 6,
        },
        "ข้อศอก (Elbows)": {
            "left_elbow": 7,
            "right_elbow": 8,
        },
        "ข้อมือ (Wrists)": {
            "left_wrist": 9,
            "right_wrist": 10,
        },
        "สะโพก (Hips)": {
            "left_hip": 11,
            "right_hip": 12,
        },
        "เข่า (Knees)": {
            "left_knee": 13,
            "right_knee": 14,
        },
        "ข้อเท้า (Ankles)": {
            "left_ankle": 15,
            "right_ankle": 16,
        },
    }

    def __init__(self, parent=None):
        """Initialize keypoint configuration widget."""
        super().__init__(parent)

        self.checkboxes: Dict[str, QCheckBox] = {}
        self.setup_ui()

        # Default: all keypoints enabled
        self.select_all()

    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)

        # Title and buttons
        header_layout = QHBoxLayout()

        title_label = QLabel("เลือกจุดร่างกายที่ต้องการแสดง")
        title_label.setStyleSheet("font-weight: bold; font-size: 11px;")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # Select all / Deselect all buttons
        select_all_btn = QPushButton("เลือกทั้งหมด")
        select_all_btn.clicked.connect(self.select_all)
        select_all_btn.setMaximumWidth(100)
        header_layout.addWidget(select_all_btn)

        deselect_all_btn = QPushButton("ไม่เลือก")
        deselect_all_btn.clicked.connect(self.deselect_all)
        deselect_all_btn.setMaximumWidth(80)
        header_layout.addWidget(deselect_all_btn)

        layout.addLayout(header_layout)

        # Create checkboxes for each keypoint group
        for group_name, keypoints in self.KEYPOINT_GROUPS.items():
            group_box = QGroupBox(group_name)
            group_layout = QVBoxLayout()

            for kpt_name, kpt_idx in keypoints.items():
                # Create checkbox
                checkbox = QCheckBox(self._translate_keypoint(kpt_name))
                checkbox.setChecked(True)
                checkbox.stateChanged.connect(self.on_config_changed)

                # Store checkbox reference
                self.checkboxes[kpt_name] = checkbox

                group_layout.addWidget(checkbox)

            group_box.setLayout(group_layout)
            layout.addWidget(group_box)

        # Add stretch at bottom
        layout.addStretch()

    def _translate_keypoint(self, kpt_name: str) -> str:
        """Translate keypoint name to Thai."""
        translations = {
            "nose": "จมูก",
            "left_eye": "ตาซ้าย",
            "right_eye": "ตาขวา",
            "left_ear": "หูซ้าย",
            "right_ear": "หูขวา",
            "left_shoulder": "ไหล่ซ้าย",
            "right_shoulder": "ไหล่ขวา",
            "left_elbow": "ข้อศอกซ้าย",
            "right_elbow": "ข้อศอกขวา",
            "left_wrist": "ข้อมือซ้าย",
            "right_wrist": "ข้อมือขวา",
            "left_hip": "สะโพกซ้าย",
            "right_hip": "สะโพกขวา",
            "left_knee": "เข่าซ้าย",
            "right_knee": "เข่าขวา",
            "left_ankle": "ข้อเท้าซ้าย",
            "right_ankle": "ข้อเท้าขวา",
        }
        return translations.get(kpt_name, kpt_name)

    def select_all(self):
        """Select all keypoints."""
        for checkbox in self.checkboxes.values():
            checkbox.setChecked(True)

    def deselect_all(self):
        """Deselect all keypoints."""
        for checkbox in self.checkboxes.values():
            checkbox.setChecked(False)

    def on_config_changed(self):
        """Handle configuration change."""
        config = self.get_config()
        self.config_changed.emit(config)

    def get_config(self) -> Dict[str, any]:
        """
        Get current keypoint configuration.

        Returns:
            Dictionary with enabled keypoint indices
        """
        enabled_keypoints = []

        for kpt_name, checkbox in self.checkboxes.items():
            if checkbox.isChecked():
                # Find keypoint index
                for group_keypoints in self.KEYPOINT_GROUPS.values():
                    if kpt_name in group_keypoints:
                        enabled_keypoints.append(group_keypoints[kpt_name])
                        break

        return {
            "enabled_keypoints": enabled_keypoints,
            "show_all": len(enabled_keypoints) == 17,  # All 17 COCO keypoints
        }

    def set_config(self, config: Dict[str, any]):
        """
        Set keypoint configuration.

        Args:
            config: Configuration dictionary
        """
        enabled = set(config.get("enabled_keypoints", []))

        for kpt_name, checkbox in self.checkboxes.items():
            # Find keypoint index
            for group_keypoints in self.KEYPOINT_GROUPS.values():
                if kpt_name in group_keypoints:
                    kpt_idx = group_keypoints[kpt_name]
                    checkbox.setChecked(kpt_idx in enabled)
                    break
