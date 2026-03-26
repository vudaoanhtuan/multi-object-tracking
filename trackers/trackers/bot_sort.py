"""BOTSORT: Extended BYTETracker with ReID and GMC support."""

from __future__ import annotations

from collections import deque
from typing import Any

import numpy as np

from .basetrack import TrackState
from .byte_tracker import BYTETracker, STrack
from .utils import matching
from .utils.gmc import GMC
from .utils.kalman_filter import KalmanFilterXYWH


class BOTrack(STrack):
    """Extended STrack with feature smoothing for ReID-based tracking.

    Attributes:
        shared_kalman (KalmanFilterXYWH): A shared Kalman filter for all instances.
        smooth_feat (np.ndarray): Smoothed feature vector.
        curr_feat (np.ndarray): Current feature vector.
        features (deque): Feature vector history.
        alpha (float): Smoothing factor for exponential moving average of features.
    """

    shared_kalman = KalmanFilterXYWH()

    def __init__(
        self, xywh: np.ndarray, score: float, cls: int, feat: np.ndarray | None = None, feat_history: int = 50
    ):
        """Initialize a BOTrack object with temporal parameters.

        Args:
            xywh: Bounding box in (x, y, w, h, idx) format.
            score: Confidence score of the detection.
            cls: Class ID of the detected object.
            feat: Feature vector associated with the detection.
            feat_history: Maximum length of the feature history deque.
        """
        super().__init__(xywh, score, cls)

        self.smooth_feat = None
        self.curr_feat = None
        if feat is not None:
            self.update_features(feat)
        self.features = deque(maxlen=feat_history)
        self.alpha = 0.9

    def update_features(self, feat: np.ndarray) -> None:
        """Update the feature vector and apply exponential moving average smoothing."""
        feat /= np.linalg.norm(feat)
        self.curr_feat = feat
        if self.smooth_feat is None:
            self.smooth_feat = feat
        else:
            self.smooth_feat = self.alpha * self.smooth_feat + (1 - self.alpha) * feat
        self.features.append(feat)
        self.smooth_feat /= np.linalg.norm(self.smooth_feat)

    def predict(self) -> None:
        """Predict the object's future state using the Kalman filter."""
        mean_state = self.mean.copy()
        if self.state != TrackState.Tracked:
            mean_state[6] = 0
            mean_state[7] = 0

        self.mean, self.covariance = self.kalman_filter.predict(mean_state, self.covariance)

    def re_activate(self, new_track: BOTrack, frame_id: int, new_id: bool = False) -> None:
        """Reactivate a track with updated features and optionally assign a new ID."""
        if new_track.curr_feat is not None:
            self.update_features(new_track.curr_feat)
        super().re_activate(new_track, frame_id, new_id)

    def update(self, new_track: BOTrack, frame_id: int) -> None:
        """Update the track with new detection information and the current frame ID."""
        if new_track.curr_feat is not None:
            self.update_features(new_track.curr_feat)
        super().update(new_track, frame_id)

    @property
    def tlwh(self) -> np.ndarray:
        """Return the current bounding box position in (top left x, top left y, width, height) format."""
        if self.mean is None:
            return self._tlwh.copy()
        ret = self.mean[:4].copy()
        ret[:2] -= ret[2:] / 2
        return ret

    @staticmethod
    def multi_predict(stracks: list[BOTrack]) -> None:
        """Predict the mean and covariance for multiple object tracks using a shared Kalman filter."""
        if len(stracks) <= 0:
            return
        multi_mean = np.asarray([st.mean.copy() for st in stracks])
        multi_covariance = np.asarray([st.covariance for st in stracks])
        for i, st in enumerate(stracks):
            if st.state != TrackState.Tracked:
                multi_mean[i][6] = 0
                multi_mean[i][7] = 0
        multi_mean, multi_covariance = BOTrack.shared_kalman.multi_predict(multi_mean, multi_covariance)
        for i, (mean, cov) in enumerate(zip(multi_mean, multi_covariance)):
            stracks[i].mean = mean
            stracks[i].covariance = cov

    def convert_coords(self, tlwh: np.ndarray) -> np.ndarray:
        """Convert tlwh bounding box coordinates to xywh format."""
        return self.tlwh_to_xywh(tlwh)

    @staticmethod
    def tlwh_to_xywh(tlwh: np.ndarray) -> np.ndarray:
        """Convert bounding box from tlwh to xywh (center-x, center-y, width, height) format."""
        ret = np.asarray(tlwh).copy()
        ret[:2] += ret[2:] / 2
        return ret


class BOTSORT(BYTETracker):
    """Extended BYTETracker with ReID and GMC support.

    Attributes:
        proximity_thresh (float): Threshold for spatial proximity (IoU) between tracks and detections.
        appearance_thresh (float): Threshold for appearance similarity (ReID embeddings).
        gmc (GMC): An instance of the GMC algorithm for data association.
    """

    def __init__(self, args: Any, frame_rate: int = 30):
        """Initialize BOTSORT with GMC algorithm.

        Args:
            args: Namespace-like object containing tracking parameters.
            frame_rate: Frame rate of the video being processed.
        """
        super().__init__(args, frame_rate)
        self.gmc = GMC(method=args.gmc_method)

        self.proximity_thresh = args.proximity_thresh
        self.appearance_thresh = args.appearance_thresh

    def get_kalmanfilter(self) -> KalmanFilterXYWH:
        """Return an instance of KalmanFilterXYWH for tracking."""
        return KalmanFilterXYWH()

    def init_track(self, results, feats: np.ndarray | None = None) -> list[BOTrack]:
        """Initialize object tracks using detection results and optional ReID features.

        Args:
            results: Detection results with .xywh, .conf, .cls attributes.
            feats: Optional feature vectors, either as a numpy array of shape (N, D)
                or a list of numpy arrays.
        """
        if len(results) == 0:
            return []
        bboxes = results.xywh
        bboxes = np.concatenate([bboxes, np.arange(len(bboxes)).reshape(-1, 1)], axis=-1)
        if self.args.with_reid and feats is not None:
            feat_list = feats if isinstance(feats, list) else [feats[i] for i in range(len(feats))]
            return [BOTrack(xywh, s, c, f) for (xywh, s, c, f) in zip(bboxes, results.conf, results.cls, feat_list)]
        else:
            return [BOTrack(xywh, s, c) for (xywh, s, c) in zip(bboxes, results.conf, results.cls)]

    def get_dists(self, tracks: list[BOTrack], detections: list[BOTrack]) -> np.ndarray:
        """Calculate distances between tracks and detections using IoU and optionally ReID embeddings."""
        dists = matching.iou_distance(tracks, detections)
        dists_mask = dists > (1 - self.proximity_thresh)

        if self.args.fuse_score:
            dists = matching.fuse_score(dists, detections)

        if self.args.with_reid:
            emb_dists = matching.embedding_distance(tracks, detections) / 2.0
            emb_dists[emb_dists > (1 - self.appearance_thresh)] = 1.0
            emb_dists[dists_mask] = 1.0
            dists = np.minimum(dists, emb_dists)
        return dists

    def multi_predict(self, tracks: list[BOTrack]) -> None:
        """Predict the mean and covariance of multiple object tracks."""
        BOTrack.multi_predict(tracks)

    def reset(self) -> None:
        """Reset the BOTSORT tracker to its initial state."""
        super().reset()
        self.gmc.reset_params()
