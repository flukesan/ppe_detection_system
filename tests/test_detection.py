"""
Unit tests for detection modules.
"""

import pytest
import numpy as np
from core.tracker import PersonTracker
from core.temporal_filter import TemporalFilter


class TestPersonTracker:
    """Tests for PersonTracker class."""

    def test_tracker_initialization(self):
        """Test tracker initialization."""
        tracker = PersonTracker(max_age=30, min_hits=3)
        assert tracker.max_age == 30
        assert tracker.min_hits == 3
        assert len(tracker.tracks) == 0

    def test_tracker_update_empty(self):
        """Test tracker with no detections."""
        tracker = PersonTracker()
        result = tracker.update([])
        assert len(result) == 0

    def test_tracker_single_detection(self):
        """Test tracker with single detection."""
        tracker = PersonTracker(min_hits=1)

        detection = {
            "bbox": [100, 100, 200, 200],
            "confidence": 0.9,
            "keypoints": None,
        }

        result = tracker.update([detection])
        assert len(result) == 1
        assert result[0]["person_id"] >= 0


class TestTemporalFilter:
    """Tests for TemporalFilter class."""

    def test_filter_initialization(self):
        """Test filter initialization."""
        filter = TemporalFilter(buffer_size=30, violation_threshold=0.7)
        assert filter.buffer_size == 30
        assert filter.violation_threshold == 0.7

    def test_filter_single_frame(self):
        """Test filter with single frame."""
        filter = TemporalFilter(buffer_size=10, violation_threshold=0.7)

        status = filter.update(
            person_id=1,
            is_compliant=False,
            detected_ppe=["vest"],
            missing_ppe=["helmet"],
        )

        assert "is_violation" in status
        assert "confidence" in status
        assert status["is_violation"] == False  # Not enough frames yet

    def test_filter_consistent_violation(self):
        """Test filter with consistent violations."""
        filter = TemporalFilter(buffer_size=10, violation_threshold=0.7)

        # Add 10 violation frames
        for i in range(10):
            status = filter.update(
                person_id=1,
                is_compliant=False,
                detected_ppe=[],
                missing_ppe=["helmet", "vest"],
            )

        # Should detect violation with 100% violation rate
        assert status["is_violation"] == True
        assert status["violation_ratio"] == 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
