from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence, QPixmap, QShortcut
from PyQt6.QtWidgets import (
    QFileDialog,
    QMainWindow,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from mot_va.controllers.annotation_controller import AnnotationController
from mot_va.controllers.navigation_controller import NavigationController
from mot_va.models.frame import Frame
from mot_va.models.project import Project
from mot_va.views.canvas.canvas_scene import CanvasScene
from mot_va.views.canvas.canvas_view import CanvasView
from mot_va.views.panels.sample_browser import SampleBrowser
from mot_va.views.panels.toolbar import ToolBar


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        # --- Create components ---
        self._toolbar = ToolBar()
        self._sample_browser = SampleBrowser()
        self._scene = CanvasScene()
        self._canvas_view = CanvasView(self._scene)

        # Object list is now inside sample_browser
        self._object_list = self._sample_browser.object_list

        # --- Controllers ---
        self._nav = NavigationController()
        self._annotation = AnnotationController(self._scene)

        # --- Layout ---
        self.addToolBar(self._toolbar)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Two-panel: left sidebar + canvas (maximized)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        self._sample_browser.setMinimumWidth(200)
        self._sample_browser.setMaximumWidth(350)
        splitter.addWidget(self._sample_browser)
        splitter.addWidget(self._canvas_view)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        layout.addWidget(splitter)

        # --- Wire signals ---
        self._wire_signals()
        self._setup_shortcuts()
        
        # Sync initial mode
        self._on_mode_changed(self._toolbar.current_mode())

    def _wire_signals(self) -> None:
        # Toolbar
        self._toolbar.open_requested.connect(self._on_open)
        self._toolbar.save_requested.connect(self._on_save)
        self._toolbar.discard_requested.connect(self._on_discard)
        self._toolbar.mode_changed.connect(self._on_mode_changed)
        self._toolbar.prev_frame.connect(self._on_prev_frame)
        self._toolbar.next_frame.connect(self._on_next_frame)
        self._toolbar.zoom_in_requested.connect(self._canvas_view.zoom_in)
        self._toolbar.zoom_out_requested.connect(self._canvas_view.zoom_out)

        # Navigation
        self._nav.project_loaded.connect(self._on_project_loaded)
        self._nav.frame_changed.connect(self._on_frame_changed)
        self._nav.dirty_changed.connect(self._toolbar.set_dirty)
        self._nav.navigation_cancelled.connect(
            lambda _si, fi: self._sample_browser.select_frame(fi)
        )
        self._nav.set_discard_callback(self._annotation.discard)
        self._nav.set_save_callback(lambda: self._annotation.save())

        # Auto-save wiring
        self._toolbar.auto_save_toggled.connect(self._annotation.set_auto_save)
        self._toolbar.auto_save_toggled.connect(self._nav.set_auto_save)

        # Sample browser
        self._sample_browser.frame_selected.connect(self._nav.on_frame_selected)

        # Annotation controller
        self._annotation.dirty_changed.connect(self._nav.set_dirty)
        self._annotation.bboxes_updated.connect(self._refresh_object_list)
        self._annotation.draw_mode_changed.connect(self._toolbar.set_draw_active)
        self._annotation.draw_mode_changed.connect(self._canvas_view.set_draw_mode)

        # Draw button -> annotation + canvas
        self._toolbar.draw_mode_toggled.connect(self._annotation.set_draw_mode)
        self._toolbar.draw_mode_toggled.connect(self._canvas_view.set_draw_mode)

        # Canvas selection -> object list
        self._scene.bbox_selected_signal.connect(self._object_list.select_object)

        # Object list -> canvas
        self._object_list.object_selected.connect(self._scene.select_bbox)
        self._object_list.delete_requested.connect(self._on_delete_bbox)
        self._object_list.change_id_requested.connect(self._annotation.change_object_id)

    def _setup_shortcuts(self) -> None:
        # Ctrl+S: Save
        QShortcut(QKeySequence.StandardKey.Save, self).activated.connect(
            self._on_save
        )
        # Zoom Out/In (Ctrl+- / Ctrl++)
        QShortcut(QKeySequence.StandardKey.ZoomIn, self).activated.connect(
            self._canvas_view.zoom_in
        )
        QShortcut(QKeySequence.StandardKey.ZoomOut, self).activated.connect(
            self._canvas_view.zoom_out
        )
        # Left arrow: previous frame
        QShortcut(QKeySequence(Qt.Key.Key_Left), self).activated.connect(
            self._on_prev_frame
        )
        # Right arrow: next frame
        QShortcut(QKeySequence(Qt.Key.Key_Right), self).activated.connect(
            self._on_next_frame
        )
        # A: enter draw mode
        QShortcut(QKeySequence(Qt.Key.Key_A), self).activated.connect(
            self._annotation.enter_draw_mode
        )
        # Escape: exit draw mode
        QShortcut(QKeySequence(Qt.Key.Key_Escape), self).activated.connect(
            self._annotation.exit_draw_mode
        )
        # Delete: remove selected bbox
        QShortcut(QKeySequence(Qt.Key.Key_Delete), self).activated.connect(
            self._annotation.delete_selected
        )
        # Backspace also deletes (macOS)
        QShortcut(QKeySequence(Qt.Key.Key_Backspace), self).activated.connect(
            self._annotation.delete_selected
        )

    # --- Slots ---

    def _on_open(self) -> None:
        path = QFileDialog.getExistingDirectory(
            self, "Open Dataset Directory"
        )
        if path:
            from pathlib import Path
            self._nav.open_dataset(Path(path))

    def _on_project_loaded(self, project: Project) -> None:
        self._sample_browser.set_project(project)
        self._annotation.set_project(project)
        self.setWindowTitle(
            f"MOT Visualization & Annotation - {project.root_dir.name}"
        )

    def _on_frame_changed(self, frame: Frame, pixmap: QPixmap) -> None:
        sample_idx = self._nav.sample_index
        frame_idx = self._nav.frame_index

        self._scene.set_frame(frame, pixmap)
        self._annotation.set_frame(frame, sample_idx, frame_idx)
        self._object_list.set_bboxes(frame.bboxes)

        # Fit image to canvas
        self._canvas_view.fit_to_scene()

        # Apply current mode to new frame
        mode = self._toolbar.current_mode()
        is_edit = mode == "edit"
        self._scene.set_editable(is_edit)
        self._object_list.set_editing_enabled(is_edit)

        # Update frame label
        sample_idx = self._nav.sample_index
        frame_idx = self._nav.frame_index
        if self._nav.project and sample_idx >= 0:
            sample = self._nav.project.samples[sample_idx]
            total = len(sample.frames)
            self._toolbar.set_frame_label(
                f"{frame.frame_id} ({frame_idx + 1}/{total})"
            )

    def _on_mode_changed(self, mode: str) -> None:
        is_edit = mode == "edit"
        self._annotation.set_annotation_mode(is_edit)
        self._object_list.set_editing_enabled(is_edit)
        self._canvas_view.set_draw_mode(False)

    def _on_save(self) -> None:
        if self._annotation.save():
            self._sample_browser.refresh_frame_indicators()

    def _on_discard(self) -> None:
        self._annotation.discard()

    def _on_prev_frame(self) -> None:
        new_idx = self._nav.go_prev()
        if new_idx is not None:
            self._sample_browser.select_frame(new_idx)

    def _on_next_frame(self) -> None:
        new_idx = self._nav.go_next()
        if new_idx is not None:
            self._sample_browser.select_frame(new_idx)

    def _on_delete_bbox(self, index: int) -> None:
        """Delete bbox triggered from the object list panel."""
        self._scene.select_bbox(index)
        self._annotation.delete_selected()

    def _refresh_object_list(self) -> None:
        frame = self._nav.current_frame()
        if frame:
            self._object_list.set_bboxes(frame.bboxes)
