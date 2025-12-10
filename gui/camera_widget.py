"""
Camera display widget with real-time detection visualization.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap
import cv2
import numpy as np
from typing import Dict, Any, Optional
import time


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
        self.video_file = None

        # Performance tracking
        self.frame_times = []
        self.fps = 0.0

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

    def start_camera(self, camera_id: int = 0):
        """
        Start camera capture.

        Args:
            camera_id: Camera device ID
        """
        if self.is_running:
            return

        try:
            self.camera = cv2.VideoCapture(camera_id)

            if not self.camera.isOpened():
                self.status_changed.emit(f"❌ Failed to open camera {camera_id}")
                return

            # Set camera properties
            cam_config = self.config["camera"]
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, cam_config["width"])
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, cam_config["height"])
            self.camera.set(cv2.CAP_PROP_FPS, cam_config["fps"])

            self.is_running = True
            self.timer.start(30)  # 30ms = ~33 FPS
            self.status_changed.emit(f"✅ Camera {camera_id} started")

        except Exception as e:
            self.status_changed.emit(f"❌ Error: {str(e)}")

    def stop_camera(self):
        """Stop camera capture."""
        self.is_running = False
        self.timer.stop()

        if self.camera is not None:
            self.camera.release()
            self.camera = None

        self.display_label.clear()
        self.status_changed.emit("Camera stopped")

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

        # Read frame
        ret, frame = self.camera.read()

        if not ret:
            # End of video or camera error
            if self.video_file:
                self.stop_camera()
                self.status_changed.emit("Video finished")
            return

        # Process detection if detector is available
        if self.detector is not None:
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
            annotated_frame = frame

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
