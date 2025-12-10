"""
Temporal Filtering module to reduce false positives over time.
"""

from collections import deque, defaultdict
from typing import Dict, Any, List, Optional
import numpy as np


class TemporalFilter:
    """
    Temporal filter to smooth detection results over time.
    Reduces false positives by requiring consistent violations.
    """

    def __init__(
        self,
        buffer_size: int = 30,
        violation_threshold: float = 0.7,
    ):
        """
        Initialize Temporal Filter.

        Args:
            buffer_size: Number of frames to keep in history
            violation_threshold: Ratio of frames with violation to trigger alert (0-1)
        """
        self.buffer_size = buffer_size
        self.violation_threshold = violation_threshold

        # Buffer for each tracked person: person_id -> deque of compliance status
        self.person_buffers: Dict[int, deque] = defaultdict(
            lambda: deque(maxlen=buffer_size)
        )

        # Current filtered status for each person
        self.person_status: Dict[int, Dict[str, Any]] = {}

    def update(
        self,
        person_id: int,
        is_compliant: bool,
        detected_ppe: List[str],
        missing_ppe: List[str],
    ) -> Dict[str, Any]:
        """
        Update filter with new detection result for a person.

        Args:
            person_id: Tracked person ID
            is_compliant: Whether person is compliant in this frame
            detected_ppe: List of detected PPE items
            missing_ppe: List of missing PPE items

        Returns:
            Filtered status containing:
                - is_violation: bool (filtered result)
                - confidence: float (confidence in the decision)
                - detected_ppe: List[str]
                - missing_ppe: List[str]
                - violation_ratio: float
        """
        # Add to buffer
        self.person_buffers[person_id].append({
            "compliant": is_compliant,
            "detected_ppe": detected_ppe,
            "missing_ppe": missing_ppe,
        })

        # Calculate violation statistics
        buffer = self.person_buffers[person_id]
        buffer_list = list(buffer)

        if len(buffer_list) == 0:
            return {
                "is_violation": False,
                "confidence": 0.0,
                "detected_ppe": [],
                "missing_ppe": [],
                "violation_ratio": 0.0,
            }

        # Count violations in buffer
        violation_count = sum(1 for item in buffer_list if not item["compliant"])
        violation_ratio = violation_count / len(buffer_list)

        # Determine if this is a confirmed violation
        is_violation = violation_ratio >= self.violation_threshold

        # Calculate confidence based on buffer fullness and consistency
        buffer_fullness = len(buffer_list) / self.buffer_size
        confidence = buffer_fullness * abs(violation_ratio - 0.5) * 2

        # Aggregate detected and missing PPE from recent frames
        recent_frames = buffer_list[-10:]  # Last 10 frames
        all_detected = []
        all_missing = []

        for frame in recent_frames:
            all_detected.extend(frame["detected_ppe"])
            all_missing.extend(frame["missing_ppe"])

        # Get most common items
        detected_ppe_filtered = self._most_common(all_detected)
        missing_ppe_filtered = self._most_common(all_missing)

        status = {
            "is_violation": is_violation,
            "confidence": float(confidence),
            "detected_ppe": detected_ppe_filtered,
            "missing_ppe": missing_ppe_filtered,
            "violation_ratio": float(violation_ratio),
        }

        self.person_status[person_id] = status

        return status

    def get_status(self, person_id: int) -> Optional[Dict[str, Any]]:
        """
        Get current filtered status for a person.

        Args:
            person_id: Tracked person ID

        Returns:
            Filtered status or None if person not tracked
        """
        return self.person_status.get(person_id)

    def remove_person(self, person_id: int):
        """
        Remove a person from tracking (e.g., when they leave the scene).

        Args:
            person_id: Tracked person ID
        """
        if person_id in self.person_buffers:
            del self.person_buffers[person_id]
        if person_id in self.person_status:
            del self.person_status[person_id]

    def cleanup_old_tracks(self, active_person_ids: List[int]):
        """
        Remove tracks that are no longer active.

        Args:
            active_person_ids: List of currently active person IDs
        """
        active_set = set(active_person_ids)

        # Remove inactive persons
        for person_id in list(self.person_buffers.keys()):
            if person_id not in active_set:
                self.remove_person(person_id)

    def reset(self):
        """Reset all tracking data."""
        self.person_buffers.clear()
        self.person_status.clear()

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get overall statistics.

        Returns:
            Dictionary with statistics
        """
        total_persons = len(self.person_status)
        violations = sum(1 for status in self.person_status.values() if status["is_violation"])
        compliant = total_persons - violations

        return {
            "total_tracked": total_persons,
            "violations": violations,
            "compliant": compliant,
            "violation_rate": violations / max(total_persons, 1),
        }

    def _most_common(self, items: List[str], top_n: int = 10) -> List[str]:
        """
        Get most common items from a list.

        Args:
            items: List of items
            top_n: Number of top items to return

        Returns:
            List of most common items
        """
        if not items:
            return []

        from collections import Counter
        counter = Counter(items)
        return [item for item, count in counter.most_common(top_n)]

    def get_person_history(self, person_id: int) -> List[Dict[str, Any]]:
        """
        Get detection history for a person.

        Args:
            person_id: Tracked person ID

        Returns:
            List of historical detections
        """
        if person_id not in self.person_buffers:
            return []

        return list(self.person_buffers[person_id])

    def set_violation_threshold(self, threshold: float):
        """
        Update violation threshold.

        Args:
            threshold: New threshold value (0-1)
        """
        if 0.0 <= threshold <= 1.0:
            self.violation_threshold = threshold
        else:
            raise ValueError("Threshold must be between 0 and 1")
