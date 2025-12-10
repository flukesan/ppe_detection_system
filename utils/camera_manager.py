"""
Camera management utility for handling multiple camera sources.
"""

import cv2
from typing import Optional, Tuple
import numpy as np


class CameraManager:
    """
    Manager for camera operations and multi-camera support.
    """

    def __init__(self):
        """Initialize camera manager."""
        self.cameras = {}
        self.current_camera_id = None

    def list_available_cameras(self, max_cameras: int = 10) -> list:
        """
        List available camera devices.

        Args:
            max_cameras: Maximum number of cameras to check

        Returns:
            List of available camera IDs
        """
        available = []

        for i in range(max_cameras):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                available.append(i)
                cap.release()

        return available

    def open_camera(
        self,
        camera_id: int,
        width: int = 1280,
        height: int = 720,
        fps: int = 30,
    ) -> bool:
        """
        Open a camera device.

        Args:
            camera_id: Camera device ID
            width: Frame width
            height: Frame height
            fps: Frames per second

        Returns:
            True if successful
        """
        if camera_id in self.cameras:
            return True

        cap = cv2.VideoCapture(camera_id)

        if not cap.isOpened():
            return False

        # Set properties
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        cap.set(cv2.CAP_PROP_FPS, fps)

        self.cameras[camera_id] = cap
        self.current_camera_id = camera_id

        return True

    def read_frame(self, camera_id: Optional[int] = None) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Read a frame from camera.

        Args:
            camera_id: Camera ID (default: current camera)

        Returns:
            (success, frame)
        """
        cam_id = camera_id or self.current_camera_id

        if cam_id not in self.cameras:
            return False, None

        return self.cameras[cam_id].read()

    def close_camera(self, camera_id: Optional[int] = None):
        """
        Close a camera.

        Args:
            camera_id: Camera ID (default: current camera)
        """
        cam_id = camera_id or self.current_camera_id

        if cam_id in self.cameras:
            self.cameras[cam_id].release()
            del self.cameras[cam_id]

            if self.current_camera_id == cam_id:
                self.current_camera_id = None

    def close_all(self):
        """Close all cameras."""
        for cam_id in list(self.cameras.keys()):
            self.close_camera(cam_id)

    def __del__(self):
        """Cleanup."""
        self.close_all()
