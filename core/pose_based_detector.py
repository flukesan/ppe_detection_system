"""
Main detection algorithm combining pose detection, PPE detection, tracking, and temporal filtering.
"""

import cv2
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from .pose_detector import PoseDetector
from .ppe_detector import PPEDetector
from .tracker import PersonTracker
from .temporal_filter import TemporalFilter

# Import device selector for auto GPU detection
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.device_selector import get_best_device


class PoseBasedDetector:
    """
    Main detection pipeline that combines all detection components.
    """

    def __init__(
        self,
        pose_model_path: str,
        ppe_model_path: str,
        config: Dict[str, Any],
    ):
        """
        Initialize the complete detection system.

        Args:
            pose_model_path: Path to YOLOv9-Pose model
            ppe_model_path: Path to PPE detection model
            config: Configuration dictionary
        """
        self.config = config

        # Initialize components
        print("🚀 Initializing PPE Detection System...")

        # Get device from models config or auto-detect best device
        pose_device_config = config.get("models", {}).get("yolov8_pose", {}).get("device", "auto")
        ppe_device_config = config.get("models", {}).get("ppe_detection", {}).get("device", "auto")

        # Auto-select best available device (GPU if available, otherwise CPU)
        pose_device = get_best_device(pose_device_config)
        ppe_device = get_best_device(ppe_device_config)

        self.pose_detector = PoseDetector(
            model_path=pose_model_path,
            device=pose_device,
            conf_threshold=config["detection"]["confidence_threshold"],
            iou_threshold=config["detection"]["nms_threshold"],
        )

        self.ppe_detector = PPEDetector(
            model_path=ppe_model_path,
            device=ppe_device,
            conf_threshold=config["detection"]["confidence_threshold"],
            iou_threshold=config["detection"]["nms_threshold"],
            required_ppe=config["detection"]["required_ppe"],
        )

        self.tracker = PersonTracker(
            max_age=config["tracking"]["max_age"],
            min_hits=config["tracking"]["min_hits"],
            iou_threshold=config["tracking"]["iou_threshold"],
        )

        self.temporal_filter = TemporalFilter(
            buffer_size=config["temporal_filter"]["buffer_size"],
            violation_threshold=config["temporal_filter"]["violation_threshold"],
        )

        self.frame_count = 0
        self.fps = 0.0

        # Configuration for selective detection
        self.enabled_keypoints = None  # None = all keypoints enabled
        self.enabled_ppe_classes = None  # None = all classes enabled

        print("✅ PPE Detection System initialized successfully!")

    def process_frame(self, frame: np.ndarray) -> Dict[str, Any]:
        """
        Process a single frame through the complete pipeline.

        Args:
            frame: Input frame (BGR format)

        Returns:
            Dictionary containing:
                - persons: List of detected persons with tracking info
                - violations: List of persons with PPE violations
                - statistics: Overall statistics
                - annotated_frame: Frame with visualizations
        """
        self.frame_count += 1
        annotated_frame = frame.copy()

        # Step 1: Detect persons and poses
        pose_detections = self.pose_detector.detect(frame)

        # Step 2: Track persons
        tracked_persons = self.tracker.update(pose_detections)

        # Step 3: Detect PPE for each person
        persons_with_ppe = []
        violations = []

        for person in tracked_persons:
            person_id = person["person_id"]
            bbox = person["bbox"]
            keypoints = person.get("keypoints")

            # Get upper body ROI for PPE detection
            if keypoints is not None:
                roi = self.pose_detector.get_upper_body_roi(
                    keypoints,
                    frame.shape[:2]
                )
            else:
                roi = bbox

            # Detect PPE in ROI
            ppe_detections = self.ppe_detector.detect(
                frame,
                roi,
                enabled_classes=self.enabled_ppe_classes
            )

            # Check compliance
            compliance = self.ppe_detector.check_compliance(ppe_detections)

            # Apply temporal filtering
            filtered_status = self.temporal_filter.update(
                person_id=person_id,
                is_compliant=compliance["compliant"],
                detected_ppe=compliance["detected_ppe"],
                missing_ppe=compliance["missing_ppe"],
            )

            # Prepare person data
            person_data = {
                "person_id": person_id,
                "bbox": bbox,
                "keypoints": keypoints,
                "confidence": person["confidence"],
                "ppe_detections": ppe_detections,
                "compliance": compliance,
                "filtered_status": filtered_status,
            }

            persons_with_ppe.append(person_data)

            # Check if this is a violation
            if filtered_status["is_violation"]:
                violations.append(person_data)

        # Step 4: Cleanup old tracks
        active_ids = [p["person_id"] for p in tracked_persons]
        self.temporal_filter.cleanup_old_tracks(active_ids)

        # Step 5: Draw visualizations
        annotated_frame = self._draw_results(
            annotated_frame,
            persons_with_ppe,
        )

        # Step 6: Collect statistics
        statistics = self._collect_statistics(persons_with_ppe)

        return {
            "persons": persons_with_ppe,
            "violations": violations,
            "statistics": statistics,
            "annotated_frame": annotated_frame,
            "frame_count": self.frame_count,
        }

    def _draw_results(
        self,
        frame: np.ndarray,
        persons: List[Dict[str, Any]],
    ) -> np.ndarray:
        """
        Draw detection results on frame.

        Args:
            frame: Input frame
            persons: List of detected persons

        Returns:
            Annotated frame
        """
        for person in persons:
            person_id = person["person_id"]
            bbox = person["bbox"]
            keypoints = person["keypoints"]
            filtered_status = person["filtered_status"]
            ppe_detections = person["ppe_detections"]

            # Choose color based on compliance
            if filtered_status["is_violation"]:
                color = tuple(self.config["ui"]["colors"]["violation"])
            else:
                color = tuple(self.config["ui"]["colors"]["safe"])

            # Draw person bbox
            cv2.rectangle(
                frame,
                (bbox[0], bbox[1]),
                (bbox[2], bbox[3]),
                color,
                2,
            )

            # Draw person ID
            label = f"ID: {person_id}"
            cv2.putText(
                frame,
                label,
                (bbox[0], bbox[1] - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                color,
                2,
            )

            # Draw keypoints if enabled
            if self.config["ui"]["display"]["show_pose_keypoints"] and keypoints is not None:
                self.pose_detector.draw_keypoints(
                    frame,
                    keypoints,
                    color,
                    2,
                    enabled_keypoints=self.enabled_keypoints
                )

            # Draw PPE detections
            self.ppe_detector.draw_detections(frame, ppe_detections, color, 1)

            # Draw violation info
            if filtered_status["is_violation"]:
                missing = ", ".join(filtered_status["missing_ppe"])
                violation_text = f"Missing: {missing}"

                # Background for text
                text_size, _ = cv2.getTextSize(
                    violation_text,
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    1
                )

                cv2.rectangle(
                    frame,
                    (bbox[0], bbox[3] + 5),
                    (bbox[0] + text_size[0] + 10, bbox[3] + text_size[1] + 15),
                    (0, 0, 255),
                    -1,
                )

                cv2.putText(
                    frame,
                    violation_text,
                    (bbox[0] + 5, bbox[3] + text_size[1] + 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 255, 255),
                    1,
                )

        return frame

    def _collect_statistics(self, persons: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Collect detection statistics.

        Args:
            persons: List of detected persons

        Returns:
            Statistics dictionary
        """
        total_persons = len(persons)
        violations = sum(1 for p in persons if p["filtered_status"]["is_violation"])
        compliant = total_persons - violations

        temp_stats = self.temporal_filter.get_statistics()

        return {
            "frame_count": self.frame_count,
            "total_persons": total_persons,
            "compliant": compliant,
            "violations": violations,
            "violation_rate": violations / max(total_persons, 1) if total_persons > 0 else 0.0,
            "temporal_stats": temp_stats,
        }

    def reset(self):
        """Reset the detection system state."""
        self.tracker.reset()
        self.temporal_filter.reset()
        self.frame_count = 0

    def set_required_ppe(self, required_ppe: List[str]):
        """
        Update required PPE items.

        Args:
            required_ppe: List of required PPE class names
        """
        self.ppe_detector.set_required_ppe(required_ppe)
        self.config["detection"]["required_ppe"] = required_ppe

    def set_enabled_keypoints(self, enabled_keypoints: Optional[List[int]]):
        """
        Set which keypoints to display.

        Args:
            enabled_keypoints: List of keypoint indices to display (0-16), or None for all
        """
        self.enabled_keypoints = enabled_keypoints

    def set_enabled_ppe_classes(self, enabled_classes: Optional[List[str]]):
        """
        Set which PPE classes to detect.

        Args:
            enabled_classes: List of PPE class names to detect, or None for all
        """
        self.enabled_ppe_classes = enabled_classes

    def get_config(self) -> Dict[str, Any]:
        """Get current configuration."""
        return self.config

    def update_config(self, config: Dict[str, Any]):
        """
        Update configuration.

        Args:
            config: New configuration dictionary
        """
        self.config.update(config)

        # Update components if needed
        if "temporal_filter" in config:
            if "violation_threshold" in config["temporal_filter"]:
                self.temporal_filter.set_violation_threshold(
                    config["temporal_filter"]["violation_threshold"]
                )
