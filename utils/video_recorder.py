"""
Video recording utility for saving violation footage.
"""

import cv2
import os
from typing import Optional
from datetime import datetime
from collections import deque
import numpy as np


class VideoRecorder:
    """
    Video recorder for capturing violation footage.
    """

    def __init__(self, config: dict):
        """
        Initialize video recorder.

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.writer = None
        self.is_recording = False
        self.current_file = None

        # Ring buffer for pre-violation frames
        buffer_size = config.get("pre_buffer", 5) * 30  # 5 seconds at 30 FPS
        self.frame_buffer = deque(maxlen=buffer_size)

    def start_recording(
        self,
        person_id: int,
        frame_width: int,
        frame_height: int,
        fps: float = 30.0,
    ) -> Optional[str]:
        """
        Start recording a violation video.

        Args:
            person_id: Person ID
            frame_width: Frame width
            frame_height: Frame height
            fps: Frames per second

        Returns:
            Path to output file
        """
        if self.is_recording:
            return self.current_file

        # Create output directory
        save_path = self.config.get("save_path", "data/videos/")
        os.makedirs(save_path, exist_ok=True)

        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"violation_person{person_id}_{timestamp}.mp4"
        self.current_file = os.path.join(save_path, filename)

        # Initialize video writer
        fourcc = cv2.VideoWriter_fourcc(*self.config.get("codec", "mp4v"))

        self.writer = cv2.VideoWriter(
            self.current_file,
            fourcc,
            fps,
            (frame_width, frame_height)
        )

        if not self.writer.isOpened():
            print(f"Failed to open video writer: {self.current_file}")
            return None

        self.is_recording = True

        # Write buffered frames
        for frame in self.frame_buffer:
            self.writer.write(frame)

        return self.current_file

    def add_frame(self, frame: np.ndarray):
        """
        Add frame to recording or buffer.

        Args:
            frame: Frame to add
        """
        if self.is_recording and self.writer is not None:
            self.writer.write(frame)
        else:
            # Add to ring buffer
            self.frame_buffer.append(frame.copy())

    def stop_recording(self) -> Optional[str]:
        """
        Stop recording and save file.

        Returns:
            Path to saved file
        """
        if not self.is_recording:
            return None

        if self.writer is not None:
            self.writer.release()

        self.is_recording = False
        saved_file = self.current_file
        self.current_file = None

        return saved_file

    def is_recording_active(self) -> bool:
        """Check if recording is active."""
        return self.is_recording

    def __del__(self):
        """Cleanup."""
        if self.is_recording:
            self.stop_recording()
