"""
Person Tracking module using DeepSORT algorithm.
"""

import numpy as np
from typing import List, Dict, Any, Tuple
from filterpy.kalman import KalmanFilter
from scipy.optimize import linear_sum_assignment


class Track:
    """Represents a single tracked person."""

    _id_counter = 0

    def __init__(self, bbox: List[int], confidence: float):
        """
        Initialize a track.

        Args:
            bbox: Bounding box [x1, y1, x2, y2]
            confidence: Detection confidence
        """
        self.id = Track._id_counter
        Track._id_counter += 1

        self.bbox = bbox
        self.confidence = confidence
        self.age = 0
        self.hits = 1
        self.time_since_update = 0

        # Initialize Kalman Filter for bbox tracking
        self.kf = KalmanFilter(dim_x=7, dim_z=4)

        # State: [x, y, s, r, vx, vy, vs]
        # x, y: center coordinates
        # s: scale (area)
        # r: aspect ratio
        # vx, vy, vs: velocities

        self.kf.F = np.array([
            [1, 0, 0, 0, 1, 0, 0],
            [0, 1, 0, 0, 0, 1, 0],
            [0, 0, 1, 0, 0, 0, 1],
            [0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 1, 0, 0],
            [0, 0, 0, 0, 0, 1, 0],
            [0, 0, 0, 0, 0, 0, 1],
        ])

        self.kf.H = np.array([
            [1, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0],
        ])

        self.kf.R *= 10.0
        self.kf.P[4:, 4:] *= 1000.0
        self.kf.P *= 10.0
        self.kf.Q[-1, -1] *= 0.01
        self.kf.Q[4:, 4:] *= 0.01

        self.kf.x[:4] = self._bbox_to_z(bbox)

    def predict(self):
        """Predict next state using Kalman Filter."""
        if self.time_since_update > 0:
            self.hits = 0

        self.time_since_update += 1
        self.age += 1
        self.kf.predict()

        # Update bbox from prediction
        self.bbox = self._z_to_bbox(self.kf.x[:4])

    def update(self, bbox: List[int], confidence: float):
        """
        Update track with new detection.

        Args:
            bbox: New bounding box
            confidence: Detection confidence
        """
        self.time_since_update = 0
        self.hits += 1
        self.confidence = confidence

        z = self._bbox_to_z(bbox)
        self.kf.update(z)

        self.bbox = self._z_to_bbox(self.kf.x[:4])

    def _bbox_to_z(self, bbox: List[int]) -> np.ndarray:
        """
        Convert bbox [x1, y1, x2, y2] to z [cx, cy, s, r].

        Args:
            bbox: [x1, y1, x2, y2]

        Returns:
            z: [cx, cy, s, r]
        """
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        cx = bbox[0] + w / 2
        cy = bbox[1] + h / 2
        s = w * h
        r = w / max(h, 1e-6)
        return np.array([cx, cy, s, r]).reshape((4, 1))

    def _z_to_bbox(self, z: np.ndarray) -> List[int]:
        """
        Convert z [cx, cy, s, r] to bbox [x1, y1, x2, y2].

        Args:
            z: [cx, cy, s, r]

        Returns:
            bbox: [x1, y1, x2, y2]
        """
        cx, cy, s, r = z.flatten()
        w = np.sqrt(s * r)
        h = s / max(w, 1e-6)
        x1 = cx - w / 2
        y1 = cy - h / 2
        x2 = cx + w / 2
        y2 = cy + h / 2
        return [int(x1), int(y1), int(x2), int(y2)]


