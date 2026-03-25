from pathlib import Path

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QMessageBox

from mot_va.models.frame import Frame
from mot_va.models.project import Project
from mot_va.services.dataset_scanner import scan_dataset
from mot_va.services.file_io import read_mot_labels


class NavigationController(QObject):
    """Controls dataset loading, frame navigation, and dirty state."""

    frame_changed = pyqtSignal(Frame, QPixmap)
    project_loaded = pyqtSignal(Project)
    dirty_changed = pyqtSignal(bool)

    def __init__(self) -> None:
        super().__init__()
        self._project: Project | None = None
        self._sample_index = -1
        self._frame_index = -1
        self._dirty = False

    @property
    def project(self) -> Project | None:
        return self._project

    @property
    def sample_index(self) -> int:
        return self._sample_index

    @property
    def frame_index(self) -> int:
        return self._frame_index

    @property
    def dirty(self) -> bool:
        return self._dirty

    def set_dirty(self, dirty: bool) -> None:
        if self._dirty != dirty:
            self._dirty = dirty
            self.dirty_changed.emit(dirty)

    def current_frame(self) -> Frame | None:
        if not self._project:
            return None
        if self._sample_index < 0 or self._frame_index < 0:
            return None
        sample = self._project.samples[self._sample_index]
        return sample.frames[self._frame_index]

    def open_dataset(self, root: Path) -> None:
        """Scan and load a dataset directory."""
        project = scan_dataset(root)
        self._project = project
        self._sample_index = -1
        self._frame_index = -1
        self._dirty = False
        self.project_loaded.emit(project)

    def on_frame_selected(self, sample_index: int, frame_index: int) -> None:
        """Handle frame selection from the browser."""
        if not self._project:
            return

        # Check dirty state before switching
        if self._dirty and not self._confirm_discard():
            return

        self._sample_index = sample_index
        self._frame_index = frame_index
        self.set_dirty(False)

        sample = self._project.samples[sample_index]
        frame = sample.frames[frame_index]

        # Lazy load labels
        if not frame.labels_loaded:
            frame.bboxes = read_mot_labels(frame.label_path)
            frame.labels_loaded = True

        pixmap = QPixmap(str(frame.image_path))
        self.frame_changed.emit(frame, pixmap)

    def go_next(self) -> int | None:
        """Navigate to next frame. Returns new frame index or None."""
        if not self._project or self._sample_index < 0:
            return None
        sample = self._project.samples[self._sample_index]
        if self._frame_index < len(sample.frames) - 1:
            new_idx = self._frame_index + 1
            self.on_frame_selected(self._sample_index, new_idx)
            return new_idx
        return None

    def go_prev(self) -> int | None:
        """Navigate to previous frame. Returns new frame index or None."""
        if not self._project or self._sample_index < 0:
            return None
        if self._frame_index > 0:
            new_idx = self._frame_index - 1
            self.on_frame_selected(self._sample_index, new_idx)
            return new_idx
        return None

    def _confirm_discard(self) -> bool:
        """Ask user whether to discard unsaved changes."""
        result = QMessageBox.question(
            None,  # type: ignore[arg-type]
            "Unsaved Changes",
            "You have unsaved changes. Discard them?",
            QMessageBox.StandardButton.Save
            | QMessageBox.StandardButton.Discard
            | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel,
        )
        if result == QMessageBox.StandardButton.Save:
            # Caller should save first — we emit a signal
            return False  # Don't navigate yet
        return result == QMessageBox.StandardButton.Discard
