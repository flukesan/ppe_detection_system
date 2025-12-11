"""
Zone manager for handling polygon-based detection zones.
"""

import numpy as np
import cv2
from typing import List, Tuple, Dict, Any, Optional
import json


class Zone:
    """
    Represents a polygon-based detection zone.
    """

    def __init__(
        self,
        name: str,
        points: List[Tuple[int, int]],
        color: Tuple[int, int, int] = (0, 255, 0),
        enabled: bool = True,
    ):
        """
        Initialize a zone.

        Args:
            name: Zone name
            points: List of (x, y) points defining the polygon
            color: Zone color in BGR format
            enabled: Whether zone is enabled
        """
        self.name = name
        self.points = np.array(points, dtype=np.int32)
        self.color = color
        self.enabled = enabled

    def contains_point(self, point: Tuple[float, float]) -> bool:
        """
        Check if a point is inside the polygon zone.

        Args:
            point: (x, y) coordinates

        Returns:
            True if point is inside the zone
        """
        if not self.enabled:
            return False

        # Use cv2.pointPolygonTest for accurate point-in-polygon test
        # Returns: positive (inside), 0 (on edge), negative (outside)
        result = cv2.pointPolygonTest(self.points, point, False)
        return result >= 0

    def draw(
        self,
        frame: np.ndarray,
        thickness: int = 2,
        fill_alpha: float = 0.3,
    ) -> np.ndarray:
        """
        Draw the zone on a frame.

        Args:
            frame: Frame to draw on
            thickness: Line thickness
            fill_alpha: Fill transparency (0-1)

        Returns:
            Frame with zone drawn
        """
        if not self.enabled:
            return frame

        # Create overlay for semi-transparent fill
        overlay = frame.copy()

        # Fill polygon
        cv2.fillPoly(overlay, [self.points], self.color)

        # Draw polygon outline
        cv2.polylines(frame, [self.points], True, self.color, thickness)

        # Blend with original frame for transparency
        cv2.addWeighted(overlay, fill_alpha, frame, 1 - fill_alpha, 0, frame)

        # Draw zone name
        if len(self.points) > 0:
            # Calculate center of polygon for label placement
            M = cv2.moments(self.points)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])

                # Draw label background
                label = f"{self.name}"
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 0.6
                font_thickness = 2
                (text_w, text_h), _ = cv2.getTextSize(
                    label, font, font_scale, font_thickness
                )

                # Draw background rectangle
                cv2.rectangle(
                    frame,
                    (cx - text_w // 2 - 5, cy - text_h // 2 - 5),
                    (cx + text_w // 2 + 5, cy + text_h // 2 + 5),
                    self.color,
                    -1,
                )

                # Draw text
                cv2.putText(
                    frame,
                    label,
                    (cx - text_w // 2, cy + text_h // 2),
                    font,
                    font_scale,
                    (255, 255, 255),
                    font_thickness,
                )

        return frame

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert zone to dictionary for serialization.

        Returns:
            Dictionary representation
        """
        return {
            "name": self.name,
            "points": self.points.tolist(),
            "color": self.color,
            "enabled": self.enabled,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Zone":
        """
        Create zone from dictionary.

        Args:
            data: Dictionary representation

        Returns:
            Zone instance
        """
        return Zone(
            name=data["name"],
            points=data["points"],
            color=tuple(data["color"]),
            enabled=data.get("enabled", True),
        )


class ZoneManager:
    """
    Manages multiple detection zones.
    """

    def __init__(self):
        """Initialize zone manager."""
        self.zones: List[Zone] = []

    def add_zone(
        self,
        name: str,
        points: List[Tuple[int, int]],
        color: Tuple[int, int, int] = (0, 255, 0),
    ) -> Zone:
        """
        Add a new zone.

        Args:
            name: Zone name
            points: List of (x, y) points
            color: Zone color in BGR

        Returns:
            Created zone
        """
        zone = Zone(name, points, color)
        self.zones.append(zone)
        return zone

    def remove_zone(self, zone_name: str) -> bool:
        """
        Remove a zone by name.

        Args:
            zone_name: Name of zone to remove

        Returns:
            True if zone was removed
        """
        for i, zone in enumerate(self.zones):
            if zone.name == zone_name:
                self.zones.pop(i)
                return True
        return False

    def get_zone(self, zone_name: str) -> Optional[Zone]:
        """
        Get a zone by name.

        Args:
            zone_name: Zone name

        Returns:
            Zone if found, None otherwise
        """
        for zone in self.zones:
            if zone.name == zone_name:
                return zone
        return None

    def clear_zones(self):
        """Clear all zones."""
        self.zones.clear()

    def is_point_in_any_zone(self, point: Tuple[float, float]) -> bool:
        """
        Check if a point is inside any enabled zone.

        Args:
            point: (x, y) coordinates

        Returns:
            True if point is in any zone, or if no zones are defined
        """
        # If no zones are defined, allow detection everywhere
        if len(self.zones) == 0:
            return True

        # Check if point is in any enabled zone
        for zone in self.zones:
            if zone.enabled and zone.contains_point(point):
                return True

        return False

    def draw_zones(
        self,
        frame: np.ndarray,
        show_zones: bool = True,
    ) -> np.ndarray:
        """
        Draw all zones on a frame.

        Args:
            frame: Frame to draw on
            show_zones: Whether to show zones (False for fullscreen mode)

        Returns:
            Frame with zones drawn
        """
        if not show_zones:
            return frame

        for zone in self.zones:
            if zone.enabled:
                frame = zone.draw(frame)

        return frame

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert zones to dictionary for serialization.

        Returns:
            Dictionary representation
        """
        return {
            "zones": [zone.to_dict() for zone in self.zones]
        }

    def from_dict(self, data: Dict[str, Any]):
        """
        Load zones from dictionary.

        Args:
            data: Dictionary representation
        """
        self.zones.clear()
        for zone_data in data.get("zones", []):
            zone = Zone.from_dict(zone_data)
            self.zones.append(zone)

    def save_to_file(self, filepath: str):
        """
        Save zones to JSON file.

        Args:
            filepath: Path to save file
        """
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    def load_from_file(self, filepath: str):
        """
        Load zones from JSON file.

        Args:
            filepath: Path to load file
        """
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                self.from_dict(data)
        except FileNotFoundError:
            # File doesn't exist yet, start with empty zones
            pass
        except Exception as e:
            print(f"⚠️ Error loading zones from {filepath}: {e}")
