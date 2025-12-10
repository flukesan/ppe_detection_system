"""
Camera connection configuration dialog for USB and RTSP sources.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox,
    QRadioButton, QLabel, QLineEdit, QSpinBox,
    QPushButton, QComboBox, QFormLayout, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from typing import Dict, Any
import cv2


class CameraConnectionDialog(QDialog):
    """
    Dialog for configuring camera connection (USB or RTSP).
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
        self.setup_ui()
        self.load_config()

    def setup_ui(self):
        """Setup the user interface."""
        self.setWindowTitle("ตั้งค่าการเชื่อมต่อกล้อง")
        self.setModal(True)
        self.setMinimumWidth(500)

        layout = QVBoxLayout(self)

        # Title
        title_label = QLabel("เลือกประเภทกล้อง")
        title_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        layout.addWidget(title_label)

        # Camera type selection
        self.usb_radio = QRadioButton("📹 USB Camera (กล้องเชื่อมต่อผ่าน USB)")
        self.rtsp_radio = QRadioButton("🌐 RTSP Camera (กล้อง IP/Network)")
        self.file_radio = QRadioButton("📁 Video File (ไฟล์วิดีโอ)")

        self.usb_radio.setChecked(True)
        self.usb_radio.toggled.connect(self.on_type_changed)
        self.rtsp_radio.toggled.connect(self.on_type_changed)
        self.file_radio.toggled.connect(self.on_type_changed)

        layout.addWidget(self.usb_radio)
        layout.addWidget(self.rtsp_radio)
        layout.addWidget(self.file_radio)

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

        # Common RTSP examples
        examples = QLabel(
            "ตัวอย่าง:\n"
            "• rtsp://admin:12345@192.168.1.100:554/stream1\n"
            "• rtsp://192.168.1.100:8554/live\n"
            "• rtsp://camera.local/h264"
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

        # Camera properties (common for all types)
        props_group = QGroupBox("Camera Properties (ตั้งค่ากล้อง)")
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

        # Buttons
        button_layout = QHBoxLayout()

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

        # Try to connect
        QMessageBox.information(self, "กำลังทดสอบ", f"กำลังเชื่อมต่อไปยัง:\n{url}\n\nกรุณารอสักครู่...")

        cap = cv2.VideoCapture(url)
        if cap.isOpened():
            ret, frame = cap.read()
            cap.release()

            if ret:
                QMessageBox.information(
                    self,
                    "สำเร็จ",
                    "✅ เชื่อมต่อกล้อง RTSP สำเร็จ!\nสามารถรับภาพได้"
                )
            else:
                QMessageBox.warning(
                    self,
                    "คำเตือน",
                    "⚠️ เชื่อมต่อได้แต่ไม่สามารถอ่านภาพ\nตรวจสอบ stream path"
                )
        else:
            QMessageBox.critical(
                self,
                "ล้มเหลว",
                "❌ ไม่สามารถเชื่อมต่อกล้อง RTSP\n\nกรุณาตรวจสอบ:\n"
                "• URL ถูกต้อง\n"
                "• กล้องออนไลน์\n"
                "• Username/Password ถูกต้อง\n"
                "• Network เชื่อมต่อได้"
            )

    def browse_video_file(self):
        """Browse for video file."""
        from PyQt6.QtWidgets import QFileDialog

        filename, _ = QFileDialog.getOpenFileName(
            self,
            "เลือกไฟล์วิดีโอ",
            "",
            "Video Files (*.mp4 *.avi *.mov *.mkv *.flv);;All Files (*.*)"
        )

        if filename:
            self.file_path_input.setText(filename)

    def get_rtsp_url(self) -> str:
        """
        Build RTSP URL from inputs.

        Returns:
            Complete RTSP URL
        """
        url = self.rtsp_url_input.text().strip()

        if not url:
            return ""

        # If username and password are provided separately, inject them
        username = self.rtsp_username_input.text().strip()
        password = self.rtsp_password_input.text().strip()

        if username and password and "@" not in url:
            # Insert credentials into URL
            if url.startswith("rtsp://"):
                url = f"rtsp://{username}:{password}@{url[7:]}"

        return url

    def load_config(self):
        """Load configuration from current config."""
        if not self.current_config:
            return

        camera_type = self.current_config.get("type", "usb")

        if camera_type == "usb":
            self.usb_radio.setChecked(True)
            camera_id = self.current_config.get("source", 0)
            index = self.usb_combo.findData(camera_id)
            if index >= 0:
                self.usb_combo.setCurrentIndex(index)

        elif camera_type == "rtsp":
            self.rtsp_radio.setChecked(True)
            self.rtsp_url_input.setText(self.current_config.get("source", ""))

        elif camera_type == "file":
            self.file_radio.setChecked(True)
            self.file_path_input.setText(self.current_config.get("source", ""))

        # Load properties
        self.width_spinbox.setValue(self.current_config.get("width", 1280))
        self.height_spinbox.setValue(self.current_config.get("height", 720))
        self.fps_spinbox.setValue(self.current_config.get("fps", 30))

    def connect_camera(self):
        """Connect to selected camera source."""
        config = {}

        # Get camera type and source
        if self.usb_radio.isChecked():
            camera_id = self.usb_combo.currentData()
            if camera_id == -1:
                QMessageBox.warning(self, "ข้อผิดพลาด", "ไม่พบกล้อง USB")
                return

            config["type"] = "usb"
            config["source"] = camera_id

        elif self.rtsp_radio.isChecked():
            url = self.get_rtsp_url()
            if not url:
                QMessageBox.warning(self, "ข้อผิดพลาด", "กรุณากรอก RTSP URL")
                return

            config["type"] = "rtsp"
            config["source"] = url

        elif self.file_radio.isChecked():
            filepath = self.file_path_input.text().strip()
            if not filepath:
                QMessageBox.warning(self, "ข้อผิดพลาด", "กรุณาเลือกไฟล์วิดีโอ")
                return

            config["type"] = "file"
            config["source"] = filepath

        # Get camera properties
        config["width"] = self.width_spinbox.value()
        config["height"] = self.height_spinbox.value()
        config["fps"] = self.fps_spinbox.value()

        # Emit signal
        self.camera_selected.emit(config)
        self.accept()
