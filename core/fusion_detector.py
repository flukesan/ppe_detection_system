"""
Multi-camera fusion detector for combining detection results from multiple views.
"""

import numpy as np
from typing import Dict, Any, List, Tuple, Optional
from .pose_based_detector import PoseBasedDetector
from .person_matcher import PersonMatcher


class FusionDetector:
    """
    Detector that fuses results from multiple camera views for improved accuracy.
    """

    def __init__(
        self,
        pose_model_path: str,
        ppe_model_path: str,
        config: Dict[str, Any],
        num_cameras: int = 2,
    ):
        """
        Initialize fusion detector.

        Args:
            pose_model_path: Path to pose detection model
            ppe_model_path: Path to PPE detection model
            config: Configuration dictionary
            num_cameras: Number of cameras (default: 2)
        """
        self.config = config
        self.num_cameras = num_cameras

        # Create separate detector instances for each camera
        # This ensures independent processing pipelines
        print(f"🚀 Initializing {num_cameras}-Camera Fusion Detection System...")

        self.detectors = []
        for i in range(num_cameras):
            print(f"   Camera {i+1} detector...")
            detector = PoseBasedDetector(
                pose_model_path=pose_model_path,
                ppe_model_path=ppe_model_path,
                config=config,
            )
            self.detectors.append(detector)

        # Person matcher for cross-view matching
        fusion_config = config.get("fusion", {})
        self.person_matcher = PersonMatcher(
            spatial_weight=fusion_config.get("spatial_weight", 0.6),
            appearance_weight=fusion_config.get("appearance_weight", 0.4),
            max_distance_threshold=fusion_config.get("max_distance_threshold", 0.5),
        )

        # Fusion strategy
        self.fusion_strategy = fusion_config.get("strategy", "or")  # "or", "and", "weighted"

        print(f"✅ Multi-Camera Fusion System initialized!")
        print(f"   Cameras: {num_cameras}")
        print(f"   Fusion Strategy: {self.fusion_strategy.upper()}")

    def process_frames(
        self,
        frames: List[np.ndarray],
    ) -> Dict[str, Any]:
        """
        Process frames from multiple cameras and fuse results.

        Args:
            frames: List of frames from each camera (must match num_cameras)

        Returns:
            Fused detection results
        """
        if len(frames) != self.num_cameras:
            raise ValueError(
                f"Expected {self.num_cameras} frames, got {len(frames)}"
            )

        # Step 1: Process each camera independently
        camera_results = []
        for i, (frame, detector) in enumerate(zip(frames, self.detectors)):
            if frame is None:
                # Handle missing frame (camera disconnected or error)
                camera_results.append(None)
            else:
                results = detector.process_frame(frame)
                camera_results.append(results)

        # Step 2: Fuse results from all cameras
        fused_results = self._fuse_results(camera_results, frames)

        return fused_results

    def _fuse_results(
        self,
        camera_results: List[Optional[Dict[str, Any]]],
        frames: List[np.ndarray],
    ) -> Dict[str, Any]:
        """
        Fuse detection results from multiple cameras.

        Args:
            camera_results: List of results from each camera
            frames: Original frames

        Returns:
            Fused results
        """
        # Filter out None results
        valid_results = [(i, r) for i, r in enumerate(camera_results) if r is not None]

        if len(valid_results) == 0:
            # No valid results
            return self._empty_results()

        if len(valid_results) == 1:
            # Only one camera has results, return as-is
            idx, results = valid_results[0]
            results["fusion_mode"] = "single_camera"
            results["active_cameras"] = [idx]
            return results

        # Multi-camera fusion (currently support 2 cameras)
        if len(valid_results) == 2:
            return self._fuse_two_cameras(valid_results, frames)
        else:
            # For >2 cameras, use first camera as reference
            idx, results = valid_results[0]
            results["fusion_mode"] = "multi_camera_partial"
            results["active_cameras"] = [i for i, _ in valid_results]
            return results

    def _fuse_two_cameras(
        self,
        camera_results: List[Tuple[int, Dict[str, Any]]],
        frames: List[np.ndarray],
    ) -> Dict[str, Any]:
        """
        Fuse results from two cameras.

        Args:
            camera_results: [(camera_idx, results), ...]
            frames: Original frames

        Returns:
            Fused results
        """
        cam1_idx, results1 = camera_results[0]
        cam2_idx, results2 = camera_results[1]

        persons1 = results1.get("persons", [])
        persons2 = results2.get("persons", [])

        # Match persons across cameras
        matches = self.person_matcher.match_persons(
            persons1,
            persons2,
            frames[cam1_idx],
            frames[cam2_idx],
        )

        # Create fused persons list
        fused_persons = []
        matched_cam1 = set()
        matched_cam2 = set()

        # Process matched persons
        for idx1, idx2, confidence in matches:
            person1 = persons1[idx1]
            person2 = persons2[idx2]

            fused_person = self.person_matcher.fuse_person_data(
                person1, person2, confidence
            )

            # Apply fusion strategy for violation detection
            violation1 = person1.get("filtered_status", {}).get("has_violation", False)
            violation2 = person2.get("filtered_status", {}).get("has_violation", False)

            if self.fusion_strategy == "or":
                # Violation if either camera detects it
                has_violation = violation1 or violation2
            elif self.fusion_strategy == "and":
                # Violation only if both cameras detect it
                has_violation = violation1 and violation2
            else:  # weighted
                # Consider match confidence
                has_violation = (violation1 or violation2) and confidence > 0.5

            # Update filtered status
            fused_person["filtered_status"] = {
                "has_violation": has_violation,
                "missing_ppe": self._merge_missing_ppe(person1, person2),
                "cam1_violation": violation1,
                "cam2_violation": violation2,
            }

            fused_persons.append(fused_person)
            matched_cam1.add(idx1)
            matched_cam2.add(idx2)

        # Add unmatched persons from camera 1
        for idx, person in enumerate(persons1):
            if idx not in matched_cam1:
                person["camera_source"] = cam1_idx
                person["match_confidence"] = 0.0  # No match
                fused_persons.append(person)

        # Add unmatched persons from camera 2
        for idx, person in enumerate(persons2):
            if idx not in matched_cam2:
                person["camera_source"] = cam2_idx
                person["match_confidence"] = 0.0  # No match
                fused_persons.append(person)

        # Aggregate statistics
        total_persons = len(fused_persons)
        violations = [p for p in fused_persons if p.get("filtered_status", {}).get("has_violation", False)]
        num_violations = len(violations)

        # Create combined annotated frame (side-by-side)
        annotated_frame = self._create_side_by_side_frame(
            results1.get("annotated_frame"),
            results2.get("annotated_frame"),
            matches,
        )

        return {
            "persons": fused_persons,
            "violations": violations,
            "statistics": {
                "total_persons": total_persons,
                "violations": num_violations,
                "compliance_rate": (
                    (total_persons - num_violations) / total_persons * 100
                    if total_persons > 0
                    else 100.0
                ),
                "matched_persons": len(matches),
                "cam1_only": len([p for p in fused_persons if p.get("camera_source") == cam1_idx]),
                "cam2_only": len([p for p in fused_persons if p.get("camera_source") == cam2_idx]),
            },
            "annotated_frame": annotated_frame,
            "fusion_mode": "dual_camera",
            "active_cameras": [cam1_idx, cam2_idx],
            "num_matches": len(matches),
        }

    def _merge_missing_ppe(
        self, person1: Dict[str, Any], person2: Dict[str, Any]
    ) -> List[str]:
        """
        Merge missing PPE lists from two persons using OR logic.

        Args:
            person1: Person from camera 1
            person2: Person from camera 2

        Returns:
            List of missing PPE items
        """
        missing1 = set(person1.get("filtered_status", {}).get("missing_ppe", []))
        missing2 = set(person2.get("filtered_status", {}).get("missing_ppe", []))

        # Item is missing only if BOTH cameras don't see it
        # (if either camera sees it, it's not missing)
        all_required = missing1 | missing2
        seen_by_either = (missing1 ^ missing2) - (missing1 & missing2)

        # Items that both cameras agree are missing
        truly_missing = missing1 & missing2

        return list(truly_missing)

    def _create_side_by_side_frame(
        self,
        frame1: Optional[np.ndarray],
        frame2: Optional[np.ndarray],
        matches: List[Tuple[int, int, float]],
    ) -> Optional[np.ndarray]:
        """
        Create side-by-side visualization of two camera views.

        Args:
            frame1: Annotated frame from camera 1
            frame2: Annotated frame from camera 2
            matches: List of person matches

        Returns:
            Combined frame or None
        """
        if frame1 is None or frame2 is None:
            return frame1 if frame1 is not None else frame2

        # Resize frames to same height
        h1, w1 = frame1.shape[:2]
        h2, w2 = frame2.shape[:2]

        target_height = min(h1, h2)
        frame1_resized = cv2.resize(frame1, (int(w1 * target_height / h1), target_height))
        frame2_resized = cv2.resize(frame2, (int(w2 * target_height / h2), target_height))

        # Concatenate horizontally
        combined = np.hstack([frame1_resized, frame2_resized])

        # Add labels
        import cv2
        cv2.putText(
            combined,
            "Camera 1",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (0, 255, 255),
            2,
        )

        cam2_x_offset = frame1_resized.shape[1] + 10
        cv2.putText(
            combined,
            "Camera 2",
            (cam2_x_offset, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (0, 255, 255),
            2,
        )

        # Add match count
        cv2.putText(
            combined,
            f"Matched: {len(matches)} persons",
            (10, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2,
        )

        return combined

    def _empty_results(self) -> Dict[str, Any]:
        """Return empty results structure."""
        return {
            "persons": [],
            "violations": [],
            "statistics": {
                "total_persons": 0,
                "violations": 0,
                "compliance_rate": 100.0,
            },
            "annotated_frame": None,
            "fusion_mode": "no_camera",
            "active_cameras": [],
        }

    def set_enabled_keypoints(self, keypoints: List[int]):
        """Set enabled keypoints for all detectors."""
        for detector in self.detectors:
            detector.set_enabled_keypoints(keypoints)

    def set_enabled_ppe_classes(self, classes: List[str]):
        """Set enabled PPE classes for all detectors."""
        for detector in self.detectors:
            detector.set_enabled_ppe_classes(classes)

    def set_required_ppe(self, required_ppe: List[str]):
        """Set required PPE for all detectors."""
        for detector in self.detectors:
            detector.set_required_ppe(required_ppe)


# Import cv2 for visualization
import cv2
