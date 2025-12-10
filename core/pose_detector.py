"""
Pose Detection module using YOLOv9-Pose for detecting human poses and keypoints.
"""

import cv2
import numpy as np
import torch
from typing import List, Tuple, Optional, Dict, Any
from ultralytics import YOLO


class PoseDetector:
    """
    Wrapper for YOLOv9-Pose model to detect human poses and keypoints.
    """

    # COCO keypoint indices
    KEYPOINT_NAMES = [
        "nose", "left_eye", "right_eye", "left_ear", "right_ear",
        "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
        "left_wrist", "right_wrist", "left_hip", "right_hip",
        "left_knee", "right_knee", "left_ankle", "right_ankle"
    ]

    def __init__(
        self,
        model_path: str,
        device: str = "cuda:0",
        conf_threshold: float = 0.5,
        iou_threshold: float = 0.4,
    ):
        """
        Initialize Pose Detector.

        Args:
            model_path: Path to YOLOv9-Pose model weights
            device: Device to run inference on ('cuda:0' or 'cpu')
            conf_threshold: Confidence threshold for detections
            iou_threshold: IoU threshold for NMS
        """
        self.device = device if torch.cuda.is_available() else "cpu"
        self.conf_threshold = conf_threshold
        self.iou_threshold = iou_threshold

        try:
            self.model = YOLO(model_path)
            self.model.to(self.device)
            print(f"✅ Pose detection model loaded on {self.device}")
        except Exception as e:
            print(f"❌ Error loading pose model: {e}")
            raise

    def detect(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """
        Detect persons and their poses in the frame.

        Args:
            frame: Input image (BGR format)

        Returns:
            List of detections, each containing:
                - bbox: [x1, y1, x2, y2]
                - confidence: float
                - keypoints: numpy array of shape (17, 3) with [x, y, confidence]
                - person_id: int (temporary ID before tracking)
        """
        results = self.model.predict(
            frame,
            conf=self.conf_threshold,
            iou=self.iou_threshold,
            device=self.device,
            verbose=False,
        )

        detections = []

        if len(results) == 0:
            return detections

        result = results[0]

        # Extract boxes and keypoints
        if result.boxes is not None and len(result.boxes) > 0:
            boxes = result.boxes.xyxy.cpu().numpy()
            confidences = result.boxes.conf.cpu().numpy()

            # Extract keypoints if available
            keypoints_data = None
            if hasattr(result, 'keypoints') and result.keypoints is not None:
                keypoints_data = result.keypoints.data.cpu().numpy()

            for i, (box, conf) in enumerate(zip(boxes, confidences)):
                detection = {
                    "bbox": box.astype(int).tolist(),
                    "confidence": float(conf),
                    "keypoints": None,
                    "person_id": -1,  # Will be assigned by tracker
                }

                # Add keypoints if available
                if keypoints_data is not None and i < len(keypoints_data):
                    detection["keypoints"] = keypoints_data[i]

                detections.append(detection)

        return detections

    def get_body_bbox_from_keypoints(
        self,
        keypoints: np.ndarray,
        expand_ratio: float = 0.1
    ) -> Optional[List[int]]:
        """
        Calculate body bounding box from keypoints.

        Args:
            keypoints: Array of shape (17, 3) with [x, y, confidence]
            expand_ratio: Ratio to expand the bbox

        Returns:
            Bounding box [x1, y1, x2, y2] or None
        """
        # Filter visible keypoints (confidence > 0)
        visible_kpts = keypoints[keypoints[:, 2] > 0.0]

        if len(visible_kpts) < 3:
            return None

        x_coords = visible_kpts[:, 0]
        y_coords = visible_kpts[:, 1]

        x1, y1 = x_coords.min(), y_coords.min()
        x2, y2 = x_coords.max(), y_coords.max()

        # Expand bbox
        w, h = x2 - x1, y2 - y1
        x1 = max(0, int(x1 - w * expand_ratio))
        y1 = max(0, int(y1 - h * expand_ratio))
        x2 = int(x2 + w * expand_ratio)
        y2 = int(y2 + h * expand_ratio)

        return [x1, y1, x2, y2]

    def get_upper_body_roi(
        self,
        keypoints: np.ndarray,
        frame_shape: Tuple[int, int]
    ) -> Optional[List[int]]:
        """
        Extract upper body region (for helmet/vest detection).

        Args:
            keypoints: Array of shape (17, 3)
            frame_shape: (height, width) of the frame

        Returns:
            ROI [x1, y1, x2, y2] or None
        """
        # Key indices for upper body
        shoulders = [5, 6]  # left_shoulder, right_shoulder
        hips = [11, 12]  # left_hip, right_hip
        nose = 0

        # Check if key points are visible
        key_indices = [nose] + shoulders + hips
        key_kpts = keypoints[key_indices]

        if np.sum(key_kpts[:, 2] > 0.0) < 3:
            return None

        visible_kpts = key_kpts[key_kpts[:, 2] > 0.0]

        x1 = int(visible_kpts[:, 0].min())
        y1 = int(visible_kpts[:, 1].min())
        x2 = int(visible_kpts[:, 0].max())
        y2 = int(visible_kpts[:, 1].max())

        # Expand horizontally for better detection
        w = x2 - x1
        x1 = max(0, int(x1 - w * 0.3))
        x2 = min(frame_shape[1], int(x2 + w * 0.3))

        # Expand vertically (mainly upward for helmet)
        h = y2 - y1
        y1 = max(0, int(y1 - h * 0.4))
        y2 = min(frame_shape[0], int(y2 + h * 0.2))

        return [x1, y1, x2, y2]

    def draw_keypoints(
        self,
        frame: np.ndarray,
        keypoints: np.ndarray,
        color: Tuple[int, int, int] = (0, 255, 0),
        thickness: int = 2,
    ) -> np.ndarray:
        """
        Draw pose keypoints and skeleton on the frame.

        Args:
            frame: Input image
            keypoints: Array of shape (17, 3)
            color: Color for drawing
            thickness: Line thickness

        Returns:
            Frame with drawn keypoints
        """
        # COCO skeleton connections
        skeleton = [
            [0, 1], [0, 2], [1, 3], [2, 4],  # Head
            [5, 6], [5, 7], [7, 9], [6, 8], [8, 10],  # Arms
            [5, 11], [6, 12], [11, 12],  # Torso
            [11, 13], [13, 15], [12, 14], [14, 16],  # Legs
        ]

        # Draw skeleton connections
        for connection in skeleton:
            kpt1, kpt2 = keypoints[connection[0]], keypoints[connection[1]]

            if kpt1[2] > 0.5 and kpt2[2] > 0.5:
                pt1 = (int(kpt1[0]), int(kpt1[1]))
                pt2 = (int(kpt2[0]), int(kpt2[1]))
                cv2.line(frame, pt1, pt2, color, thickness)

        # Draw keypoints
        for kpt in keypoints:
            if kpt[2] > 0.5:
                center = (int(kpt[0]), int(kpt[1]))
                cv2.circle(frame, center, 4, color, -1)

        return frame

    def __del__(self):
        """Cleanup resources."""
        if hasattr(self, 'model'):
            del self.model
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
