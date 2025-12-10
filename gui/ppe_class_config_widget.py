"""
PPE class configuration widget for selecting which PPE items to detect.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QCheckBox, QPushButton, QLabel
)
from PyQt6.QtCore import pyqtSignal
from typing import Dict, List


class PPEClassConfigWidget(QWidget):
    """
    Widget for configuring which PPE classes to detect.
    """

    # Signal emitted when class selection changes
    config_changed = pyqtSignal(dict)

    # PPE classes (Thai and English names)
    PPE_CLASSES = {
        "helmet": {
            "thai": "หมวกนิรภัย",
            "english": "Safety Helmet",
            "icon": "🪖",
            "required": True,  # Default required
        },
        "vest": {
            "thai": "เสื้อสะท้อนแสง",
            "english": "Safety Vest",
            "icon": "🦺",
            "required": True,
        },
        "gloves": {
            "thai": "ถุงมือ",
            "english": "Safety Gloves",
            "icon": "🧤",
            "required": False,
        },
        "boots": {
            "thai": "รองเท้าบูท",
            "english": "Safety Boots",
            "icon": "🥾",
            "required": False,
        },
        "goggles": {
            "thai": "แว่นตานิรภัย",
            "english": "Safety Goggles",
            "icon": "🥽",
            "required": False,
        },
        "mask": {
            "thai": "หน้ากาก",
            "english": "Face Mask",
            "icon": "😷",
            "required": False,
        },
    }

    def __init__(self, parent=None):
        """Initialize PPE class configuration widget."""
        super().__init__(parent)

        self.detect_checkboxes: Dict[str, QCheckBox] = {}
        self.required_checkboxes: Dict[str, QCheckBox] = {}
        self.setup_ui()

    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)

        # Title
        title_label = QLabel("เลือก PPE ที่ต้องการตรวจจับ")
        title_label.setStyleSheet("font-weight: bold; font-size: 11px;")
        layout.addWidget(title_label)

        # PPE selection group
        ppe_group = QGroupBox("อุปกรณ์ความปลอดภัย (PPE)")
        ppe_layout = QVBoxLayout()

        # Header row
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("PPE"), stretch=3)
        header_layout.addWidget(QLabel("ตรวจจับ"), stretch=1)
        header_layout.addWidget(QLabel("บังคับ"), stretch=1)
        ppe_layout.addLayout(header_layout)

        # Add separator
        separator = QLabel("")
        separator.setStyleSheet("border-bottom: 1px solid #555;")
        separator.setMaximumHeight(1)
        ppe_layout.addWidget(separator)

        # Create row for each PPE class
        for class_name, class_info in self.PPE_CLASSES.items():
            row_layout = QHBoxLayout()

            # PPE name label with icon
            name_label = QLabel(f"{class_info['icon']} {class_info['thai']}")
            name_label.setToolTip(class_info['english'])
            row_layout.addWidget(name_label, stretch=3)

            # Detect checkbox
            detect_checkbox = QCheckBox()
            detect_checkbox.setChecked(True)  # Default: detect all
            detect_checkbox.stateChanged.connect(self.on_config_changed)
            detect_checkbox.stateChanged.connect(
                lambda state, cls=class_name: self.on_detect_changed(cls, state)
            )
            self.detect_checkboxes[class_name] = detect_checkbox
            row_layout.addWidget(detect_checkbox, stretch=1)

            # Required checkbox
            required_checkbox = QCheckBox()
            required_checkbox.setChecked(class_info["required"])
            required_checkbox.stateChanged.connect(self.on_config_changed)
            self.required_checkboxes[class_name] = required_checkbox
            row_layout.addWidget(required_checkbox, stretch=1)

            ppe_layout.addLayout(row_layout)

        ppe_group.setLayout(ppe_layout)
        layout.addWidget(ppe_group)

        # Quick selection buttons
        button_layout = QHBoxLayout()

        # All button
        all_btn = QPushButton("ตรวจจับทั้งหมด")
        all_btn.clicked.connect(self.select_all_detect)
        button_layout.addWidget(all_btn)

        # Required only button
        required_btn = QPushButton("เฉพาะที่บังคับ")
        required_btn.clicked.connect(self.select_required_only)
        button_layout.addWidget(required_btn)

        # None button
        none_btn = QPushButton("ไม่ตรวจจับ")
        none_btn.clicked.connect(self.deselect_all_detect)
        button_layout.addWidget(none_btn)

        layout.addLayout(button_layout)

        # Info label
        info_label = QLabel(
            "💡 หมายเหตุ: 'บังคับ' = PPE ที่ต้องสวมใส่ (ขาดจะถือว่า Violation)"
        )
        info_label.setStyleSheet("color: #888; font-size: 9px;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        # Add stretch
        layout.addStretch()

    def on_detect_changed(self, class_name: str, state: int):
        """
        Handle detect checkbox state change.

        If detect is disabled, also disable required.
        """
        if state == 0:  # Unchecked
            self.required_checkboxes[class_name].setChecked(False)
            self.required_checkboxes[class_name].setEnabled(False)
        else:  # Checked
            self.required_checkboxes[class_name].setEnabled(True)

    def select_all_detect(self):
        """Select all PPE classes for detection."""
        for checkbox in self.detect_checkboxes.values():
            checkbox.setChecked(True)

    def deselect_all_detect(self):
        """Deselect all PPE classes."""
        for checkbox in self.detect_checkboxes.values():
            checkbox.setChecked(False)

    def select_required_only(self):
        """Select only required PPE classes."""
        for class_name, checkbox in self.detect_checkboxes.items():
            is_required = self.required_checkboxes[class_name].isChecked()
            checkbox.setChecked(is_required)

    def on_config_changed(self):
        """Handle configuration change."""
        config = self.get_config()
        self.config_changed.emit(config)

    def get_config(self) -> Dict[str, any]:
        """
        Get current PPE class configuration.

        Returns:
            Dictionary with enabled classes and required classes
        """
        enabled_classes = []
        required_classes = []

        for class_name in self.PPE_CLASSES.keys():
            if self.detect_checkboxes[class_name].isChecked():
                enabled_classes.append(class_name)

                if self.required_checkboxes[class_name].isChecked():
                    required_classes.append(class_name)

        return {
            "enabled_classes": enabled_classes,
            "required_classes": required_classes,
        }

    def set_config(self, config: Dict[str, any]):
        """
        Set PPE class configuration.

        Args:
            config: Configuration dictionary
        """
        enabled = set(config.get("enabled_classes", []))
        required = set(config.get("required_classes", []))

        for class_name in self.PPE_CLASSES.keys():
            self.detect_checkboxes[class_name].setChecked(class_name in enabled)
            self.required_checkboxes[class_name].setChecked(class_name in required)
