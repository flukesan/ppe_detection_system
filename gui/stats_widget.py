"""
Statistics display widget showing detection metrics and charts.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QGroupBox, QGridLayout, QPushButton
)
from PyQt6.QtCore import Qt
from typing import Dict, Any
from collections import deque
import pyqtgraph as pg


class StatsWidget(QWidget):
    """
    Widget for displaying detection statistics and charts.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize statistics widget.

        Args:
            config: Application configuration
        """
        super().__init__()

        self.config = config

        # Data buffers for charts
        self.history_size = 100
        self.person_count_history = deque(maxlen=self.history_size)
        self.violation_count_history = deque(maxlen=self.history_size)

        self.setup_ui()

    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)

        # Current statistics
        stats_group = QGroupBox("Current Statistics")
        stats_layout = QGridLayout()

        # Labels
        self.total_persons_label = QLabel("0")
        self.total_persons_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.total_persons_label.setStyleSheet("font-size: 24px; font-weight: bold;")

        self.compliant_label = QLabel("0")
        self.compliant_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.compliant_label.setStyleSheet("font-size: 24px; font-weight: bold; color: green;")

        self.violations_label = QLabel("0")
        self.violations_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.violations_label.setStyleSheet("font-size: 24px; font-weight: bold; color: red;")

        stats_layout.addWidget(QLabel("Total Persons:"), 0, 0)
        stats_layout.addWidget(self.total_persons_label, 0, 1)

        stats_layout.addWidget(QLabel("Compliant:"), 1, 0)
        stats_layout.addWidget(self.compliant_label, 1, 1)

        stats_layout.addWidget(QLabel("Violations:"), 2, 0)
        stats_layout.addWidget(self.violations_label, 2, 1)

        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)

        # Charts
        charts_group = QGroupBox("Detection History")
        charts_layout = QVBoxLayout()

        # Person count chart
        self.person_chart = pg.PlotWidget()
        self.person_chart.setBackground('w')
        self.person_chart.setTitle("Person Count Over Time", color='k')
        self.person_chart.setLabel('left', 'Count', color='k')
        self.person_chart.setLabel('bottom', 'Frame', color='k')
        self.person_chart.showGrid(x=True, y=True)
        self.person_curve = self.person_chart.plot(pen=pg.mkPen(color='b', width=2))
        charts_layout.addWidget(self.person_chart)

        # Violation count chart
        self.violation_chart = pg.PlotWidget()
        self.violation_chart.setBackground('w')
        self.violation_chart.setTitle("Violations Over Time", color='k')
        self.violation_chart.setLabel('left', 'Count', color='k')
        self.violation_chart.setLabel('bottom', 'Frame', color='k')
        self.violation_chart.showGrid(x=True, y=True)
        self.violation_curve = self.violation_chart.plot(pen=pg.mkPen(color='r', width=2))
        charts_layout.addWidget(self.violation_chart)

        charts_group.setLayout(charts_layout)
        layout.addWidget(charts_group)

        # Export button
        export_btn = QPushButton("📊 Export Statistics")
        export_btn.clicked.connect(self.on_export_clicked)
        layout.addWidget(export_btn)

    def update_statistics(self, stats: Dict[str, Any]):
        """
        Update statistics display.

        Args:
            stats: Statistics dictionary
        """
        # Update labels
        self.total_persons_label.setText(str(stats["total_persons"]))
        self.compliant_label.setText(str(stats["compliant"]))
        self.violations_label.setText(str(stats["violations"]))

        # Update history
        self.person_count_history.append(stats["total_persons"])
        self.violation_count_history.append(stats["violations"])

        # Update charts
        self.person_curve.setData(list(self.person_count_history))
        self.violation_curve.setData(list(self.violation_count_history))

    def on_export_clicked(self):
        """Handle export button click."""
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        import pandas as pd
        from datetime import datetime

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export Statistics",
            f"statistics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            "Excel Files (*.xlsx);;CSV Files (*.csv)"
        )

        if filename:
            try:
                # Create DataFrame
                df = pd.DataFrame({
                    'Frame': range(len(self.person_count_history)),
                    'Total Persons': list(self.person_count_history),
                    'Violations': list(self.violation_count_history),
                })

                # Export
                if filename.endswith('.csv'):
                    df.to_csv(filename, index=False)
                else:
                    df.to_excel(filename, index=False)

                QMessageBox.information(self, "Success", f"Statistics exported to {filename}")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export: {str(e)}")

    def reset_statistics(self):
        """Reset all statistics."""
        self.person_count_history.clear()
        self.violation_count_history.clear()
        self.person_curve.setData([])
        self.violation_curve.setData([])
        self.total_persons_label.setText("0")
        self.compliant_label.setText("0")
        self.violations_label.setText("0")
