"""
Camera connection configuration dialog for USB and RTSP sources with save/load capability.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox,
    QRadioButton, QLabel, QLineEdit, QSpinBox,
    QPushButton, QComboBox, QFormLayout, QMessageBox,
    QListWidget, QListWidgetItem, QSplitter, QInputDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from typing import Dict, Any, Optional
import cv2
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.camera_config_manager import CameraConfigManager


class CameraConnectionDialog(QDialog):
    """
    Dialog for configuring camera connection (USB or RTSP) with save/load.
    """

    # Signal emitted when camera source is selected
    camera_selected = pyqtSignal(dict)

    def __init__(self, parent=None, current_config: Dict[str, Any] = None):
        """
        Initialize camera connection dialog.

        Args:
            parent: Parent widget
            current_config: Current camera configuration
        """
        super().__init__(parent)
        self.current_config = current_config or {}
        self.config_manager = CameraConfigManager()
        self.setup_ui()
        self.refresh_saved_cameras()

    def setup_ui(self):
        """Setup the user interface."""
        self.setWindowTitle("ตั้งค่าการเชื่อมต่อกล้อง")
        self.setModal(True)
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)

        main_layout = QHBoxLayout(self)

        # Create splitter for saved cameras list and settings
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left side: Saved cameras list
        left_widget = self.create_saved_cameras_panel()
        splitter.addWidget(left_widget)

        # Right side: Camera settings
        right_widget = self.create_camera_settings_panel()
        splitter.addWidget(right_widget)

        # Set splitter sizes (30% left, 70% right)
        splitter.setSizes([250, 550])

        main_layout.addWidget(splitter)

    def create_saved_cameras_panel(self):
        """Create saved cameras list panel."""
        widget = QGroupBox("กล้องที่บันทึกไว้")
        layout = QVBoxLayout()

        # Saved cameras list
        self.saved_cameras_list = QListWidget()
        self.saved_cameras_list.itemClicked.connect(self.on_camera_item_clicked)
        self.saved_cameras_list.itemDoubleClicked.connect(self.on_camera_item_double_clicked)
        layout.addWidget(self.saved_cameras_list)

        # Buttons for saved cameras
        btn_layout = QVBoxLayout()

        load_btn = QPushButton("📥 โหลด")
        load_btn.clicked.connect(self.load_selected_camera)
        btn_layout.addWidget(load_btn)

        delete_btn = QPushButton("🗑️ ลบ")
        delete_btn.clicked.connect(self.delete_selected_camera)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 6px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        btn_layout.addWidget(delete_btn)

        btn_layout.addStretch()

        layout.addLayout(btn_layout)

        # Info label
        info_label = QLabel("💡 ดับเบิ้ลคลิกเพื่อโหลดค่า")
        info_label.setStyleSheet("color: #888; font-size: 9px;")
        layout.addWidget(info_label)

        widget.setLayout(layout)
        return widget

    def create_camera_settings_panel(self):
        """Create camera settings panel."""
        widget = QGroupBox("ตั้งค่ากล้อง")
        layout = QVBoxLayout()

        # Camera name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("ชื่อกล้อง:"))
        self.camera_name_input = QLineEdit()
        self.camera_name_input.setPlaceholderText("เช่น: กล้องหน้าโรงงาน, CCTV ทางเข้า")
        name_layout.addWidget(self.camera_name_input)
        layout.addLayout(name_layout)

        # Camera type selection
        type_group = QGroupBox("ประเภทกล้อง")
        type_layout = QVBoxLayout()

        self.usb_radio = QRadioButton("📹 USB Camera (กล้องเชื่อมต่อผ่าน USB)")
        self.rtsp_radio = QRadioButton("🌐 RTSP Camera (กล้อง IP/Network)")
        self.file_radio = QRadioButton("📁 Video File (ไฟล์วิดีโอ)")

        self.usb_radio.setChecked(True)
        self.usb_radio.toggled.connect(self.on_type_changed)
        self.rtsp_radio.toggled.connect(self.on_type_changed)
        self.file_radio.toggled.connect(self.on_type_changed)

        type_layout.addWidget(self.usb_radio)
        type_layout.addWidget(self.rtsp_radio)
        type_layout.addWidget(self.file_radio)
        type_group.setLayout(type_layout)
        layout.addWidget(type_group)

        # USB Camera settings
        self.usb_group = QGroupBox("USB Camera Settings")
        usb_layout = QFormLayout()

        self.usb_combo = QComboBox()
        self.refresh_usb_cameras()
        usb_layout.addRow("เลือกกล้อง:", self.usb_combo)

        refresh_btn = QPushButton("🔄 ค้นหากล้อง")
        refresh_btn.clicked.connect(self.refresh_usb_cameras)
        usb_layout.addRow("", refresh_btn)

        self.usb_group.setLayout(usb_layout)
        layout.addWidget(self.usb_group)

        # RTSP Camera settings
        self.rtsp_group = QGroupBox("RTSP Camera Settings")
        rtsp_layout = QFormLayout()

        self.rtsp_url_input = QLineEdit()
        self.rtsp_url_input.setPlaceholderText("rtsp://username:password@192.168.1.100:554/stream")
        rtsp_layout.addRow("RTSP URL:", self.rtsp_url_input)

        examples = QLabel(
            "ตัวอย่าง:\n"
            "• rtsp://admin:12345@192.168.1.100:554/stream1\n"
            "• rtsp://192.168.1.100:8554/live"
        )
        examples.setStyleSheet("color: #888; font-size: 9px;")
        rtsp_layout.addRow("", examples)

        self.rtsp_username_input = QLineEdit()
        self.rtsp_username_input.setPlaceholderText("admin (ถ้ามี)")
        rtsp_layout.addRow("Username:", self.rtsp_username_input)

        self.rtsp_password_input = QLineEdit()
        self.rtsp_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.rtsp_password_input.setPlaceholderText("password (ถ้ามี)")
        rtsp_layout.addRow("Password:", self.rtsp_password_input)

        test_rtsp_btn = QPushButton("🧪 ทดสอบการเชื่อมต่อ")
        test_rtsp_btn.clicked.connect(self.test_rtsp_connection)
        rtsp_layout.addRow("", test_rtsp_btn)

        self.rtsp_group.setLayout(rtsp_layout)
        self.rtsp_group.setVisible(False)
        layout.addWidget(self.rtsp_group)

        # Video file settings
        self.file_group = QGroupBox("Video File Settings")
        file_layout = QFormLayout()

        self.file_path_input = QLineEdit()
        self.file_path_input.setPlaceholderText("C:/videos/test.mp4")
        file_layout.addRow("ไฟล์วิดีโอ:", self.file_path_input)

        browse_btn = QPushButton("📂 เลือกไฟล์")
        browse_btn.clicked.connect(self.browse_video_file)
        file_layout.addRow("", browse_btn)

        self.file_group.setLayout(file_layout)
        self.file_group.setVisible(False)
        layout.addWidget(self.file_group)

        # Camera properties
        props_group = QGroupBox("Camera Properties")
        props_layout = QFormLayout()

        self.width_spinbox = QSpinBox()
        self.width_spinbox.setRange(320, 3840)
        self.width_spinbox.setValue(1280)
        self.width_spinbox.setSingleStep(160)
        props_layout.addRow("ความกว้าง (Width):", self.width_spinbox)

        self.height_spinbox = QSpinBox()
        self.height_spinbox.setRange(240, 2160)
        self.height_spinbox.setValue(720)
        self.height_spinbox.setSingleStep(120)
        props_layout.addRow("ความสูง (Height):", self.height_spinbox)

        self.fps_spinbox = QSpinBox()
        self.fps_spinbox.setRange(1, 60)
        self.fps_spinbox.setValue(30)
        props_layout.addRow("FPS:", self.fps_spinbox)

        props_group.setLayout(props_layout)
        layout.addWidget(props_group)

        # Action buttons
        button_layout = QHBoxLayout()

        save_btn = QPushButton("💾 บันทึกกล้อง")
        save_btn.clicked.connect(self.save_current_camera)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        button_layout.addWidget(save_btn)

        connect_btn = QPushButton("✅ เชื่อมต่อ")
        connect_btn.clicked.connect(self.connect_camera)
        connect_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        button_layout.addWidget(connect_btn)

        cancel_btn = QPushButton("❌ ยกเลิก")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

        widget.setLayout(layout)
        return widget

    def refresh_usb_cameras(self):
        """Scan and list available USB cameras."""
        self.usb_combo.clear()

        # Check for available cameras (0-9)
        available_cameras = []
        for i in range(10):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                available_cameras.append(i)
                cap.release()

        if available_cameras:
            for cam_id in available_cameras:
                self.usb_combo.addItem(f"Camera {cam_id}", cam_id)
        else:
            self.usb_combo.addItem("ไม่พบกล้อง USB", -1)

    def on_type_changed(self):
        """Handle camera type selection change."""
        self.usb_group.setVisible(self.usb_radio.isChecked())
        self.rtsp_group.setVisible(self.rtsp_radio.isChecked())
        self.file_group.setVisible(self.file_radio.isChecked())

    def test_rtsp_connection(self):
        """Test RTSP connection."""
        url = self.get_rtsp_url()

        if not url:
            QMessageBox.warning(self, "ข้อผิดพลาด", "กรุณากรอก RTSP URL")
            return

        QMessageBox.information(
            self, "กำลังทดสอบ",
            f"กำลังเชื่อมต่อไปยัง:\n{url}\n\nกรุณารอสักครู่..."
        )

        cap = cv2.VideoCapture(url)
        if cap.isOpened():
            ret, frame = cap.read()
            cap.release()

            if ret:
                QMessageBox.information(
                    self, "สำเร็จ",
                    "✅ เชื่อมต่อกล้อง RTSP สำเร็จ!\nสามารถรับภาพได้"
                )
            else:
                QMessageBox.warning(
                    self, "คำเตือน",
                    "⚠️ เชื่อมต่อได้แต่ไม่สามารถอ่านภาพ\nตรวจสอบ stream path"
                )
        else:
            QMessageBox.critical(
                self, "ล้มเหลว",
                "❌ ไม่สามารถเชื่อมต่อกล้อง RTSP\n\n"
                "กรุณาตรวจสอบ:\n• URL ถูกต้อง\n• กล้องออนไลน์\n"
                "• Username/Password ถูกต้อง\n• Network เชื่อมต่อได้"
            )

    def browse_video_file(self):
        """Browse for video file."""
        from PyQt6.QtWidgets import QFileDialog

        filename, _ = QFileDialog.getOpenFileName(
            self, "เลือกไฟล์วิดีโอ", "",
            "Video Files (*.mp4 *.avi *.mov *.mkv *.flv);;All Files (*.*)"
        )

        if filename:
            self.file_path_input.setText(filename)

    def get_rtsp_url(self) -> str:
        """Build RTSP URL from inputs."""
        url = self.rtsp_url_input.text().strip()

        if not url:
            return ""

        username = self.rtsp_username_input.text().strip()
        password = self.rtsp_password_input.text().strip()

        if username and password and "@" not in url:
            if url.startswith("rtsp://"):
                url = f"rtsp://{username}:{password}@{url[7:]}"

        return url

    def get_current_config(self) -> Dict[str, Any]:
        """Get current camera configuration from form."""
        config = {
            "name": self.camera_name_input.text().strip() or "Unnamed Camera",
            "width": self.width_spinbox.value(),
            "height": self.height_spinbox.value(),
            "fps": self.fps_spinbox.value(),
        }

        if self.usb_radio.isChecked():
            camera_id = self.usb_combo.currentData()
            config["type"] = "usb"
            config["source"] = camera_id
        elif self.rtsp_radio.isChecked():
            url = self.get_rtsp_url()
            config["type"] = "rtsp"
            config["source"] = url
        elif self.file_radio.isChecked():
            filepath = self.file_path_input.text().strip()
            config["type"] = "file"
            config["source"] = filepath

        return config

    def load_camera_config(self, config: Dict[str, Any]):
        """Load camera configuration into form."""
        # Set camera name
        self.camera_name_input.setText(config.get("name", ""))

        # Set camera type
        camera_type = config.get("type", "usb")

        if camera_type == "usb":
            self.usb_radio.setChecked(True)
            camera_id = config.get("source", 0)
            index = self.usb_combo.findData(camera_id)
            if index >= 0:
                self.usb_combo.setCurrentIndex(index)

        elif camera_type == "rtsp":
            self.rtsp_radio.setChecked(True)
            self.rtsp_url_input.setText(config.get("source", ""))

        elif camera_type == "file":
            self.file_radio.setChecked(True)
            self.file_path_input.setText(config.get("source", ""))

        # Set properties
        self.width_spinbox.setValue(config.get("width", 1280))
        self.height_spinbox.setValue(config.get("height", 720))
        self.fps_spinbox.setValue(config.get("fps", 30))

    def refresh_saved_cameras(self):
        """Refresh saved cameras list."""
        self.saved_cameras_list.clear()

        cameras = self.config_manager.get_all_cameras()
        for name, config in cameras.items():
            item = QListWidgetItem(f"📹 {name}")
            item.setData(Qt.ItemDataRole.UserRole, name)

            # Add camera type icon
            cam_type = config.get("type", "usb").upper()
            item.setText(f"{'📹' if cam_type == 'USB' else '🌐' if cam_type == 'RTSP' else '📁'} {name}")

            self.saved_cameras_list.addItem(item)

    def on_camera_item_clicked(self, item: QListWidgetItem):
        """Handle camera item single click."""
        pass  # Could add preview here

    def on_camera_item_double_clicked(self, item: QListWidgetItem):
        """Handle camera item double click - load configuration."""
        self.load_selected_camera()

    def load_selected_camera(self):
        """Load selected camera configuration."""
        current_item = self.saved_cameras_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "คำเตือน", "กรุณาเลือกกล้องที่ต้องการโหลด")
            return

        camera_name = current_item.data(Qt.ItemDataRole.UserRole)
        config = self.config_manager.get_camera(camera_name)

        if config:
            self.load_camera_config(config)
            self.statusBar().showMessage(f"โหลดค่าจาก '{camera_name}' เรียบร้อย") if hasattr(self, 'statusBar') else None

    def delete_selected_camera(self):
        """Delete selected camera configuration."""
        current_item = self.saved_cameras_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "คำเตือน", "กรุณาเลือกกล้องที่ต้องการลบ")
            return

        camera_name = current_item.data(Qt.ItemDataRole.UserRole)

        reply = QMessageBox.question(
            self, "ยืนยันการลบ",
            f"ต้องการลบกล้อง '{camera_name}' ใช่หรือไม่?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            if self.config_manager.remove_camera(camera_name):
                self.refresh_saved_cameras()
                QMessageBox.information(self, "สำเร็จ", f"ลบกล้อง '{camera_name}' เรียบร้อยแล้ว")

    def save_current_camera(self):
        """Save current camera configuration."""
        config = self.get_current_config()
        camera_name = config["name"]

        # Check if camera already exists
        if self.config_manager.camera_exists(camera_name):
            reply = QMessageBox.question(
                self, "ยืนยันการเขียนทับ",
                f"กล้อง '{camera_name}' มีอยู่แล้ว\nต้องการเขียนทับใช่หรือไม่?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply != QMessageBox.StandardButton.Yes:
                return

        # Validate configuration
        if config["type"] == "usb" and config["source"] == -1:
            QMessageBox.warning(self, "ข้อผิดพลาด", "ไม่พบกล้อง USB")
            return
        elif config["type"] == "rtsp" and not config["source"]:
            QMessageBox.warning(self, "ข้อผิดพลาด", "กรุณากรอก RTSP URL")
            return
        elif config["type"] == "file" and not config["source"]:
            QMessageBox.warning(self, "ข้อผิดพลาด", "กรุณาเลือกไฟล์วิดีโอ")
            return

        # Save configuration
        if self.config_manager.add_camera(camera_name, config):
            self.refresh_saved_cameras()
            QMessageBox.information(
                self, "สำเร็จ",
                f"บันทึกกล้อง '{camera_name}' เรียบร้อยแล้ว"
            )

    def connect_camera(self):
        """Connect to camera with current settings."""
        config = self.get_current_config()

        # Validate
        if config["type"] == "usb" and config["source"] == -1:
            QMessageBox.warning(self, "ข้อผิดพลาด", "ไม่พบกล้อง USB")
            return
        elif config["type"] == "rtsp" and not config["source"]:
            QMessageBox.warning(self, "ข้อผิดพลาด", "กรุณากรอก RTSP URL")
            return
        elif config["type"] == "file" and not config["source"]:
            QMessageBox.warning(self, "ข้อผิดพลาด", "กรุณาเลือกไฟล์วิดีโอ")
            return

        # Emit signal
        self.camera_selected.emit(config)
        self.accept()
