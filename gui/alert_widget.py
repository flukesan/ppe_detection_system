"""
Alert widget for displaying PPE violation notifications.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QListWidget, QListWidgetItem, QPushButton, QGroupBox
)
from PyQt6.QtCore import Qt, QTimer
from typing import Dict, Any, List
from datetime import datetime


class AlertWidget(QWidget):
    """
    Widget for displaying PPE violation alerts.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize alert widget.

        Args:
            config: Application configuration
        """
        super().__init__()

        self.config = config
        self.alert_queue = []
        self.max_alerts = config["notifications"]["max_queue_size"]

        self.setup_ui()

    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)

        # Alert group
        alert_group = QGroupBox("🚨 Recent Alerts")
        alert_layout = QVBoxLayout()

        # Alert list
        self.alert_list = QListWidget()
        self.alert_list.setMaximumHeight(200)
        alert_layout.addWidget(self.alert_list)

        # Clear button
        button_layout = QHBoxLayout()
        clear_btn = QPushButton("Clear All")
        clear_btn.clicked.connect(self.clear_alerts)
        button_layout.addWidget(clear_btn)

        export_btn = QPushButton("Export Log")
        export_btn.clicked.connect(self.export_alerts)
        button_layout.addWidget(export_btn)

        alert_layout.addLayout(button_layout)

        alert_group.setLayout(alert_layout)
        layout.addWidget(alert_group)

    def add_alert(self, person_id: int, missing_ppe: List[str]):
        """
        Add a new alert.

        Args:
            person_id: ID of the person with violation
            missing_ppe: List of missing PPE items
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        missing_items = ", ".join(missing_ppe)

        alert_text = f"[{timestamp}] Person {person_id}: Missing {missing_items}"

        # Add to list
        item = QListWidgetItem(alert_text)
        item.setForeground(Qt.GlobalColor.red)
        self.alert_list.insertItem(0, item)

        # Store in queue
        self.alert_queue.append({
            "timestamp": timestamp,
            "person_id": person_id,
            "missing_ppe": missing_ppe,
        })

        # Limit queue size
        if self.alert_list.count() > self.max_alerts:
            self.alert_list.takeItem(self.alert_list.count() - 1)

        if len(self.alert_queue) > self.max_alerts:
            self.alert_queue.pop(0)

        # Play sound if enabled
        if self.config["alerts"]["sound"]:
            self.play_alert_sound()

    def play_alert_sound(self):
        """Play alert sound."""
        # TODO: Implement sound playback
        # For now, just use system beep
        try:
            import sys
            if sys.platform == "win32":
                import winsound
                winsound.Beep(1000, 200)
        except:
            pass

    def clear_alerts(self):
        """Clear all alerts."""
        self.alert_list.clear()
        self.alert_queue.clear()

    def export_alerts(self):
        """Export alerts to file."""
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        from datetime import datetime

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export Alerts",
            f"alerts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "Text Files (*.txt);;All Files (*)"
        )

        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write("PPE Violation Alerts\n")
                    f.write("=" * 50 + "\n\n")

                    for alert in reversed(self.alert_queue):
                        f.write(f"[{alert['timestamp']}] Person {alert['person_id']}\n")
                        f.write(f"  Missing PPE: {', '.join(alert['missing_ppe'])}\n\n")

                QMessageBox.information(self, "Success", f"Alerts exported to {filename}")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export: {str(e)}")

    def get_alert_count(self) -> int:
        """Get current number of alerts."""
        return len(self.alert_queue)
