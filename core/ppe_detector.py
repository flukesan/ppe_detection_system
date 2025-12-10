"""
PPE Detection module for detecting personal protective equipment.
"""

import cv2
import numpy as np
import torch
from typing import List, Dict, Any, Optional, Tuple
from ultralytics import YOLO


class PPEDetector:
    """
    Detector for Personal Protective Equipment (helmet, vest, gloves, etc.)
    """

    def __init__(
        self,
        model_path: str,
        device: str = "cuda:0",
        conf_threshold: float = 0.5,
        iou_threshold: float = 0.4,
        required_ppe: Optional[List[str]] = None,
    ):
        """
        Initialize PPE Detector.

        Args:
            model_path: Path to PPE detection model weights
            device: Device to run inference on
            conf_threshold: Confidence threshold for detections
            iou_threshold: IoU threshold for NMS
            required_ppe: List of required PPE items (e.g., ['helmet', 'vest'])
        """
        self.device = device if torch.cuda.is_available() else "cpu"
        self.conf_threshold = conf_threshold
        self.iou_threshold = iou_threshold
        self.required_ppe = required_ppe or ["helmet", "vest"]

        try:
            self.model = YOLO(model_path)
            self.model.to(self.device)
            self.class_names = self.model.names
            print(f"✅ PPE detection model loaded on {self.device}")
            print(f"   Detected classes: {self.class_names}")
        except Exception as e:
            print(f"❌ Error loading PPE model: {e}")
            raise

    def detect(
        self,
        frame: np.ndarray,
        roi: Optional[List[int]] = None,
        enabled_classes: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Detect PPE items in the frame or ROI.

        Args:
            frame: Input image (BGR format)
            roi: Region of interest [x1, y1, x2, y2] or None for full frame
            enabled_classes: List of class names to detect (None = all)

        Returns:
            List of PPE detections, each containing:
                - class_name: str
                - bbox: [x1, y1, x2, y2] in original frame coordinates
                - confidence: float
        """
        # Extract ROI if specified
        if roi is not None:
            x1, y1, x2, y2 = roi
            x1, y1 = max(0, x1), max(0, y1)
            x2 = min(frame.shape[1], x2)
            y2 = min(frame.shape[0], y2)
            roi_frame = frame[y1:y2, x1:x2]
            offset = (x1, y1)
        else:
            roi_frame = frame
            offset = (0, 0)

        if roi_frame.size == 0:
            return []

        # Run detection
        results = self.model.predict(
            roi_frame,
            conf=self.conf_threshold,
            iou=self.iou_threshold,
            device=self.device,
            verbose=False,
        )

        detections = []

        if len(results) == 0:
            return detections

        result = results[0]

        if result.boxes is not None and len(result.boxes) > 0:
            boxes = result.boxes.xyxy.cpu().numpy()
            confidences = result.boxes.conf.cpu().numpy()
            class_ids = result.boxes.cls.cpu().numpy().astype(int)

            for box, conf, cls_id in zip(boxes, confidences, class_ids):
                class_name = self.class_names[cls_id]

                # Filter by enabled classes
                if enabled_classes is not None and class_name not in enabled_classes:
                    continue

                # Convert bbox to original frame coordinates
                bbox = [
                    int(box[0]) + offset[0],
                    int(box[1]) + offset[1],
                    int(box[2]) + offset[0],
                    int(box[3]) + offset[1],
                ]

                detections.append({
                    "class_name": class_name,
                    "bbox": bbox,
                    "confidence": float(conf),
                })

        return detections

    def check_compliance(self, detections: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Check if detected PPE meets compliance requirements.

        Args:
            detections: List of PPE detections

        Returns:
            Dictionary containing:
                - compliant: bool
                - detected_ppe: List[str]
                - missing_ppe: List[str]
                - violations: List[str]
        """
        detected_classes = [d["class_name"].lower() for d in detections]
        detected_unique = list(set(detected_classes))

        missing_ppe = []
        for required in self.required_ppe:
            if required.lower() not in detected_classes:
                missing_ppe.append(required)

        compliant = len(missing_ppe) == 0

        violations = []
        if not compliant:
            violations.append(f"Missing PPE: {', '.join(missing_ppe)}")

        return {
            "compliant": compliant,
            "detected_ppe": detected_unique,
            "missing_ppe": missing_ppe,
            "violations": violations,
        }

    def draw_detections(
        self,
        frame: np.ndarray,
        detections: List[Dict[str, Any]],
        color: Tuple[int, int, int] = (0, 255, 0),
        thickness: int = 2,
    ) -> np.ndarray:
        """
        Draw PPE detections on the frame.

        Args:
            frame: Input image
            detections: List of PPE detections
            color: Color for bounding boxes
            thickness: Line thickness

        Returns:
            Frame with drawn detections
        """
        for det in detections:
            bbox = det["bbox"]
            class_name = det["class_name"]
            confidence = det["confidence"]

            # Draw bounding box
            cv2.rectangle(
                frame,
                (bbox[0], bbox[1]),
                (bbox[2], bbox[3]),
                color,
                thickness,
            )

            # Draw label
            label = f"{class_name} {confidence:.2f}"
            label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)

            # Background for label
            cv2.rectangle(
                frame,
                (bbox[0], bbox[1] - label_size[1] - 5),
                (bbox[0] + label_size[0], bbox[1]),
                color,
                -1,
            )

            # Text
            cv2.putText(
                frame,
                label,
                (bbox[0], bbox[1] - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 0, 0),
                1,
            )

        return frame

    def set_required_ppe(self, required_ppe: List[str]):
        """
        Update the list of required PPE items.

        Args:
            required_ppe: List of required PPE class names
        """
        self.required_ppe = required_ppe
        print(f"Updated required PPE: {self.required_ppe}")

    def get_available_classes(self) -> List[str]:
        """
        Get list of available PPE classes that can be detected.

        Returns:
            List of class names
        """
        return list(self.class_names.values())

    def __del__(self):
        """Cleanup resources."""
        if hasattr(self, 'model'):
            del self.model
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
