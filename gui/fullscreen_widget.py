"""
Full screen widget for displaying camera feed in full screen mode.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap, QKeyEvent, QMouseEvent
import numpy as np


class FullScreenWidget(QWidget):
    """
    Full screen widget for displaying video feed.
    """

    # Signal emitted when user exits full screen
    exit_fullscreen = pyqtSignal()

    def __init__(self):
        """Initialize full screen widget."""
        super().__init__()

        self.setup_ui()
        self.setup_events()

    def setup_ui(self):
        """Setup the user interface."""
        # Set window flags for full screen
        self.setWindowFlags(
            Qt.WindowType.Window
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        # Black background
        self.setStyleSheet("background-color: black;")

        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Display label
        self.display_label = QLabel()
        self.display_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.display_label.setStyleSheet("background-color: black;")
        self.display_label.setScaledContents(False)

        layout.addWidget(self.display_label)

        # Instructions label (top-right corner)
        self.instructions_label = QLabel(
            "🖥️ Full Screen Mode | ESC, F11, or Double-click to exit"
        )
        self.instructions_label.setStyleSheet(
            """
            QLabel {
                color: white;
                background-color: rgba(0, 0, 0, 150);
                padding: 10px 15px;
                font-size: 12px;
                border-radius: 5px;
            }
            """
        )
        self.instructions_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        self.instructions_label.setParent(self)
        self.instructions_label.move(10, 10)
        self.instructions_label.adjustSize()

    def setup_events(self):
        """Setup event handlers."""
        # Track double-click
        self.last_click_time = 0
        self.double_click_threshold = 300  # milliseconds

    def keyPressEvent(self, event: QKeyEvent):
        """
        Handle key press events.

        Args:
            event: Key event
        """
        if event.key() in (Qt.Key.Key_Escape, Qt.Key.Key_F11, Qt.Key.Key_F):
            self.exit_fullscreen.emit()
            self.close()
        else:
            super().keyPressEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        """
        Handle mouse double-click events.

        Args:
            event: Mouse event
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.exit_fullscreen.emit()
            self.close()
        else:
            super().mouseDoubleClickEvent(event)

    def display_frame(self, frame: np.ndarray):
        """
        Display frame on the label.

        Args:
            frame: Frame to display (BGR format)
        """
        import cv2

        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w

        # Create QImage
        qt_image = QImage(
            rgb_frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888
        )

        # Scale to fit screen while maintaining aspect ratio
        screen_size = self.size()
        scaled_pixmap = QPixmap.fromImage(qt_image).scaled(
            screen_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        self.display_label.setPixmap(scaled_pixmap)

    def showEvent(self, event):
        """
        Handle show event.

        Args:
            event: Show event
        """
        super().showEvent(event)
        # Show in full screen
        self.showFullScreen()

    def resizeEvent(self, event):
        """
        Handle resize event to reposition instructions label.

        Args:
            event: Resize event
        """
        super().resizeEvent(event)
        # Keep instructions label in top-right corner
        self.instructions_label.move(
            self.width() - self.instructions_label.width() - 10, 10
        )
