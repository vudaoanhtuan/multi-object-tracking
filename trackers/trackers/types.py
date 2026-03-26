"""Data types for multi-object tracking."""

from __future__ import annotations

import dataclasses
import datetime

import numpy as np


@dataclasses.dataclass
class DetectionRecord:
    """A single detection from a YOLO model.

    Attributes:
        id: Unique identifier for this detection.
        frame_id: Identifier for the frame this detection belongs to.
        bbox: Bounding box as [x_min, y_min, x_max, y_max] in int32.
        recording_time: Timestamp of the recording.
        conf: Confidence score of the detection.
        reid: ReID feature vector, float32, 1024 dimensions.
    """

    id: str
    frame_id: str
    bbox: np.ndarray
    recording_time: datetime.datetime
    conf: float
    reid: np.ndarray


@dataclasses.dataclass
class Tracklet:
    """A tracked object across multiple frames.

    Attributes:
        id: Unique identifier for this tracklet.
        records: List of detection records belonging to this tracklet, ordered by time.
    """

    id: str
    records: list[DetectionRecord]
