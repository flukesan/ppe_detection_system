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
        # TODO: Implement configuration dialog
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(
            self,
            "Configuration",
            "PPE configuration dialog will be implemented here."
        )

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
