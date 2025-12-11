"""
Camera display widget with real-time detection visualization.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap, QMouseEvent
import cv2
import numpy as np
from typing import Dict, Any, Optional
import time

from .fullscreen_widget import FullScreenWidget


class CameraWidget(QWidget):
    """
    Widget for displaying camera feed with detection results.
    """

    # Signals
    frame_processed = pyqtSignal(dict)  # Emits detection results
    status_changed = pyqtSignal(str)  # Emits status messages

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize camera widget.

        Args:
            config: Application configuration
        """
        super().__init__()

        self.config = config
        self.camera = None
        self.detector = None
        self.is_running = False
        self.detection_enabled = False  # Separate flag for detection
        self.video_file = None
        self.is_rtsp = False  # Track if current source is RTSP

        # Performance tracking
        self.frame_times = []
        self.fps = 0.0

        # Full screen support
        self.fullscreen_widget = None
        self.current_frame = None  # Store current frame for full screen display

        self.setup_ui()

    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Camera display label
        self.display_label = QLabel()
        self.display_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.display_label.setStyleSheet("background-color: black; border: 1px solid #555;")
        self.display_label.setMinimumSize(640, 480)
        self.display_label.setScaledContents(False)

        layout.addWidget(self.display_label)

        # Timer for frame updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

    def set_detector(self, detector):
        """
        Set the detection system.

        Args:
            detector: PoseBasedDetector instance
        """
        self.detector = detector

    def start_camera(self, camera_source=0, camera_config: Optional[Dict[str, Any]] = None):
        """
        Start camera capture from USB, RTSP, or file.

        Args:
            camera_source: Camera device ID (int) or RTSP URL (str) or file path (str)
            camera_config: Camera configuration (width, height, fps)
        """
        if self.is_running:
            return

        try:
            # Determine source type
            if isinstance(camera_source, int):
                source_type = "USB"
                source_desc = f"Camera {camera_source}"
                self.is_rtsp = False
            elif camera_source.startswith("rtsp://"):
                source_type = "RTSP"
                source_desc = "RTSP Camera"
                self.is_rtsp = True
            else:
                source_type = "File"
                source_desc = camera_source
                self.is_rtsp = False

            self.camera = cv2.VideoCapture(camera_source)

            if not self.camera.isOpened():
                self.status_changed.emit(f"❌ Failed to open {source_type}: {source_desc}")
                return

            # Set camera properties (if applicable)
            cam_conf = camera_config or self.config["camera"]

            # For RTSP, reduce buffer size to minimize latency
            if self.is_rtsp:
                self.camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Minimal buffer
                # Try to enable low latency mode
                self.camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'H264'))

            # For USB and some RTSP cameras, we can set properties
            if isinstance(camera_source, int) or source_type == "RTSP":
                self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, cam_conf["width"])
                self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, cam_conf["height"])
                self.camera.set(cv2.CAP_PROP_FPS, cam_conf["fps"])

            self.is_running = True
            # Detection is NOT enabled by default - user must start it manually
            self.detection_enabled = False
            self.timer.start(30)  # 30ms = ~33 FPS
            self.status_changed.emit(
                f"✅ {source_type} connected: {source_desc} "
                f"(Detection: {'ON' if self.detection_enabled else 'OFF'})"
            )

        except Exception as e:
            self.status_changed.emit(f"❌ Error: {str(e)}")

    def stop_camera(self):
        """Stop camera capture."""
        self.is_running = False
        self.detection_enabled = False
        self.timer.stop()

        if self.camera is not None:
            self.camera.release()
            self.camera = None

        self.display_label.clear()
        self.status_changed.emit("Camera stopped")

    def start_detection(self):
        """Start detection processing."""
        if not self.is_running:
            self.status_changed.emit("⚠️ Please connect camera first")
            return

        if self.detector is None:
            self.status_changed.emit("⚠️ Detector not initialized")
            return

        self.detection_enabled = True
        self.status_changed.emit("✅ Detection started")

    def stop_detection(self):
        """Stop detection processing (camera keeps running)."""
        self.detection_enabled = False
        self.status_changed.emit("⏹️ Detection stopped (camera still running)")

    def is_detection_running(self) -> bool:
        """Check if detection is currently running."""
        return self.detection_enabled

    def open_video_file(self, filename: str):
        """
        Open video file for processing.

        Args:
            filename: Path to video file
        """
        if self.is_running:
            self.stop_camera()

        try:
            self.camera = cv2.VideoCapture(filename)
            self.video_file = filename

            if not self.camera.isOpened():
                self.status_changed.emit(f"❌ Failed to open video: {filename}")
                return

            self.is_running = True
            self.timer.start(30)
            self.status_changed.emit(f"✅ Video opened: {filename}")

        except Exception as e:
            self.status_changed.emit(f"❌ Error: {str(e)}")

    def update_frame(self):
        """Update frame from camera and process detection."""
        if not self.is_running or self.camera is None:
            return

        start_time = time.time()

        # For RTSP streams, skip buffered frames to get the latest frame
        if self.is_rtsp:
            # Grab and decode only the latest frame (skip buffered frames)
            for _ in range(2):  # Skip 1-2 buffered frames
                self.camera.grab()
            ret, frame = self.camera.retrieve()
        else:
            # For USB/File, read normally
            ret, frame = self.camera.read()

        if not ret:
            # End of video or camera error
            if self.video_file:
                self.stop_camera()
                self.status_changed.emit("Video finished")
            return

        # Process detection ONLY if enabled
        if self.detection_enabled and self.detector is not None:
            try:
                results = self.detector.process_frame(frame)
                annotated_frame = results["annotated_frame"]

                # Draw FPS
                if self.config["ui"]["display"]["show_fps"]:
                    cv2.putText(
                        annotated_frame,
                        f"FPS: {self.fps:.1f}",
                        (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 255, 0),
                        2,
                    )

                # Emit results
                self.frame_processed.emit(results)

            except Exception as e:
                annotated_frame = frame
                self.status_changed.emit(f"Detection error: {str(e)}")
        else:
            # Just display the raw frame without detection
            annotated_frame = frame.copy()

            # Draw status indicator
            status_text = "Detection: OFF" if not self.detection_enabled else "Detection: No Detector"
            cv2.putText(
                annotated_frame,
                status_text,
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 165, 255),  # Orange color
                2,
            )

            # Draw FPS even without detection
            if self.config["ui"]["display"]["show_fps"]:
                cv2.putText(
                    annotated_frame,
                    f"FPS: {self.fps:.1f}",
                    (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2,
                )

        # Display frame
        self.display_frame(annotated_frame)

        # Calculate FPS
        elapsed = time.time() - start_time
        self.frame_times.append(elapsed)
        if len(self.frame_times) > 30:
            self.frame_times.pop(0)
        self.fps = 1.0 / (sum(self.frame_times) / len(self.frame_times))

    def display_frame(self, frame: np.ndarray):
        """
        Display frame on the label.

        Args:
            frame: Frame to display (BGR format)
        """
        # Store current frame for full screen mode
        self.current_frame = frame.copy()

        # Update full screen display if active
        if self.fullscreen_widget and self.fullscreen_widget.isVisible():
            self.fullscreen_widget.display_frame(frame)
            return

        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w

        # Create QImage
        q_image = QImage(
            rgb_frame.data,
            w,
            h,
            bytes_per_line,
            QImage.Format.Format_RGB888
        )

        # Scale to fit label
        pixmap = QPixmap.fromImage(q_image)
        scaled_pixmap = pixmap.scaled(
            self.display_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        self.display_label.setPixmap(scaled_pixmap)

    def update_settings(self, settings: Dict[str, Any]):
        """
        Update detection settings.

        Args:
            settings: New settings
        """
        if self.detector is not None:
            self.detector.update_config(settings)

    def update_display_settings(self, display_settings: Dict[str, Any]):
        """
        Update display settings.

        Args:
            display_settings: New display settings
        """
        self.config["ui"]["display"].update(display_settings)

    def toggle_fullscreen(self):
        """Toggle full screen mode for video display."""
        if self.fullscreen_widget and self.fullscreen_widget.isVisible():
            # Exit full screen
            self.fullscreen_widget.close()
            self.fullscreen_widget = None
        else:
            # Enter full screen
            if self.current_frame is not None:
                self.fullscreen_widget = FullScreenWidget()
                self.fullscreen_widget.exit_fullscreen.connect(self.on_exit_fullscreen)
                self.fullscreen_widget.display_frame(self.current_frame)
                self.fullscreen_widget.show()

    def on_exit_fullscreen(self):
        """Handle exit from full screen mode."""
        if self.fullscreen_widget:
            self.fullscreen_widget.close()
            self.fullscreen_widget = None

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        """
        Handle mouse double-click to toggle full screen.

        Args:
            event: Mouse event
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.toggle_fullscreen()
        else:
            super().mouseDoubleClickEvent(event)
