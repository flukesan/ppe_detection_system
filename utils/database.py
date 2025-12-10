"""
Database utility for storing detection records.
"""

import sqlite3
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
import json


class Database:
    """
    SQLite database for storing PPE detection records.
    """

    def __init__(self, db_path: str = "data/database/ppe_detections.db"):
        """
        Initialize database.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path

        # Create directory if not exists
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)

        self.conn = None
        self.init_database()

    def init_database(self):
        """Initialize database schema."""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = self.conn.cursor()

        # Create tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS detections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                person_id INTEGER NOT NULL,
                is_violation BOOLEAN NOT NULL,
                detected_ppe TEXT,
                missing_ppe TEXT,
                confidence REAL,
                screenshot_path TEXT,
                video_path TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                total_persons INTEGER,
                compliant INTEGER,
                violations INTEGER,
                violation_rate REAL
            )
        """)

        self.conn.commit()

    def add_detection(
        self,
        person_id: int,
        is_violation: bool,
        detected_ppe: List[str],
        missing_ppe: List[str],
        confidence: float,
        screenshot_path: Optional[str] = None,
        video_path: Optional[str] = None,
    ) -> int:
        """
        Add a detection record.

        Args:
            person_id: Person ID
            is_violation: Whether this is a violation
            detected_ppe: List of detected PPE
            missing_ppe: List of missing PPE
            confidence: Detection confidence
            screenshot_path: Path to screenshot
            video_path: Path to video recording

        Returns:
            Record ID
        """
        cursor = self.conn.cursor()

        cursor.execute("""
            INSERT INTO detections (
                timestamp, person_id, is_violation, detected_ppe,
                missing_ppe, confidence, screenshot_path, video_path
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            person_id,
            is_violation,
            json.dumps(detected_ppe),
            json.dumps(missing_ppe),
            confidence,
            screenshot_path,
            video_path,
        ))

        self.conn.commit()
        return cursor.lastrowid

    def add_statistics(self, stats: Dict[str, Any]):
        """
        Add statistics record.

        Args:
            stats: Statistics dictionary
        """
        cursor = self.conn.cursor()

        cursor.execute("""
            INSERT INTO statistics (
                timestamp, total_persons, compliant, violations, violation_rate
            ) VALUES (?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            stats["total_persons"],
            stats["compliant"],
            stats["violations"],
            stats["violation_rate"],
        ))

        self.conn.commit()

    def get_violations(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get recent violations.

        Args:
            limit: Maximum number of records

        Returns:
            List of violation records
        """
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT * FROM detections
            WHERE is_violation = 1
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))

        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()

        return [dict(zip(columns, row)) for row in rows]

    def get_statistics_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """
        Get statistics history.

        Args:
            hours: Number of hours to retrieve

        Returns:
            List of statistics records
        """
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT * FROM statistics
            WHERE timestamp >= datetime('now', '-' || ? || ' hours')
            ORDER BY timestamp DESC
        """, (hours,))

        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()

        return [dict(zip(columns, row)) for row in rows]

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()

    def __del__(self):
        """Cleanup."""
        self.close()
