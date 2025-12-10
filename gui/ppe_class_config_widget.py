"""
PPE class configuration widget for selecting which PPE items to detect.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QCheckBox, QPushButton, QLabel, QDialog, QLineEdit,
    QDialogButtonBox, QFormLayout, QMessageBox, QScrollArea
)
from PyQt6.QtCore import pyqtSignal, Qt
from typing import Dict, List, Any


class AddPPEDialog(QDialog):
    """Dialog for adding a new custom PPE item."""

    def __init__(self, parent=None, existing_classes: List[str] = None):
        """
        Initialize add PPE dialog.

        Args:
            parent: Parent widget
            existing_classes: List of existing PPE class names
        """
        super().__init__(parent)
        self.existing_classes = existing_classes or []
        self.setup_ui()

    def setup_ui(self):
        """Setup the user interface."""
        self.setWindowTitle("เพิ่ม PPE ใหม่")
        self.setModal(True)
        self.setMinimumWidth(400)

        layout = QFormLayout(self)

        # Class name (English, for detection)
        self.class_name_input = QLineEdit()
        self.class_name_input.setPlaceholderText("ตัวอย่าง: hardhat, earplugs")
        layout.addRow("ชื่อ Class (English):", self.class_name_input)

        # Thai name
        self.thai_name_input = QLineEdit()
        self.thai_name_input.setPlaceholderText("ตัวอย่าง: หมวกนิรภัย, ที่อุดหู")
        layout.addRow("ชื่อภาษาไทย:", self.thai_name_input)

        # English name
        self.english_name_input = QLineEdit()
        self.english_name_input.setPlaceholderText("ตัวอย่าง: Safety Hardhat, Earplugs")
        layout.addRow("ชื่อภาษาอังกฤษ:", self.english_name_input)

        # Icon/Emoji
        self.icon_input = QLineEdit()
        self.icon_input.setPlaceholderText("ตัวอย่าง: 🪖 (อิโมจิ หรือสัญลักษณ์)")
        self.icon_input.setMaxLength(10)
        layout.addRow("ไอคอน/อิโมจิ:", self.icon_input)

        # Required by default
        self.required_checkbox = QCheckBox("ตั้งเป็น PPE บังคับ (Required)")
        self.required_checkbox.setChecked(False)
        layout.addRow("", self.required_checkbox)

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.validate_and_accept)
        button_box.rejected.connect(self.reject)
        layout.addRow(button_box)

    def validate_and_accept(self):
        """Validate input and accept dialog."""
        class_name = self.class_name_input.text().strip().lower()
        thai_name = self.thai_name_input.text().strip()
        english_name = self.english_name_input.text().strip()

        # Validation
        if not class_name:
            QMessageBox.warning(self, "ข้อผิดพลาด", "กรุณากรอกชื่อ Class")
            return

        if not thai_name:
            QMessageBox.warning(self, "ข้อผิดพลาด", "กรุณากรอกชื่อภาษาไทย")
            return

        # Check for duplicates
        if class_name in self.existing_classes:
            QMessageBox.warning(
                self,
                "ข้อผิดพลาด",
                f"PPE ชื่อ '{class_name}' มีอยู่แล้วในระบบ"
            )
            return

        # Validate class name format (alphanumeric and underscore only)
        if not class_name.replace("_", "").replace("-", "").isalnum():
            QMessageBox.warning(
                self,
                "ข้อผิดพลาด",
                "ชื่อ Class ต้องเป็นตัวอักษรภาษาอังกฤษและตัวเลขเท่านั้น (a-z, 0-9, _, -)"
            )
            return

        self.accept()

    def get_ppe_data(self) -> Dict[str, Any]:
        """
        Get the PPE data from the form.

        Returns:
            Dictionary with PPE information
        """
        icon = self.icon_input.text().strip()
        if not icon:
            icon = "📦"  # Default icon

        return {
            "class_name": self.class_name_input.text().strip().lower(),
            "thai": self.thai_name_input.text().strip(),
            "english": self.english_name_input.text().strip() or self.thai_name_input.text().strip(),
            "icon": icon,
            "required": self.required_checkbox.isChecked(),
            "custom": True,  # Mark as custom PPE
        }


class PPEClassConfigWidget(QWidget):
    """
    Widget for configuring which PPE classes to detect.
    """

    # Signal emitted when class selection changes
    config_changed = pyqtSignal(dict)

    # Default PPE classes (Thai and English names)
    DEFAULT_PPE_CLASSES = {
        "helmet": {
            "thai": "หมวกนิรภัย",
            "english": "Safety Helmet",
            "icon": "🪖",
            "required": True,  # Default required
            "custom": False,
        },
        "vest": {
            "thai": "เสื้อสะท้อนแสง",
            "english": "Safety Vest",
            "icon": "🦺",
            "required": True,
            "custom": False,
        },
        "gloves": {
            "thai": "ถุงมือ",
            "english": "Safety Gloves",
            "icon": "🧤",
            "required": False,
            "custom": False,
        },
        "boots": {
            "thai": "รองเท้าบูท",
            "english": "Safety Boots",
            "icon": "🥾",
            "required": False,
            "custom": False,
        },
        "goggles": {
            "thai": "แว่นตานิรภัย",
            "english": "Safety Goggles",
            "icon": "🥽",
            "required": False,
            "custom": False,
        },
        "mask": {
            "thai": "หน้ากาก",
            "english": "Face Mask",
            "icon": "😷",
            "required": False,
            "custom": False,
        },
    }

    def __init__(self, parent=None, custom_ppe_classes: Dict[str, Any] = None):
        """
        Initialize PPE class configuration widget.

        Args:
            parent: Parent widget
            custom_ppe_classes: Custom PPE classes to add to defaults
        """
        super().__init__(parent)

        # Combine default and custom PPE classes
        self.ppe_classes = self.DEFAULT_PPE_CLASSES.copy()
        if custom_ppe_classes:
            self.ppe_classes.update(custom_ppe_classes)

        self.detect_checkboxes: Dict[str, QCheckBox] = {}
        self.required_checkboxes: Dict[str, QCheckBox] = {}
        self.delete_buttons: Dict[str, QPushButton] = {}

        self.main_layout = None
        self.ppe_rows_layout = None
        self.setup_ui()

    def setup_ui(self):
        """Setup the user interface."""
        self.main_layout = QVBoxLayout(self)

        # Title
        title_label = QLabel("เลือก PPE ที่ต้องการตรวจจับ")
        title_label.setStyleSheet("font-weight: bold; font-size: 11px;")
        self.main_layout.addWidget(title_label)

        # PPE selection group
        ppe_group = QGroupBox("อุปกรณ์ความปลอดภัย (PPE)")
        ppe_layout = QVBoxLayout()

        # Header row
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("PPE"), stretch=3)
        header_layout.addWidget(QLabel("ตรวจจับ"), stretch=1)
        header_layout.addWidget(QLabel("บังคับ"), stretch=1)
        header_layout.addWidget(QLabel(""), stretch=1)  # For delete button
        ppe_layout.addLayout(header_layout)

        # Add separator
        separator = QLabel("")
        separator.setStyleSheet("border-bottom: 1px solid #555;")
        separator.setMaximumHeight(1)
        ppe_layout.addWidget(separator)

        # Create container for PPE rows (for dynamic updates)
        self.ppe_rows_layout = QVBoxLayout()
        ppe_layout.addLayout(self.ppe_rows_layout)

        # Build PPE rows
        self.rebuild_ppe_rows()

        ppe_group.setLayout(ppe_layout)
        self.main_layout.addWidget(ppe_group)

        # Add PPE button
        add_ppe_btn = QPushButton("➕ เพิ่ม PPE ใหม่")
        add_ppe_btn.clicked.connect(self.add_custom_ppe)
        add_ppe_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        self.main_layout.addWidget(add_ppe_btn)

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

        self.main_layout.addLayout(button_layout)

        # Info label
        info_label = QLabel(
            "💡 หมายเหตุ: 'บังคับ' = PPE ที่ต้องสวมใส่ (ขาดจะถือว่า Violation)\n"
            "   PPE ที่เพิ่มเอง (สีเขียว) สามารถลบได้"
        )
        info_label.setStyleSheet("color: #888; font-size: 9px;")
        info_label.setWordWrap(True)
        self.main_layout.addWidget(info_label)

        # Add stretch
        self.main_layout.addStretch()

    def rebuild_ppe_rows(self):
        """Rebuild all PPE rows (used when adding/removing items)."""
        # Clear existing rows
        while self.ppe_rows_layout.count():
            child = self.ppe_rows_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self.clear_layout(child.layout())

        # Clear checkbox dictionaries
        self.detect_checkboxes.clear()
        self.required_checkboxes.clear()
        self.delete_buttons.clear()

        # Create row for each PPE class
        for class_name, class_info in self.ppe_classes.items():
            row_layout = QHBoxLayout()

            # PPE name label with icon
            name_label = QLabel(f"{class_info['icon']} {class_info['thai']}")
            name_label.setToolTip(class_info['english'])

            # Highlight custom PPE
            if class_info.get('custom', False):
                name_label.setStyleSheet("color: #28a745; font-weight: bold;")

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

            # Delete button (only for custom PPE)
            # Create a container widget for the delete button to prevent stretching
            delete_container = QWidget()
            delete_container_layout = QHBoxLayout(delete_container)
            delete_container_layout.setContentsMargins(0, 0, 0, 0)
            delete_container_layout.addStretch()

            if class_info.get('custom', False):
                delete_btn = QPushButton("🗑️")
                delete_btn.setFixedSize(35, 25)  # Fixed size to prevent expansion
                delete_btn.setToolTip(f"ลบ {class_info['thai']}")
                delete_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #dc3545;
                        color: white;
                        border: none;
                        padding: 2px;
                        border-radius: 3px;
                    }
                    QPushButton:hover {
                        background-color: #c82333;
                    }
                """)
                delete_btn.clicked.connect(
                    lambda checked, cls=class_name: self.delete_custom_ppe(cls)
                )
                self.delete_buttons[class_name] = delete_btn
                delete_container_layout.addWidget(delete_btn)

            delete_container_layout.addStretch()
            row_layout.addWidget(delete_container, stretch=1)

            self.ppe_rows_layout.addLayout(row_layout)

    def clear_layout(self, layout):
        """Recursively clear a layout."""
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self.clear_layout(child.layout())

    def add_custom_ppe(self):
        """Open dialog to add custom PPE."""
        existing_classes = list(self.ppe_classes.keys())
        dialog = AddPPEDialog(self, existing_classes)

        if dialog.exec():
            ppe_data = dialog.get_ppe_data()
            class_name = ppe_data.pop("class_name")

            # Add to PPE classes
            self.ppe_classes[class_name] = ppe_data

            # Rebuild UI
            self.rebuild_ppe_rows()

            # Emit config changed
            self.on_config_changed()

            QMessageBox.information(
                self,
                "สำเร็จ",
                f"เพิ่ม PPE '{ppe_data['thai']}' เรียบร้อยแล้ว"
            )

    def delete_custom_ppe(self, class_name: str):
        """
        Delete a custom PPE item.

        Args:
            class_name: Name of the PPE class to delete
        """
        class_info = self.ppe_classes.get(class_name)
        if not class_info:
            return

        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "ยืนยันการลบ",
            f"ต้องการลบ PPE '{class_info['thai']}' ใช่หรือไม่?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Remove from PPE classes
            del self.ppe_classes[class_name]

            # Rebuild UI
            self.rebuild_ppe_rows()

            # Emit config changed
            self.on_config_changed()

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

    def get_config(self) -> Dict[str, Any]:
        """
        Get current PPE class configuration.

        Returns:
            Dictionary with enabled classes, required classes, and custom PPE
        """
        enabled_classes = []
        required_classes = []

        for class_name in self.ppe_classes.keys():
            if self.detect_checkboxes[class_name].isChecked():
                enabled_classes.append(class_name)

                if self.required_checkboxes[class_name].isChecked():
                    required_classes.append(class_name)

        # Extract custom PPE classes for persistence
        custom_ppe = {
            name: info for name, info in self.ppe_classes.items()
            if info.get('custom', False)
        }

        return {
            "enabled_classes": enabled_classes,
            "required_classes": required_classes,
            "custom_ppe_classes": custom_ppe,
        }

    def set_config(self, config: Dict[str, Any]):
        """
        Set PPE class configuration.

        Args:
            config: Configuration dictionary
        """
        # Load custom PPE classes if provided
        custom_ppe = config.get("custom_ppe_classes", {})
        if custom_ppe:
            # Merge with existing classes
            for class_name, class_info in custom_ppe.items():
                if class_name not in self.ppe_classes:
                    self.ppe_classes[class_name] = class_info

            # Rebuild UI to show custom PPE
            self.rebuild_ppe_rows()

        enabled = set(config.get("enabled_classes", []))
        required = set(config.get("required_classes", []))

        for class_name in self.ppe_classes.keys():
            if class_name in self.detect_checkboxes:
                self.detect_checkboxes[class_name].setChecked(class_name in enabled)
                self.required_checkboxes[class_name].setChecked(class_name in required)
