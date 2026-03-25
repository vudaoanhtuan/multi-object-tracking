from dataclasses import dataclass, field
from pathlib import Path

from mot_va.models.bbox import BoundingBox


@dataclass
class Frame:
    frame_id: str
    image_path: Path
    label_path: Path
    bboxes: list[BoundingBox] = field(default_factory=list)
    labels_loaded: bool = field(default=False, repr=False)
