from dataclasses import dataclass


@dataclass
class BoundingBox:
    object_id: int
    x_min: int
    y_min: int
    x_max: int
    y_max: int

    @property
    def width(self) -> int:
        return self.x_max - self.x_min

    @property
    def height(self) -> int:
        return self.y_max - self.y_min

    def iou(self, other: "BoundingBox") -> float:
        """Calculate Intersection over Union (IoU) with another bounding box."""
        # Intersection coordinates
        x_left = max(self.x_min, other.x_min)
        y_top = max(self.y_min, other.y_min)
        x_right = min(self.x_max, other.x_max)
        y_bottom = min(self.y_max, other.y_max)

        if x_right < x_left or y_bottom < y_top:
            return 0.0

        intersection_area = (x_right - x_left) * (y_bottom - y_top)

        self_area = self.width * self.height
        other_area = other.width * other.height

        union_area = self_area + other_area - intersection_area

        if union_area == 0:
            return 0.0

        return intersection_area / union_area
