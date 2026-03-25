from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QColor, QIcon, QPixmap
from PyQt6.QtWidgets import (
    QComboBox,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from mot_va.models.project import Project
from mot_va.models.sample import Sample
from mot_va.views.panels.object_list import ObjectListPanel


class SampleBrowser(QWidget):
    """Left panel: sample/frame browser + object list (stacked vertically)."""

    frame_selected = pyqtSignal(int, int)  # sample_index, frame_index

    def __init__(self) -> None:
        super().__init__()
        self._project: Project | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        # Sample selector
        layout.addWidget(QLabel("Sample:"))
        self._sample_combo = QComboBox()
        self._sample_combo.currentIndexChanged.connect(self._on_sample_changed)
        layout.addWidget(self._sample_combo)

        # Vertical splitter: frames on top, objects on bottom
        splitter = QSplitter()
        splitter.setOrientation(splitter.orientation())  # default vertical
        from PyQt6.QtCore import Qt
        splitter.setOrientation(Qt.Orientation.Vertical)

        # Frames section
        frames_widget = QWidget()
        frames_layout = QVBoxLayout(frames_widget)
        frames_layout.setContentsMargins(0, 0, 0, 0)
        frames_layout.addWidget(QLabel("Frames:"))
        self._frame_list = QListWidget()
        self._frame_list.currentRowChanged.connect(self._on_frame_changed)
        frames_layout.addWidget(self._frame_list)
        splitter.addWidget(frames_widget)

        # Object list section
        self.object_list = ObjectListPanel()
        splitter.addWidget(self.object_list)

        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        layout.addWidget(splitter)

    def set_project(self, project: Project) -> None:
        """Populate the browser with a scanned project."""
        self._project = project
        self._sample_combo.blockSignals(True)
        self._sample_combo.clear()
        for sample in project.samples:
            self._sample_combo.addItem(sample.sample_id)
        self._sample_combo.blockSignals(False)

        if project.samples:
            self._sample_combo.setCurrentIndex(0)
            self._populate_frames(project.samples[0])

    def _populate_frames(self, sample: Sample) -> None:
        self._frame_list.blockSignals(True)
        self._frame_list.clear()
        for frame in sample.frames:
            item = QListWidgetItem(frame.frame_id)
            if frame.label_path.exists():
                px = QPixmap(8, 8)
                px.fill(QColor(60, 180, 75))
                item.setIcon(QIcon(px))
            self._frame_list.addItem(item)
        self._frame_list.blockSignals(False)

        if sample.frames:
            self._frame_list.setCurrentRow(0)

    def _on_sample_changed(self, index: int) -> None:
        if self._project and 0 <= index < len(self._project.samples):
            self._populate_frames(self._project.samples[index])

    def _on_frame_changed(self, row: int) -> None:
        sample_idx = self._sample_combo.currentIndex()
        if sample_idx >= 0 and row >= 0:
            self.frame_selected.emit(sample_idx, row)

    def select_frame(self, frame_index: int) -> None:
        """Programmatically select a frame by index."""
        self._frame_list.blockSignals(True)
        self._frame_list.setCurrentRow(frame_index)
        self._frame_list.blockSignals(False)

    def current_sample_index(self) -> int:
        return self._sample_combo.currentIndex()

    def refresh_frame_indicators(self) -> None:
        """Refresh the label-exists indicators for the current sample."""
        sample_idx = self._sample_combo.currentIndex()
        if not self._project or sample_idx < 0:
            return
        sample = self._project.samples[sample_idx]
        for i, frame in enumerate(sample.frames):
            item = self._frame_list.item(i)
            if item and frame.label_path.exists():
                px = QPixmap(8, 8)
                px.fill(QColor(60, 180, 75))
                item.setIcon(QIcon(px))
