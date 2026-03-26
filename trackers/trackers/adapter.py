"""Adapter that bridges DetectionRecord/Tracklet types with the underlying trackers."""

from __future__ import annotations

import itertools
from collections import defaultdict
from types import SimpleNamespace

import numpy as np

from .bot_sort import BOTSORT
from .byte_tracker import BYTETracker
from .types import DetectionRecord, Tracklet

DEFAULT_CONFIG = {
    "track_high_thresh": 0.5,
    "track_low_thresh": 0.1,
    "new_track_thresh": 0.6,
    "track_buffer": 30,
    "match_thresh": 0.8,
    "fuse_score": True,
    # Bot-SORT specific
    "with_reid": True,
    "proximity_thresh": 0.5,
    "appearance_thresh": 0.25,
    "gmc_method": "none",
}


class _DetectionBatch:
    """Mimics the ultralytics Results interface expected by BYTETracker.update()."""

    def __init__(self, xywh: np.ndarray, conf: np.ndarray, cls: np.ndarray):
        self.xywh = xywh
        self.conf = conf
        self.cls = cls

    @property
    def xyxy(self) -> np.ndarray:
        """Convert xywh to xyxy format."""
        ret = self.xywh.copy()
        ret[:, :2] -= ret[:, 2:] / 2
        ret[:, 2:] += ret[:, :2]
        return ret

    def __getitem__(self, idx):
        """Support boolean/integer indexing."""
        return _DetectionBatch(self.xywh[idx], self.conf[idx], self.cls[idx])

    def __len__(self):
        return len(self.conf)


class MOTTracker:
    """Multi-object tracker adapter that wraps BYTETracker or BOTSORT.

    Converts between DetectionRecord/Tracklet types and the tracker's internal formats.

    Args:
        method: Tracking algorithm to use, either "bytetrack" or "botsort".
        frame_rate: Frame rate of the video sequence.
        **kwargs: Override default tracker config values.
    """

    def __init__(self, method: str = "botsort", frame_rate: int = 30, **kwargs):
        self._method = method
        self._frame_rate = frame_rate

        config = {**DEFAULT_CONFIG, **kwargs}
        args = SimpleNamespace(**config)

        if method == "bytetrack":
            self._tracker = BYTETracker(args, frame_rate=frame_rate)
        elif method == "botsort":
            self._tracker = BOTSORT(args, frame_rate=frame_rate)
        else:
            raise ValueError(f"Unknown tracking method: {method}. Use 'bytetrack' or 'botsort'.")

        self._use_reid = method == "botsort" and config["with_reid"]

    def track(self, records: list[DetectionRecord]) -> list[Tracklet]:
        """Process all detections across all frames and return tracklets.

        Records are grouped by frame_id and processed in temporal order (sorted by recording_time).
        Each detection is mapped back to its original DetectionRecord via the tracker's idx field.

        Args:
            records: List of detection records across all frames.

        Returns:
            List of Tracklet objects, each containing the detection records for one tracked object.
        """
        if not records:
            return []

        # Sort by recording_time, then group by frame_id
        sorted_records = sorted(records, key=lambda r: r.recording_time)
        grouped = itertools.groupby(sorted_records, key=lambda r: r.frame_id)

        tracklet_map: dict[int, list[DetectionRecord]] = defaultdict(list)

        for frame_id, frame_records_iter in grouped:
            frame_records = list(frame_records_iter)

            # Build detection batch
            batch = self._to_det_batch(frame_records)
            feats = self._to_feats(frame_records)

            # Run tracker
            results = self._tracker.update(batch, img=None, feats=feats)

            # Map results back to original DetectionRecords
            # results shape: (M, 8) -> [x1, y1, x2, y2, track_id, conf, cls, idx]
            for row in results:
                track_id = int(row[4])
                det_idx = int(row[7])
                if 0 <= det_idx < len(frame_records):
                    tracklet_map[track_id].append(frame_records[det_idx])

        # Build Tracklet objects
        tracklets = []
        for track_id, det_records in tracklet_map.items():
            tracklets.append(Tracklet(id=str(track_id), records=det_records))

        return tracklets

    def reset(self):
        """Reset tracker state for a new sequence."""
        self._tracker.reset()

    def _to_det_batch(self, frame_records: list[DetectionRecord]) -> _DetectionBatch:
        """Convert a list of DetectionRecords to a _DetectionBatch."""
        bboxes_xyxy = np.array([r.bbox for r in frame_records], dtype=np.float32)

        # Convert xyxy to xywh: center_x, center_y, width, height
        xywh = np.empty_like(bboxes_xyxy)
        xywh[:, 0] = (bboxes_xyxy[:, 0] + bboxes_xyxy[:, 2]) / 2  # cx
        xywh[:, 1] = (bboxes_xyxy[:, 1] + bboxes_xyxy[:, 3]) / 2  # cy
        xywh[:, 2] = bboxes_xyxy[:, 2] - bboxes_xyxy[:, 0]  # w
        xywh[:, 3] = bboxes_xyxy[:, 3] - bboxes_xyxy[:, 1]  # h

        conf = np.array([r.conf for r in frame_records], dtype=np.float32)
        cls = np.zeros(len(frame_records), dtype=np.float32)  # single class: Person

        return _DetectionBatch(xywh, conf, cls)

    def _to_feats(self, frame_records: list[DetectionRecord]) -> np.ndarray | None:
        """Extract ReID features from DetectionRecords."""
        if not self._use_reid:
            return None
        return np.stack([r.reid for r in frame_records], axis=0)
