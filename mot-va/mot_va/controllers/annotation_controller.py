from PyQt6.QtCore import QObject, QRectF, pyqtSignal

from mot_va.models.bbox import BoundingBox
from mot_va.models.frame import Frame
from mot_va.services.file_io import write_mot_labels
from mot_va.views.canvas.canvas_scene import CanvasScene
from mot_va.views.dialogs.object_id_dialog import ObjectIdDialog


class AnnotationController(QObject):
    """Orchestrates annotation mode operations: draw, move, delete, save."""

    dirty_changed = pyqtSignal(bool)
    bboxes_updated = pyqtSignal()  # signals that the bbox list changed
    draw_mode_changed = pyqtSignal(bool)  # sync draw button state

    def __init__(self, scene: CanvasScene) -> None:
        super().__init__()
        self._scene = scene
        self._current_frame: Frame | None = None
        self._annotation_mode = False

        self._scene.bbox_drawn.connect(self._on_bbox_drawn)

    def set_frame(self, frame: Frame) -> None:
        self._current_frame = frame

    def set_annotation_mode(self, enabled: bool) -> None:
        self._annotation_mode = enabled
        self._scene.set_draw_mode(False)
        self.draw_mode_changed.emit(False)
        self._scene.set_editable(enabled)

    def set_draw_mode(self, enabled: bool) -> None:
        """Set draw mode (called from toolbar button)."""
        if enabled and not self._annotation_mode:
            return
        self._scene.set_draw_mode(enabled)

    def enter_draw_mode(self) -> None:
        """Enter bbox drawing mode (hotkey A)."""
        if self._annotation_mode:
            self._scene.set_draw_mode(True)
            self.draw_mode_changed.emit(True)

    def exit_draw_mode(self) -> None:
        """Exit bbox drawing mode."""
        self._scene.set_draw_mode(False)
        self.draw_mode_changed.emit(False)

    def _on_bbox_drawn(self, rect: QRectF) -> None:
        """Handle a newly drawn bounding box rectangle."""
        if not self._current_frame:
            return

        # Exit draw mode after drawing
        self._scene.set_draw_mode(False)
        self.draw_mode_changed.emit(False)

        # Collect existing IDs
        existing_ids = list({b.object_id for b in self._current_frame.bboxes})

        dialog = ObjectIdDialog(existing_ids)
        dialog.exec()
        obj_id = dialog.selected_id()

        if obj_id is None:
            return  # Cancelled

        bbox = BoundingBox(
            object_id=obj_id,
            x_min=int(rect.x()),
            y_min=int(rect.y()),
            x_max=int(rect.x() + rect.width()),
            y_max=int(rect.y() + rect.height()),
        )
        self._current_frame.bboxes.append(bbox)
        item = self._scene.add_bbox_item(bbox)
        item.set_editable(True)
        self.dirty_changed.emit(True)
        self.bboxes_updated.emit()

    def delete_selected(self) -> None:
        """Delete the currently selected bbox."""
        if not self._current_frame or not self._annotation_mode:
            return

        index = self._scene.selected_bbox_index()
        if index is None:
            return

        self._current_frame.bboxes.pop(index)
        self._scene.remove_bbox_item(index)
        self.dirty_changed.emit(True)
        self.bboxes_updated.emit()

    def change_object_id(self, index: int) -> None:
        """Change the object ID of a bbox at the given index."""
        if not self._current_frame or not self._annotation_mode:
            return
        if index < 0 or index >= len(self._current_frame.bboxes):
            return

        existing_ids = list({b.object_id for b in self._current_frame.bboxes})
        dialog = ObjectIdDialog(existing_ids)
        dialog.exec()
        new_id = dialog.selected_id()

        if new_id is None:
            return

        self._current_frame.bboxes[index].object_id = new_id
        # Refresh the scene to show updated color
        self._refresh_scene()
        self.dirty_changed.emit(True)
        self.bboxes_updated.emit()

    def save(self) -> bool:
        """Save current frame labels to disk. Returns True if saved."""
        if not self._current_frame:
            return False

        # Sync positions from moved items
        for item in self._scene.bbox_items:
            item.sync_bbox_from_pos()

        write_mot_labels(
            self._current_frame.label_path,
            self._current_frame.bboxes,
        )
        self.dirty_changed.emit(False)
        return True

    def discard(self) -> None:
        """Discard changes by reloading labels from disk."""
        if not self._current_frame:
            return
        from mot_va.services.file_io import read_mot_labels
        self._current_frame.bboxes = read_mot_labels(self._current_frame.label_path)
        self._refresh_scene()
        self.dirty_changed.emit(False)
        self.bboxes_updated.emit()

    def on_bbox_moved(self) -> None:
        """Called when a bbox item has been moved on the canvas."""
        self.dirty_changed.emit(True)

    def _refresh_scene(self) -> None:
        """Rebuild bbox items from the current frame model."""
        if not self._current_frame:
            return
        # Remove all existing bbox items
        for item in list(self._scene.bbox_items):
            self._scene.removeItem(item)
        self._scene._bbox_items.clear()

        # Re-add from model
        for bbox in self._current_frame.bboxes:
            item = self._scene.add_bbox_item(bbox)
            if self._annotation_mode:
                item.set_editable(True)
