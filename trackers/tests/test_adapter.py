"""Smoke tests for the MOTTracker adapter."""

import datetime

import numpy as np

from trackers import DetectionRecord, MOTTracker, Tracklet


def _make_record(frame_id: str, x_min: int, y_min: int, x_max: int, y_max: int, conf: float = 0.9) -> DetectionRecord:
    """Helper to create a DetectionRecord with random reid features."""
    return DetectionRecord(
        id=f"det_{frame_id}_{x_min}",
        frame_id=frame_id,
        bbox=np.array([x_min, y_min, x_max, y_max], dtype=np.int32),
        recording_time=datetime.datetime(2024, 1, 1, 0, 0, int(frame_id)),
        conf=conf,
        reid=np.random.randn(1024).astype(np.float32),
    )


def _make_sequence() -> list[DetectionRecord]:
    """Create a simple 5-frame sequence with 2 objects moving linearly."""
    records = []
    for frame in range(5):
        # Object A: moves right
        records.append(_make_record(str(frame), 100 + frame * 10, 100, 200 + frame * 10, 200))
        # Object B: moves down
        records.append(_make_record(str(frame), 300, 100 + frame * 10, 400, 200 + frame * 10))
    return records


def test_bytetrack_returns_tracklets():
    tracker = MOTTracker(method="bytetrack", frame_rate=30)
    records = _make_sequence()
    tracklets = tracker.track(records)

    assert isinstance(tracklets, list)
    assert all(isinstance(t, Tracklet) for t in tracklets)
    assert len(tracklets) > 0
    # Each tracklet should have records
    for t in tracklets:
        assert len(t.records) > 0
        assert all(isinstance(r, DetectionRecord) for r in t.records)


def test_botsort_returns_tracklets():
    tracker = MOTTracker(method="botsort", frame_rate=30)
    records = _make_sequence()
    tracklets = tracker.track(records)

    assert isinstance(tracklets, list)
    assert all(isinstance(t, Tracklet) for t in tracklets)
    assert len(tracklets) > 0
    for t in tracklets:
        assert len(t.records) > 0


def test_botsort_without_reid():
    tracker = MOTTracker(method="botsort", frame_rate=30, with_reid=False)
    records = _make_sequence()
    tracklets = tracker.track(records)

    assert isinstance(tracklets, list)
    assert len(tracklets) > 0


def test_empty_input():
    tracker = MOTTracker(method="bytetrack")
    tracklets = tracker.track([])
    assert tracklets == []


def test_single_frame():
    tracker = MOTTracker(method="bytetrack")
    records = [_make_record("0", 100, 100, 200, 200)]
    tracklets = tracker.track(records)
    assert isinstance(tracklets, list)


def test_reset():
    tracker = MOTTracker(method="botsort")
    records = _make_sequence()
    tracker.track(records)
    tracker.reset()
    # After reset, tracking again should work fresh
    tracklets = tracker.track(records)
    assert isinstance(tracklets, list)
    assert len(tracklets) > 0


def test_tracklet_ids_are_strings():
    tracker = MOTTracker(method="bytetrack")
    records = _make_sequence()
    tracklets = tracker.track(records)
    for t in tracklets:
        assert isinstance(t.id, str)


def test_two_objects_tracked_separately():
    """With 2 well-separated objects, we should get at least 2 tracklets."""
    tracker = MOTTracker(method="bytetrack", frame_rate=30)
    records = _make_sequence()
    tracklets = tracker.track(records)
    assert len(tracklets) >= 2
