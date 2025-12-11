"""
Zone editor dialog for creating and managing detection zones.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QLineEdit, QMessageBox, QWidget, QGroupBox, QColorDialog
)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint
from PyQt6.QtGui import QImage, QPixmap, QPainter, QPen, QColor, QMouseEvent
import cv2
import numpy as np
from typing import List, Tuple, Optional
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.zone_manager import ZoneManager, Zone


class ZoneDrawWidget(QLabel):
    """
    Widget for drawing polygon zones on a video frame.
    """

    def __init__(self):
        """Initialize zone draw widget."""
        super().__init__()

        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("background-color: black; border: 2px solid #555;")
        self.setMinimumSize(800, 600)

        # Drawing state
        self.current_points: List[Tuple[int, int]] = []
        self.is_drawing = False
        self.current_color = (0, 255, 0)  # Default green

        # Frame and zones
        self.frame: Optional[np.ndarray] = None
        self.zone_manager: Optional[ZoneManager] = None
        self.scale_x = 1.0
        self.scale_y = 1.0

        # Mouse tracking
        self.setMouseTracking(True)
        self.mouse_pos: Optional[Tuple[int, int]] = None

    def set_frame(self, frame: np.ndarray):
        """
        Set the current frame to draw on.

        Args:
            frame: Frame to display
        """
        self.frame = frame.copy()
        self.update_display()

    def set_zone_manager(self, zone_manager: ZoneManager):
        """
        Set the zone manager.

        Args:
            zone_manager: Zone manager instance
        """
        self.zone_manager = zone_manager
        self.update_display()

    def update_display(self):
        """Update the display with current frame and zones."""
        if self.frame is None:
            return

        # Create display frame
        display_frame = self.frame.copy()

        # Draw existing zones
        if self.zone_manager:
            display_frame = self.zone_manager.draw_zones(display_frame, show_zones=True)

        # Draw current polygon being drawn
        if len(self.current_points) > 0:
            # Draw lines between points
            for i in range(len(self.current_points) - 1):
                cv2.line(
                    display_frame,
                    self.current_points[i],
                    self.current_points[i + 1],
                    self.current_color,
                    2,
                )

            # Draw line from last point to mouse position
            if self.mouse_pos and len(self.current_points) > 0:
                cv2.line(
                    display_frame,
                    self.current_points[-1],
                    self.mouse_pos,
                    self.current_color,
                    1,
                )

            # Draw points
            for point in self.current_points:
                cv2.circle(display_frame, point, 5, self.current_color, -1)
                cv2.circle(display_frame, point, 6, (255, 255, 255), 1)

        # Draw instructions
        if self.is_drawing:
            instructions = [
                "Left-click: Add point",
                "Right-click: Complete polygon",
                "ESC: Cancel",
            ]
            y_offset = 30

            # Draw background box for instructions
            max_text_width = 0
            for instruction in instructions:
                (text_w, text_h), _ = cv2.getTextSize(
                    instruction, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2
                )
                max_text_width = max(max_text_width, text_w)

            # Draw semi-transparent background
            overlay = display_frame.copy()
            cv2.rectangle(
                overlay,
                (5, 10),
                (max_text_width + 25, y_offset + len(instructions) * 25),
                (0, 0, 0),
                -1
            )
            cv2.addWeighted(overlay, 0.7, display_frame, 0.3, 0, display_frame)

            # Draw instruction text
            for instruction in instructions:
                cv2.putText(
                    display_frame,
                    instruction,
                    (10, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),  # Green text
                    2,
                )
                y_offset += 25

        # Convert to QPixmap and display
        rgb_frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)

        # Scale to fit widget
        scaled_pixmap = QPixmap.fromImage(qt_image).scaled(
            self.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        # Calculate scale factors for coordinate mapping
        if scaled_pixmap.width() > 0 and scaled_pixmap.height() > 0:
            self.scale_x = w / scaled_pixmap.width()
            self.scale_y = h / scaled_pixmap.height()

        self.setPixmap(scaled_pixmap)

    def start_drawing(self, color: Tuple[int, int, int] = (0, 255, 0)):
        """
        Start drawing a new zone.

        Args:
            color: Zone color in BGR
        """
        self.is_drawing = True
        self.current_points = []
        self.current_color = color
        self.update_display()

    def stop_drawing(self) -> Optional[List[Tuple[int, int]]]:
        """
        Stop drawing and return points.

        Returns:
            List of points if polygon is valid, None otherwise
        """
        self.is_drawing = False
        points = self.current_points.copy() if len(self.current_points) >= 3 else None
        self.current_points = []
        self.mouse_pos = None
        self.update_display()
        return points

    def cancel_drawing(self):
        """Cancel current drawing."""
        self.is_drawing = False
        self.current_points = []
        self.mouse_pos = None
        self.update_display()

    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press events."""
        if not self.is_drawing or self.frame is None:
            return

        # Get position relative to pixmap
        pixmap_pos = self._get_pixmap_position(event.pos())
        if pixmap_pos is None:
            return

        # Convert to frame coordinates
        frame_x = int(pixmap_pos.x() * self.scale_x)
        frame_y = int(pixmap_pos.y() * self.scale_y)
        point = (frame_x, frame_y)

        if event.button() == Qt.MouseButton.LeftButton:
            # Add point
            self.current_points.append(point)
            self.update_display()

        elif event.button() == Qt.MouseButton.RightButton:
            # Complete polygon
            if len(self.current_points) >= 3:
                # Signal that polygon is complete by stopping drawing mode
                # Don't call stop_drawing() here - let _check_drawing_completion() handle it
                self.is_drawing = False
                self.mouse_pos = None
                self.update_display()

    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move events."""
        if not self.is_drawing or self.frame is None:
            return

        # Get position relative to pixmap
        pixmap_pos = self._get_pixmap_position(event.pos())
        if pixmap_pos is None:
            self.mouse_pos = None
            return

        # Convert to frame coordinates
        frame_x = int(pixmap_pos.x() * self.scale_x)
        frame_y = int(pixmap_pos.y() * self.scale_y)
        self.mouse_pos = (frame_x, frame_y)

        self.update_display()

    def keyPressEvent(self, event):
        """Handle key press events."""
        if event.key() == Qt.Key.Key_Escape:
            if self.is_drawing:
                self.cancel_drawing()

    def _get_pixmap_position(self, widget_pos: QPoint) -> Optional[QPoint]:
        """
        Get position relative to pixmap.

        Args:
            widget_pos: Position in widget coordinates

        Returns:
            Position in pixmap coordinates, or None if outside pixmap
        """
        pixmap = self.pixmap()
        if pixmap is None:
            return None

        # Calculate pixmap position in widget
        pixmap_rect = pixmap.rect()
        widget_rect = self.rect()

        # Center the pixmap
        x_offset = (widget_rect.width() - pixmap_rect.width()) // 2
        y_offset = (widget_rect.height() - pixmap_rect.height()) // 2

        # Convert to pixmap coordinates
        pixmap_x = widget_pos.x() - x_offset
        pixmap_y = widget_pos.y() - y_offset

        # Check if inside pixmap
        if 0 <= pixmap_x < pixmap_rect.width() and 0 <= pixmap_y < pixmap_rect.height():
            return QPoint(pixmap_x, pixmap_y)

        return None


class ZoneEditorDialog(QDialog):
    """
    Dialog for editing detection zones.
    """

    zones_changed = pyqtSignal()

    def __init__(self, parent, zone_manager: ZoneManager, current_frame: Optional[np.ndarray] = None):
        """
        Initialize zone editor dialog.

        Args:
            parent: Parent widget
            zone_manager: Zone manager instance
            current_frame: Current video frame to display
        """
        super().__init__(parent)

        self.zone_manager = zone_manager
        self.current_frame = current_frame

        self.setWindowTitle("Detection Zone Editor")
        self.resize(1200, 800)

        self.setup_ui()
        self.update_zone_list()

    def setup_ui(self):
        """Setup the user interface."""
        layout = QHBoxLayout(self)

        # Left panel: Zone drawing
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        # Draw widget
        self.draw_widget = ZoneDrawWidget()
        self.draw_widget.set_zone_manager(self.zone_manager)
        if self.current_frame is not None:
            self.draw_widget.set_frame(self.current_frame)
        left_layout.addWidget(self.draw_widget)

        layout.addWidget(left_panel, stretch=3)

        # Right panel: Zone controls
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        # Zone list
        zones_group = QGroupBox("Detection Zones")
        zones_layout = QVBoxLayout(zones_group)

        self.zone_list = QListWidget()
        zones_layout.addWidget(self.zone_list)

        # Zone control buttons
        zone_buttons = QHBoxLayout()

        self.delete_zone_btn = QPushButton("🗑️ Delete")
        self.delete_zone_btn.clicked.connect(self.on_delete_zone)
        zone_buttons.addWidget(self.delete_zone_btn)

        self.clear_zones_btn = QPushButton("🧹 Clear All")
        self.clear_zones_btn.clicked.connect(self.on_clear_zones)
        zone_buttons.addWidget(self.clear_zones_btn)

        zones_layout.addLayout(zone_buttons)
        right_layout.addWidget(zones_group)

        # New zone controls
        new_zone_group = QGroupBox("New Zone")
        new_zone_layout = QVBoxLayout(new_zone_group)

        # Zone name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Name:"))
        self.zone_name_input = QLineEdit()
        self.zone_name_input.setPlaceholderText("Enter zone name...")
        name_layout.addWidget(self.zone_name_input)
        new_zone_layout.addLayout(name_layout)

        # Zone color
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("Color:"))
        self.color_button = QPushButton("🎨 Choose Color")
        self.color_button.clicked.connect(self.on_choose_color)
        self.current_zone_color = (0, 255, 0)  # Default green
        self._update_color_button()
        color_layout.addWidget(self.color_button)
        new_zone_layout.addLayout(color_layout)

        # Draw button
        self.draw_zone_btn = QPushButton("✏️ Draw New Zone")
        self.draw_zone_btn.clicked.connect(self.on_start_drawing)
        new_zone_layout.addWidget(self.draw_zone_btn)

        # Instructions
        instructions = QLabel(
            "<b>Instructions:</b><br>"
            "1. Enter zone name<br>"
            "2. Choose color (optional)<br>"
            "3. Click 'Draw New Zone'<br>"
            "4. Left-click to add points<br>"
            "5. Right-click to complete<br>"
            "6. ESC to cancel"
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("padding: 10px; background-color: #f0f0f0; border-radius: 5px;")
        new_zone_layout.addWidget(instructions)

        right_layout.addWidget(new_zone_group)

        # Bottom buttons
        button_layout = QHBoxLayout()

        save_btn = QPushButton("💾 Save")
        save_btn.clicked.connect(self.on_save)
        button_layout.addWidget(save_btn)

        cancel_btn = QPushButton("❌ Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        right_layout.addLayout(button_layout)
        right_layout.addStretch()

        layout.addWidget(right_panel, stretch=1)

    def update_zone_list(self):
        """Update the zone list."""
        self.zone_list.clear()
        for zone in self.zone_manager.zones:
            status = "✅" if zone.enabled else "❌"
            self.zone_list.addItem(f"{status} {zone.name}")

    def on_start_drawing(self):
        """Start drawing a new zone."""
        zone_name = self.zone_name_input.text().strip()
        if not zone_name:
            QMessageBox.warning(self, "No Name", "Please enter a zone name first.")
            return

        # Check if zone name already exists
        if self.zone_manager.get_zone(zone_name):
            QMessageBox.warning(self, "Duplicate Name", f"Zone '{zone_name}' already exists.")
            return

        # Start drawing
        self.draw_zone_btn.setEnabled(False)
        self.draw_zone_btn.setText("Drawing... (Right-click to finish)")
        self.draw_widget.start_drawing(self.current_zone_color)

        # Monitor drawing completion
        self._check_drawing_completion()

    def _check_drawing_completion(self):
        """Check if drawing is complete."""
        if not self.draw_widget.is_drawing:
            # Drawing stopped - get points without clearing them yet
            if len(self.draw_widget.current_points) >= 3:
                # Valid polygon
                zone_name = self.zone_name_input.text().strip()
                points = self.draw_widget.current_points.copy()

                # Add zone to manager
                self.zone_manager.add_zone(zone_name, points, self.current_zone_color)
                self.update_zone_list()
                self.zone_name_input.clear()
                self.zones_changed.emit()

                # Now clear the drawing
                self.draw_widget.current_points = []
                self.draw_widget.mouse_pos = None
                self.draw_widget.update_display()
            else:
                # Not enough points, just clear
                self.draw_widget.current_points = []
                self.draw_widget.mouse_pos = None
                self.draw_widget.update_display()

            # Re-enable button
            self.draw_zone_btn.setEnabled(True)
            self.draw_zone_btn.setText("✏️ Draw New Zone")
        else:
            # Still drawing, check again later
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(100, self._check_drawing_completion)

    def on_delete_zone(self):
        """Delete selected zone."""
        selected_items = self.zone_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a zone to delete.")
            return

        selected_text = selected_items[0].text()
        zone_name = selected_text.split(" ", 1)[1]  # Remove status emoji

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete zone '{zone_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.zone_manager.remove_zone(zone_name)
            self.update_zone_list()
            self.draw_widget.update_display()
            self.zones_changed.emit()

    def on_clear_zones(self):
        """Clear all zones."""
        if len(self.zone_manager.zones) == 0:
            return

        reply = QMessageBox.question(
            self,
            "Confirm Clear",
            "Are you sure you want to delete ALL zones?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.zone_manager.clear_zones()
            self.update_zone_list()
            self.draw_widget.update_display()
            self.zones_changed.emit()

    def on_choose_color(self):
        """Choose zone color."""
        # Convert BGR to RGB for QColor
        qcolor = QColor(
            self.current_zone_color[2],
            self.current_zone_color[1],
            self.current_zone_color[0],
        )

        color = QColorDialog.getColor(qcolor, self, "Choose Zone Color")
        if color.isValid():
            # Convert RGB to BGR
            self.current_zone_color = (color.blue(), color.green(), color.red())
            self._update_color_button()

    def _update_color_button(self):
        """Update color button style."""
        r, g, b = self.current_zone_color[2], self.current_zone_color[1], self.current_zone_color[0]
        self.color_button.setStyleSheet(
            f"background-color: rgb({r}, {g}, {b}); color: {'white' if (r + g + b) < 384 else 'black'};"
        )
        # Force immediate update
        self.color_button.update()
        self.color_button.repaint()

        # Process pending events to ensure immediate visual feedback
        from PyQt6.QtWidgets import QApplication
        QApplication.processEvents()

    def on_save(self):
        """Handle save button click."""
        from PyQt6.QtWidgets import QMessageBox

        # Check if there are any zones
        if len(self.zone_manager.zones) == 0:
            reply = QMessageBox.question(
                self,
                "No Zones Defined",
                "You haven't created any detection zones.\n\n"
                "Without zones, detection will work everywhere.\n\n"
                "Do you want to save anyway?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.No:
                return

        # Show confirmation
        zone_count = len(self.zone_manager.zones)
        QMessageBox.information(
            self,
            "Zones Saved",
            f"✅ Successfully saved {zone_count} detection zone{'s' if zone_count != 1 else ''}!\n\n"
            f"Zones will be applied to the detection system.",
            QMessageBox.StandardButton.Ok
        )

        # Accept the dialog
        self.accept()