class PersonTracker:
    """
    Multi-person tracker using Kalman Filter and Hungarian algorithm.
    """

    def __init__(
        self,
        max_age: int = 30,
        min_hits: int = 3,
        iou_threshold: float = 0.3,
    ):
        """
        Initialize Person Tracker.

        Args:
            max_age: Maximum frames to keep track alive without detection
            min_hits: Minimum hits before track is confirmed
            iou_threshold: IoU threshold for matching
        """
        self.max_age = max_age
        self.min_hits = min_hits
        self.iou_threshold = iou_threshold
        self.tracks: List[Track] = []
        self.frame_count = 0

    def update(self, detections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Update tracks with new detections.

        Args:
            detections: List of detections from pose detector

        Returns:
            List of tracked persons with assigned IDs
        """
        self.frame_count += 1

        # Predict new locations of existing tracks
        for track in self.tracks:
            track.predict()

        # Match detections to tracks
        matched, unmatched_dets, unmatched_trks = self._associate_detections(detections)

        # Update matched tracks
        for det_idx, trk_idx in matched:
            self.tracks[trk_idx].update(
                detections[det_idx]["bbox"],
                detections[det_idx]["confidence"]
            )

        # Create new tracks for unmatched detections
        for det_idx in unmatched_dets:
            new_track = Track(
                detections[det_idx]["bbox"],
                detections[det_idx]["confidence"]
            )
            self.tracks.append(new_track)

        # Remove dead tracks
        self.tracks = [
            t for t in self.tracks
            if t.time_since_update <= self.max_age
        ]

        # Return tracked detections
        tracked_detections = []
        for i, det in enumerate(detections):
            # Find matching track
            track_id = -1
            for m_det, m_trk in matched:
                if m_det == i:
                    track_id = self.tracks[m_trk].id
                    break

            # Only return confirmed tracks
            if track_id != -1:
                track = self._get_track_by_id(track_id)
                if track and track.hits >= self.min_hits:
                    tracked_det = det.copy()
                    tracked_det["person_id"] = track_id
                    tracked_det["bbox"] = track.bbox
                    tracked_detections.append(tracked_det)

        return tracked_detections

    def _associate_detections(
        self,
        detections: List[Dict[str, Any]]
    ) -> Tuple[List[Tuple[int, int]], List[int], List[int]]:
        """
        Associate detections to tracks using Hungarian algorithm.

        Args:
            detections: List of detections

        Returns:
            matched: List of (detection_idx, track_idx) pairs
            unmatched_detections: List of detection indices
            unmatched_tracks: List of track indices
        """
        if len(self.tracks) == 0:
            return [], list(range(len(detections))), []

        # Compute IoU cost matrix
        iou_matrix = np.zeros((len(detections), len(self.tracks)))

        for d, det in enumerate(detections):
            for t, track in enumerate(self.tracks):
                iou_matrix[d, t] = self._iou(det["bbox"], track.bbox)

        # Convert IoU to cost (1 - IoU)
        cost_matrix = 1 - iou_matrix

        # Hungarian algorithm
        if cost_matrix.size > 0:
            row_ind, col_ind = linear_sum_assignment(cost_matrix)
            matched_indices = np.array(list(zip(row_ind, col_ind)))
        else:
            matched_indices = np.empty((0, 2), dtype=int)

        unmatched_detections = []
        for d in range(len(detections)):
            if d not in matched_indices[:, 0]:
                unmatched_detections.append(d)

        unmatched_tracks = []
        for t in range(len(self.tracks)):
            if t not in matched_indices[:, 1]:
                unmatched_tracks.append(t)

        # Filter matches with low IoU
        matches = []
        for m in matched_indices:
            if iou_matrix[m[0], m[1]] < self.iou_threshold:
                unmatched_detections.append(m[0])
                unmatched_tracks.append(m[1])
            else:
                matches.append((m[0], m[1]))

        return matches, unmatched_detections, unmatched_tracks

    def _iou(self, bbox1: List[int], bbox2: List[int]) -> float:
        """
        Calculate Intersection over Union (IoU) between two bboxes.

        Args:
            bbox1: [x1, y1, x2, y2]
            bbox2: [x1, y1, x2, y2]

        Returns:
            IoU value
        """
        x1 = max(bbox1[0], bbox2[0])
        y1 = max(bbox1[1], bbox2[1])
        x2 = min(bbox1[2], bbox2[2])
        y2 = min(bbox1[3], bbox2[3])

        intersection = max(0, x2 - x1) * max(0, y2 - y1)

        area1 = (bbox1[2] - bbox1[0]) * (bbox1[3] - bbox1[1])
        area2 = (bbox2[2] - bbox2[0]) * (bbox2[3] - bbox2[1])

        union = area1 + area2 - intersection

        return intersection / max(union, 1e-6)

    def _get_track_by_id(self, track_id: int) -> Track:
        """Get track by ID."""
        for track in self.tracks:
            if track.id == track_id:
                return track
        return None

    def reset(self):
        """Reset tracker state."""
        self.tracks = []
        self.frame_count = 0
        Track._id_counter = 0

    def get_active_tracks(self) -> List[Dict[str, Any]]:
        """
        Get all active tracks.

        Returns:
            List of track information
        """
        active_tracks = []
        for track in self.tracks:
            if track.hits >= self.min_hits and track.time_since_update <= 1:
                active_tracks.append({
                    "id": track.id,
                    "bbox": track.bbox,
                    "confidence": track.confidence,
                    "age": track.age,
                    "hits": track.hits,
                })
        return active_tracks
