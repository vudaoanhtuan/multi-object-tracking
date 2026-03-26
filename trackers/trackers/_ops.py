"""Utility functions extracted from ultralytics (pure numpy, no torch dependency)."""

from __future__ import annotations

import numpy as np


def xywh2ltwh(x: np.ndarray) -> np.ndarray:
    """Convert bounding box format from [x, y, w, h] to [x1, y1, w, h] where x1, y1 are top-left coordinates."""
    y = np.copy(x)
    y[..., 0] = x[..., 0] - x[..., 2] / 2  # top left x
    y[..., 1] = x[..., 1] - x[..., 3] / 2  # top left y
    return y


def bbox_ioa(box1: np.ndarray, box2: np.ndarray, iou: bool = False, eps: float = 1e-7) -> np.ndarray:
    """Calculate the intersection over box2 area given box1 and box2.

    Args:
        box1: A numpy array of shape (N, 4) representing N bounding boxes in x1y1x2y2 format.
        box2: A numpy array of shape (M, 4) representing M bounding boxes in x1y1x2y2 format.
        iou: Calculate the standard IoU if True else return inter_area/box2_area.
        eps: A small value to avoid division by zero.

    Returns:
        A numpy array of shape (N, M) representing the intersection over box2 area.
    """
    b1_x1, b1_y1, b1_x2, b1_y2 = box1.T
    b2_x1, b2_y1, b2_x2, b2_y2 = box2.T

    inter_area = (np.minimum(b1_x2[:, None], b2_x2) - np.maximum(b1_x1[:, None], b2_x1)).clip(0) * (
        np.minimum(b1_y2[:, None], b2_y2) - np.maximum(b1_y1[:, None], b2_y1)
    ).clip(0)

    area = (b2_x2 - b2_x1) * (b2_y2 - b2_y1)
    if iou:
        box1_area = (b1_x2 - b1_x1) * (b1_y2 - b1_y1)
        area = area + box1_area[:, None] - inter_area

    return inter_area / (area + eps)
