"""
Person matcher for matching persons across multiple camera views.
"""

import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from scipy.optimize import linear_sum_assignment
import cv2


class PersonMatcher:
    """
    Matches persons detected in different camera views using spatial and appearance features.
    """

    def __init__(
        self,
        spatial_weight: float = 0.6,
        appearance_weight: float = 0.4,
        max_distance_threshold: float = 0.5,
    ):
        """
        Initialize person matcher.

        Args:
            spatial_weight: Weight for spatial distance (0-1)
            appearance_weight: Weight for appearance similarity (0-1)
            max_distance_threshold: Maximum distance threshold for matching (0-1)
        """
        self.spatial_weight = spatial_weight
        self.appearance_weight = appearance_weight
        self.max_distance_threshold = max_distance_threshold

    def match_persons(
        self,
        persons_cam1: List[Dict[str, Any]],
        persons_cam2: List[Dict[str, Any]],
        frame_cam1: Optional[np.ndarray] = None,
        frame_cam2: Optional[np.ndarray] = None,
    ) -> List[Tuple[int, int, float]]:
        """
        Match persons from two camera views.

        Args:
            persons_cam1: List of detected persons from camera 1
            persons_cam2: List of detected persons from camera 2
            frame_cam1: Frame from camera 1 (optional, for appearance matching)
            frame_cam2: Frame from camera 2 (optional, for appearance matching)

        Returns:
            List of tuples (cam1_idx, cam2_idx, confidence)
        """
        if not persons_cam1 or not persons_cam2:
            return []

        # Compute cost matrix
        cost_matrix = self._compute_cost_matrix(
            persons_cam1, persons_cam2, frame_cam1, frame_cam2
        )

        # Use Hungarian algorithm for optimal matching
        row_indices, col_indices = linear_sum_assignment(cost_matrix)

        # Filter matches by threshold
        matches = []
        for i, j in zip(row_indices, col_indices):
            cost = cost_matrix[i, j]
            # Convert cost to confidence (1 - cost)
            confidence = 1.0 - cost

            if confidence >= (1.0 - self.max_distance_threshold):
                matches.append((i, j, confidence))

        return matches

    def _compute_cost_matrix(
        self,
        persons_cam1: List[Dict[str, Any]],
        persons_cam2: List[Dict[str, Any]],
        frame_cam1: Optional[np.ndarray] = None,
        frame_cam2: Optional[np.ndarray] = None,
    ) -> np.ndarray:
        """
        Compute cost matrix for person matching.

        Args:
            persons_cam1: Persons from camera 1
            persons_cam2: Persons from camera 2
            frame_cam1: Frame from camera 1
            frame_cam2: Frame from camera 2

        Returns:
            Cost matrix (n_cam1 x n_cam2)
        """
        n_cam1 = len(persons_cam1)
        n_cam2 = len(persons_cam2)
        cost_matrix = np.zeros((n_cam1, n_cam2))

        for i, p1 in enumerate(persons_cam1):
            for j, p2 in enumerate(persons_cam2):
                # Spatial distance
                spatial_cost = self._compute_spatial_distance(p1, p2)

                # Appearance similarity (if frames provided)
                appearance_cost = 0.0
                if frame_cam1 is not None and frame_cam2 is not None:
                    appearance_cost = self._compute_appearance_distance(
                        p1, p2, frame_cam1, frame_cam2
                    )

                # Combined cost
                if frame_cam1 is not None and frame_cam2 is not None:
                    cost = (
                        self.spatial_weight * spatial_cost
                        + self.appearance_weight * appearance_cost
                    )
                else:
                    cost = spatial_cost

                cost_matrix[i, j] = cost

        return cost_matrix

    def _compute_spatial_distance(
        self, person1: Dict[str, Any], person2: Dict[str, Any]
    ) -> float:
        """
        Compute normalized spatial distance between two persons.

        Args:
            person1: Person from camera 1
            person2: Person from camera 2

        Returns:
            Normalized distance (0-1)
        """
        # Get normalized center positions
        bbox1 = person1.get("bbox", [0, 0, 1, 1])
        bbox2 = person2.get("bbox", [0, 0, 1, 1])

        # Calculate centers (normalized coordinates 0-1)
        center1 = np.array([
            (bbox1[0] + bbox1[2]) / 2.0,
            (bbox1[1] + bbox1[3]) / 2.0,
        ])

        center2 = np.array([
            (bbox2[0] + bbox2[2]) / 2.0,
            (bbox2[1] + bbox2[3]) / 2.0,
        ])

        # Euclidean distance (normalized to 0-1 range)
        distance = np.linalg.norm(center1 - center2)

        # Normalize by diagonal (max possible distance is sqrt(2))
        normalized_distance = min(distance / np.sqrt(2), 1.0)

        return normalized_distance

    def _compute_appearance_distance(
        self,
        person1: Dict[str, Any],
        person2: Dict[str, Any],
        frame1: np.ndarray,
        frame2: np.ndarray,
    ) -> float:
        """
        Compute appearance distance between two persons using color histograms.

        Args:
            person1: Person from camera 1
            person2: Person from camera 2
            frame1: Frame from camera 1
            frame2: Frame from camera 2

        Returns:
            Normalized distance (0-1)
        """
        # Extract person crops
        crop1 = self._extract_person_crop(person1, frame1)
        crop2 = self._extract_person_crop(person2, frame2)

        if crop1 is None or crop2 is None:
            return 1.0  # Maximum distance if crops unavailable

        # Compute color histograms
        hist1 = self._compute_color_histogram(crop1)
        hist2 = self._compute_color_histogram(crop2)

        # Compare histograms using correlation
        correlation = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)

        # Convert correlation (-1 to 1) to distance (0 to 1)
        # correlation = 1 (identical) -> distance = 0
        # correlation = -1 (opposite) -> distance = 1
        distance = (1.0 - correlation) / 2.0

        return distance

    def _extract_person_crop(
        self, person: Dict[str, Any], frame: np.ndarray
    ) -> Optional[np.ndarray]:
        """
        Extract person crop from frame.

        Args:
            person: Person detection
            frame: Source frame

        Returns:
            Cropped image or None
        """
        bbox = person.get("bbox")
        if bbox is None:
            return None

        x1, y1, x2, y2 = map(int, bbox)
        h, w = frame.shape[:2]

        # Clip to frame boundaries
        x1 = max(0, min(x1, w))
        y1 = max(0, min(y1, h))
        x2 = max(0, min(x2, w))
        y2 = max(0, min(y2, h))

        if x2 <= x1 or y2 <= y1:
            return None

        crop = frame[y1:y2, x1:x2]
        return crop

    def _compute_color_histogram(self, image: np.ndarray) -> np.ndarray:
        """
        Compute normalized color histogram.

        Args:
            image: Input image (BGR)

        Returns:
            Normalized histogram
        """
        # Convert to HSV for better color representation
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # Compute histogram
        hist = cv2.calcHist(
            [hsv],
            [0, 1, 2],  # H, S, V channels
            None,
            [8, 8, 8],  # Bins per channel
            [0, 180, 0, 256, 0, 256],  # Ranges
        )

        # Normalize
        hist = cv2.normalize(hist, hist).flatten()

        return hist

    def fuse_person_data(
        self,
        person_cam1: Dict[str, Any],
        person_cam2: Dict[str, Any],
        match_confidence: float,
    ) -> Dict[str, Any]:
        """
        Fuse data from two person detections.

        Args:
            person_cam1: Person from camera 1
            person_cam2: Person from camera 2
            match_confidence: Matching confidence

        Returns:
            Fused person data
        """
        # Use tracking ID from camera 1 (or merge if needed)
        track_id = person_cam1.get("track_id", person_cam2.get("track_id"))

        # Fuse PPE detections (OR logic - if either camera sees PPE, it exists)
        ppe_cam1 = person_cam1.get("ppe_status", {})
        ppe_cam2 = person_cam2.get("ppe_status", {})

        fused_ppe = {}
        all_ppe_types = set(ppe_cam1.keys()) | set(ppe_cam2.keys())

        for ppe_type in all_ppe_types:
            detected_cam1 = ppe_cam1.get(ppe_type, {}).get("detected", False)
            detected_cam2 = ppe_cam2.get(ppe_type, {}).get("detected", False)

            conf_cam1 = ppe_cam1.get(ppe_type, {}).get("confidence", 0.0)
            conf_cam2 = ppe_cam2.get(ppe_type, {}).get("confidence", 0.0)

            # Fusion logic: OR for detection, MAX for confidence
            fused_ppe[ppe_type] = {
                "detected": detected_cam1 or detected_cam2,
                "confidence": max(conf_cam1, conf_cam2),
                "cam1_detected": detected_cam1,
                "cam2_detected": detected_cam2,
                "cam1_confidence": conf_cam1,
                "cam2_confidence": conf_cam2,
            }

        # Create fused person
        fused_person = {
            "track_id": track_id,
            "bbox_cam1": person_cam1.get("bbox"),
            "bbox_cam2": person_cam2.get("bbox"),
            "ppe_status": fused_ppe,
            "match_confidence": match_confidence,
            "person_cam1": person_cam1,
            "person_cam2": person_cam2,
        }

        return fused_person
