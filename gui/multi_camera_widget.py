"""
Multi-camera display widget with fusion detection visualization.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap
import cv2
import numpy as np
from typing import Dict, Any, Optional, List
import time
import os


class MultiCameraWidget(QWidget):
    """
    Widget for displaying multiple camera feeds with fusion detection.
    """

    # Signals
    frame_processed = pyqtSignal(dict)  # Emits detection results
    status_changed = pyqtSignal(str)  # Emits status messages

    def __init__(self, config: Dict[str, Any], num_cameras: int = 2):
        """
        Initialize multi-camera widget.

        Args:
            config: Application configuration
            num_cameras: Number of cameras (default: 2)
        """
        super().__init__()

        self.config = config
        self.num_cameras = num_cameras
        self.cameras = [None] * num_cameras
        self.camera_sources = [None] * num_cameras
        self.fusion_detector = None
        self.is_running = False
        self.detection_enabled = False

        # Performance tracking
        self.frame_times = []
        self.fps = 0.0

        self.setup_ui()

    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Display mode: side-by-side or fused
        self.display_mode = "fused"  # "fused" or "side_by_side"

        # Camera display label
        self.display_label = QLabel()
        self.display_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.display_label.setStyleSheet("background-color: black; border: 1px solid #555;")
        self.display_label.setMinimumSize(1280, 480)  # Wider for dual cameras
        self.display_label.setScaledContents(False)

        layout.addWidget(self.display_label)

        # Status labels for each camera
        status_layout = QHBoxLayout()
        self.camera_status_labels = []

        for i in range(self.num_cameras):
            label = QLabel(f"📹 Camera {i+1}: Disconnected")
            label.setStyleSheet("color: #888; font-size: 10px;")
            status_layout.addWidget(label)
            self.camera_status_labels.append(label)

        layout.addLayout(status_layout)

        # Timer for frame updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

    def set_detector(self, detector):
        """
        Set the fusion detection system.

        Args:
            detector: FusionDetector instance
        """
        self.fusion_detector = detector

    def start_cameras(
        self,
        camera_sources: List[Any],
        camera_configs: Optional[List[Dict[str, Any]]] = None,
    ):
        """
        Start multiple cameras.

        Args:
            camera_sources: List of camera sources (int, str RTSP, or file paths)
            camera_configs: List of camera configurations
        """
        if len(camera_sources) != self.num_cameras:
            self.status_changed.emit(
                f"❌ Expected {self.num_cameras} cameras, got {len(camera_sources)}"
            )
            return

        if self.is_running:
            self.stop_cameras()

        # Start each camera
        all_started = True
        for i, source in enumerate(camera_sources):
            config = (
                camera_configs[i]
                if camera_configs and i < len(camera_configs)
                else self.config.get("camera", {})
            )

            success = self._start_single_camera(i, source, config)
            if not success:
                all_started = False
                self.camera_status_labels[i].setText(f"📹 Camera {i+1}: ❌ Failed")
                self.camera_status_labels[i].setStyleSheet("color: #dc3545; font-size: 10px;")
            else:
                self.camera_status_labels[i].setText(f"📹 Camera {i+1}: ✅ Connected")
                self.camera_status_labels[i].setStyleSheet("color: #28a745; font-size: 10px;")

        if all_started:
            self.is_running = True
            self.detection_enabled = False
            self.timer.start(30)  # 30ms = ~33 FPS
            self.status_changed.emit(
                f"✅ {self.num_cameras} cameras connected (Detection: OFF)"
            )
        else:
            self.status_changed.emit("⚠️ Some cameras failed to connect")

    def _start_single_camera(
        self, camera_idx: int, source: Any, config: Dict[str, Any]
    ) -> bool:
        """
        Start a single camera.

        Args:
            camera_idx: Camera index
            source: Camera source
            config: Camera configuration

        Returns:
            True if successful
        """
        try:
            # Determine source type
            is_rtsp = isinstance(source, str) and source.startswith("rtsp://")

            camera = cv2.VideoCapture(source)

            if not camera.isOpened():
                return False

            # Set camera properties
            if is_rtsp:
                # RTSP optimization for network streams
                camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Minimal buffer
                camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'H264'))
                # Error tolerance for H.264 decoding issues
                camera.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 5000)  # 5 sec timeout
                camera.set(cv2.CAP_PROP_READ_TIMEOUT_MSEC, 5000)  # 5 sec read timeout
                # Use TCP instead of UDP for more reliable streaming
                os.environ.setdefault('OPENCV_FFMPEG_CAPTURE_OPTIONS', 'rtsp_transport;tcp')

            if isinstance(source, int) or is_rtsp:
                camera.set(cv2.CAP_PROP_FRAME_WIDTH, config.get("width", 1280))
                camera.set(cv2.CAP_PROP_FRAME_HEIGHT, config.get("height", 720))
                camera.set(cv2.CAP_PROP_FPS, config.get("fps", 30))

            self.cameras[camera_idx] = camera
            self.camera_sources[camera_idx] = source

            return True

        except Exception as e:
            print(f"Error starting camera {camera_idx}: {e}")
            return False

    def stop_cameras(self):
        """Stop all cameras."""
        self.is_running = False
        self.detection_enabled = False
        self.timer.stop()

        for i, camera in enumerate(self.cameras):
            if camera is not None:
                camera.release()
                self.cameras[i] = None

            self.camera_status_labels[i].setText(f"📹 Camera {i+1}: Disconnected")
            self.camera_status_labels[i].setStyleSheet("color: #888; font-size: 10px;")

        self.display_label.clear()
        self.status_changed.emit("All cameras stopped")

    def start_detection(self):
        """Start fusion detection processing."""
        if not self.is_running:
            self.status_changed.emit("⚠️ Please connect cameras first")
            return

        if self.fusion_detector is None:
            self.status_changed.emit("⚠️ Fusion detector not initialized")
            return

        self.detection_enabled = True
        self.status_changed.emit("✅ Multi-camera fusion detection started")

    def stop_detection(self):
        """Stop detection processing."""
        self.detection_enabled = False
        self.status_changed.emit("⏹️ Detection stopped (cameras still running)")

    def is_detection_running(self) -> bool:
        """Check if detection is running."""
        return self.detection_enabled

    def update_frame(self):
        """Update frames from all cameras and process fusion detection."""
        if not self.is_running:
            return

        start_time = time.time()

        # Read frames from all cameras with error handling
        frames = []
        valid_cameras = []

        for i, camera in enumerate(self.cameras):
            if camera is not None and camera.isOpened():
                try:
                    ret, frame = camera.read()
                    if ret and frame is not None:
                        frames.append(frame)
                        valid_cameras.append(i)
                    else:
                        # Frame read failed, append None and continue
                        frames.append(None)
                except Exception as e:
                    # Handle H.264 decoding errors gracefully
                    # print(f"Warning: Camera {i} frame read error: {e}")
                    frames.append(None)
            else:
                frames.append(None)

        # Check if we have enough valid frames
        if len(valid_cameras) < 1:
            return

        # Process fusion detection if enabled
        if self.detection_enabled and self.fusion_detector is not None:
            try:
                results = self.fusion_detector.process_frames(frames)
                annotated_frame = results.get("annotated_frame")

                if annotated_frame is not None:
                    # Draw FPS
                    if self.config["ui"]["display"].get("show_fps", True):
                        cv2.putText(
                            annotated_frame,
                            f"FPS: {self.fps:.1f}",
                            (10, annotated_frame.shape[0] - 20),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.7,
                            (0, 255, 0),
                            2,
                        )

                    # Draw fusion info
                    fusion_mode = results.get("fusion_mode", "unknown")
                    num_matches = results.get("num_matches", 0)

                    info_text = f"Mode: {fusion_mode.upper()} | Matched: {num_matches}"
                    cv2.putText(
                        annotated_frame,
                        info_text,
                        (10, annotated_frame.shape[0] - 50),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (255, 255, 0),
                        2,
                    )

                # Emit results
                self.frame_processed.emit(results)

            except Exception as e:
                # Fallback: show frames side by side
                annotated_frame = self._create_side_by_side_display(frames)
                self.status_changed.emit(f"Detection error: {str(e)}")
        else:
            # Just display frames without detection
            annotated_frame = self._create_side_by_side_display(frames)

            # Draw status
            if annotated_frame is not None:
                status_text = "Detection: OFF"
                cv2.putText(
                    annotated_frame,
                    status_text,
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 0, 255),
                    2,
                )

        # Display frame
        if annotated_frame is not None:
            self.display_frame(annotated_frame)

        # Update FPS
        frame_time = time.time() - start_time
        self.frame_times.append(frame_time)
        if len(self.frame_times) > 30:
            self.frame_times.pop(0)
        if self.frame_times:
            self.fps = len(self.frame_times) / sum(self.frame_times)

    def _create_side_by_side_display(
        self, frames: List[Optional[np.ndarray]]
    ) -> Optional[np.ndarray]:
        """
        Create side-by-side display of frames.

        Args:
            frames: List of frames

        Returns:
            Combined frame
        """
        valid_frames = [f for f in frames if f is not None]

        if not valid_frames:
            return None

        if len(valid_frames) == 1:
            return valid_frames[0]

        # Resize to same height
        heights = [f.shape[0] for f in valid_frames]
        target_height = min(heights)

        resized_frames = []
        for frame in valid_frames:
            h, w = frame.shape[:2]
            new_w = int(w * target_height / h)
            resized = cv2.resize(frame, (new_w, target_height))
            resized_frames.append(resized)

        # Concatenate horizontally
        combined = np.hstack(resized_frames)

        # Add labels
        for i, _ in enumerate(valid_frames):
            x_offset = sum(f.shape[1] for f in resized_frames[:i]) + 10
            cv2.putText(
                combined,
                f"Camera {i+1}",
                (x_offset, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (0, 255, 255),
                2,
            )

        return combined

    def display_frame(self, frame: np.ndarray):
        """
        Display frame in widget.

        Args:
            frame: Frame to display (BGR)
        """
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Convert to QImage
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        qt_image = QImage(
            rgb_frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888
        )

        # Scale to fit widget while maintaining aspect ratio
        scaled_pixmap = QPixmap.fromImage(qt_image).scaled(
            self.display_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        self.display_label.setPixmap(scaled_pixmap)

    def update_settings(self, settings: Dict[str, Any]):
        """
        Update detection settings.

        Args:
            settings: New settings
        """
        # Update config
        self.config.update(settings)

    def update_display_settings(self, display_settings: Dict[str, Any]):
        """
        Update display settings.

        Args:
            display_settings: Display settings
        """
        self.config["ui"]["display"] = display_settings
