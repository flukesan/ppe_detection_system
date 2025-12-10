"""
Main application window for PPE Detection System.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QStatusBar, QMenuBar, QMenu
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction
from typing import Dict, Any, Optional
import sys

from .camera_widget import CameraWidget
from .control_panel import ControlPanel
from .stats_widget import StatsWidget
from .alert_widget import AlertWidget
from .config_dialog import ConfigDialog


class MainWindow(QMainWindow):
    """
    Main application window containing all UI components.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize main window.

        Args:
            config: Application configuration
        """
        super().__init__()

        self.config = config
        self.setup_ui()
        self.setup_menu()
        self.setup_status_bar()
        self.apply_theme()

    def setup_ui(self):
        """Setup the user interface."""
        # Set window properties
        window_config = self.config["ui"]["window"]
        self.setWindowTitle(self.config["application"]["name"])
        self.resize(window_config["width"], window_config["height"])

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QHBoxLayout(central_widget)

        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left panel: Camera view and alerts
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)

        # Camera widget
        self.camera_widget = CameraWidget(self.config)
        left_layout.addWidget(self.camera_widget, stretch=3)

        # Alert widget
        self.alert_widget = AlertWidget(self.config)
        left_layout.addWidget(self.alert_widget, stretch=1)

        splitter.addWidget(left_panel)

        # Right panel: Controls and statistics
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)

        # Control panel
        self.control_panel = ControlPanel(self.config)
        right_layout.addWidget(self.control_panel, stretch=1)

        # Statistics widget
        self.stats_widget = StatsWidget(self.config)
        right_layout.addWidget(self.stats_widget, stretch=2)

        splitter.addWidget(right_panel)

        # Set splitter sizes (70% left, 30% right)
        splitter.setSizes([700, 300])

        main_layout.addWidget(splitter)

        # Connect signals
        self.connect_signals()

    def setup_menu(self):
        """Setup menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        open_video_action = QAction("&Open Video File", self)
        open_video_action.setShortcut("Ctrl+O")
        open_video_action.triggered.connect(self.on_open_video)
        file_menu.addAction(open_video_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # View menu
        view_menu = menubar.addMenu("&View")

        toggle_pose_action = QAction("Show &Pose Keypoints", self, checkable=True)
        toggle_pose_action.setChecked(self.config["ui"]["display"]["show_pose_keypoints"])
        toggle_pose_action.triggered.connect(self.on_toggle_pose_keypoints)
        view_menu.addAction(toggle_pose_action)

        toggle_fps_action = QAction("Show &FPS", self, checkable=True)
        toggle_fps_action.setChecked(self.config["ui"]["display"]["show_fps"])
        toggle_fps_action.triggered.connect(self.on_toggle_fps)
        view_menu.addAction(toggle_fps_action)

        # Camera menu
        camera_menu = menubar.addMenu("&Camera")

        connect_camera_action = QAction("📹 &Connect Camera", self)
        connect_camera_action.setShortcut("Ctrl+K")
        connect_camera_action.triggered.connect(self.on_connect_camera)
        camera_menu.addAction(connect_camera_action)

        camera_menu.addSeparator()

        disconnect_camera_action = QAction("⏹️ &Disconnect", self)
        disconnect_camera_action.triggered.connect(self.on_disconnect_camera)
        camera_menu.addAction(disconnect_camera_action)

        # Settings menu
        settings_menu = menubar.addMenu("&Settings")

        configure_action = QAction("&Configure PPE Requirements", self)
        configure_action.triggered.connect(self.on_configure_ppe)
        settings_menu.addAction(configure_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        about_action = QAction("&About", self)
        about_action.triggered.connect(self.on_about)
        help_menu.addAction(about_action)

    def setup_status_bar(self):
        """Setup status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def connect_signals(self):
        """Connect signals between components."""
        # Camera widget signals
        self.camera_widget.frame_processed.connect(self.on_frame_processed)
        self.camera_widget.status_changed.connect(self.on_status_changed)

        # Control panel signals
        self.control_panel.start_requested.connect(self.camera_widget.start_camera)
        self.control_panel.stop_requested.connect(self.camera_widget.stop_camera)
        self.control_panel.settings_changed.connect(self.on_settings_changed)

    def on_frame_processed(self, results: Dict[str, Any]):
        """
        Handle processed frame results.

        Args:
            results: Detection results from camera widget
        """
        # Update statistics
        self.stats_widget.update_statistics(results["statistics"])

        # Check for violations and show alerts
        if results["violations"]:
            for violation in results["violations"]:
                self.alert_widget.add_alert(
                    person_id=violation["person_id"],
                    missing_ppe=violation["filtered_status"]["missing_ppe"],
                )

    def on_status_changed(self, status: str):
        """
        Handle status changes.

        Args:
            status: Status message
        """
        self.status_bar.showMessage(status)

    def on_settings_changed(self, settings: Dict[str, Any]):
        """
        Handle settings changes from control panel.

        Args:
            settings: New settings
        """
        self.camera_widget.update_settings(settings)

    def on_open_video(self):
        """Handle opening video file."""
        from PyQt6.QtWidgets import QFileDialog

        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Open Video File",
            "",
            "Video Files (*.mp4 *.avi *.mov *.mkv);;All Files (*)"
        )

        if filename:
            self.camera_widget.open_video_file(filename)

    def on_connect_camera(self):
        """Open camera connection dialog."""
        from .camera_connection_dialog import CameraConnectionDialog

        # Get current camera config if exists
        current_config = getattr(self, 'camera_config', None)

        # Create and show dialog
        dialog = CameraConnectionDialog(self, current_config)
        dialog.camera_selected.connect(self.on_camera_selected)

        if dialog.exec():
            pass  # Connection handled by signal

    def on_camera_selected(self, config: Dict[str, Any]):
        """
        Handle camera source selection.

        Args:
            config: Camera configuration
        """
        # Save configuration
        self.camera_config = config

        # Stop current camera if running
        if self.camera_widget.is_running:
            self.camera_widget.stop_camera()

        # Start camera with new source
        source = config["source"]
        camera_conf = {
            "width": config["width"],
            "height": config["height"],
            "fps": config["fps"],
        }

        self.camera_widget.start_camera(source, camera_conf)

        # Update status
        source_type = config["type"].upper()
        self.status_bar.showMessage(f"เชื่อมต่อ {source_type} camera สำเร็จ")

    def on_disconnect_camera(self):
        """Disconnect current camera."""
        if self.camera_widget.is_running:
            self.camera_widget.stop_camera()
            self.status_bar.showMessage("ตัดการเชื่อมต่อกล้องแล้ว")
        else:
            self.status_bar.showMessage("ไม่มีกล้องที่เชื่อมต่ออยู่")

    def on_toggle_pose_keypoints(self, checked: bool):
        """Toggle pose keypoints display."""
        self.config["ui"]["display"]["show_pose_keypoints"] = checked
        self.camera_widget.update_display_settings(self.config["ui"]["display"])

    def on_toggle_fps(self, checked: bool):
        """Toggle FPS display."""
        self.config["ui"]["display"]["show_fps"] = checked
        self.camera_widget.update_display_settings(self.config["ui"]["display"])

    def on_configure_ppe(self):
        """Open PPE configuration dialog."""
        # Initialize config if not exists
        if "detection_config" not in self.config:
            self.config["detection_config"] = {
                "keypoints": {
                    "enabled_keypoints": list(range(17)),  # All keypoints
                    "show_all": True,
                },
                "ppe_classes": {
                    "enabled_classes": ["helmet", "vest", "gloves", "boots", "goggles", "mask"],
                    "required_classes": ["helmet", "vest"],
                },
            }

        # Create and show dialog
        dialog = ConfigDialog(self, self.config.get("detection_config", {}))
        dialog.config_applied.connect(self.on_detection_config_changed)

        if dialog.exec():
            # Configuration was accepted
            self.status_bar.showMessage("ตั้งค่าการตรวจจับเรียบร้อย")

    def on_detection_config_changed(self, config: Dict[str, Any]):
        """
        Handle detection configuration changes.

        Args:
            config: New configuration
        """
        # Update config
        self.config["detection_config"] = config

        # Apply to camera widget/detector
        if hasattr(self.camera_widget, 'detector') and self.camera_widget.detector:
            # Update keypoints filter
            enabled_keypoints = config["keypoints"]["enabled_keypoints"]
            self.camera_widget.detector.set_enabled_keypoints(enabled_keypoints)

            # Update PPE classes filter
            enabled_classes = config["ppe_classes"]["enabled_classes"]
            required_classes = config["ppe_classes"]["required_classes"]

            # Update PPE detector
            self.camera_widget.detector.set_enabled_ppe_classes(enabled_classes)
            self.camera_widget.detector.set_required_ppe(required_classes)

            print(f"✅ Updated detection config:")
            print(f"   Enabled keypoints: {len(enabled_keypoints)}/17")
            print(f"   Enabled PPE: {enabled_classes}")
            print(f"   Required PPE: {required_classes}")

    def on_about(self):
        """Show about dialog."""
        from PyQt6.QtWidgets import QMessageBox

        about_text = f"""
        <h2>{self.config['application']['name']}</h2>
        <p>Version {self.config['application']['version']}</p>
        <p>AI-powered Personal Protective Equipment Detection System</p>
        <p>Using YOLOv9-Pose and Deep Learning</p>
        """

        QMessageBox.about(self, "About", about_text)

    def apply_theme(self):
        """Apply UI theme."""
        theme = self.config["ui"]["theme"]

        if theme == "dark":
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QWidget {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QPushButton {
                    background-color: #3c3c3c;
                    color: #ffffff;
                    border: 1px solid #555555;
                    padding: 5px 15px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #4c4c4c;
                }
                QPushButton:pressed {
                    background-color: #5c5c5c;
                }
                QGroupBox {
                    border: 1px solid #555555;
                    border-radius: 5px;
                    margin-top: 10px;
                    padding-top: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    subcontrol-position: top left;
                    padding: 0 5px;
                }
            """)

    def closeEvent(self, event):
        """Handle window close event."""
        # Stop camera before closing
        self.camera_widget.stop_camera()
        event.accept()
