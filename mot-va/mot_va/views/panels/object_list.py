from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from mot_va.models.bbox import BoundingBox
from mot_va.services import color_registry


class ObjectListPanel(QWidget):
    """Right panel: list of objects in the current frame."""

    object_selected = pyqtSignal(int)  # bbox index
    delete_requested = pyqtSignal(int)  # bbox index
    change_id_requested = pyqtSignal(int)  # bbox index

    def __init__(self) -> None:
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        layout.addWidget(QLabel("Objects in Frame:"))

        self._list = QListWidget()
        self._list.currentRowChanged.connect(self._on_selection_changed)
        layout.addWidget(self._list)

        btn_layout = QHBoxLayout()
        self._change_id_btn = QPushButton("Change ID")
        self._change_id_btn.clicked.connect(self._on_change_id)
        self._change_id_btn.setEnabled(False)
        btn_layout.addWidget(self._change_id_btn)

        self._delete_btn = QPushButton("Delete")
        self._delete_btn.clicked.connect(self._on_delete)
        self._delete_btn.setEnabled(False)
        btn_layout.addWidget(self._delete_btn)

        layout.addLayout(btn_layout)

        self._editing_enabled = False

    def set_bboxes(self, bboxes: list[BoundingBox]) -> None:
        """Populate the list with bounding boxes."""
        self._list.blockSignals(True)
        self._list.clear()
        for bbox in bboxes:
            color = color_registry.get_color(bbox.object_id)
            px = QPixmap(12, 12)
            px.fill(color)

            text = f"ID: {bbox.object_id}  [{bbox.x_min}, {bbox.y_min}, {bbox.x_max}, {bbox.y_max}]"
            item = QListWidgetItem(QIcon(px), text)
            self._list.addItem(item)
        self._list.blockSignals(False)

    def set_editing_enabled(self, enabled: bool) -> None:
        """Enable or disable editing buttons."""
        self._editing_enabled = enabled
        has_selection = self._list.currentRow() >= 0
        self._change_id_btn.setEnabled(enabled and has_selection)
        self._delete_btn.setEnabled(enabled and has_selection)

    def select_object(self, index: int) -> None:
        """Programmatically select an object by index."""
        self._list.blockSignals(True)
        self._list.setCurrentRow(index)
        self._list.blockSignals(False)
        self._update_buttons()

    def _on_selection_changed(self, row: int) -> None:
        self._update_buttons()
        if row >= 0:
            self.object_selected.emit(row)

    def _update_buttons(self) -> None:
        has_selection = self._list.currentRow() >= 0
        self._change_id_btn.setEnabled(self._editing_enabled and has_selection)
        self._delete_btn.setEnabled(self._editing_enabled and has_selection)

    def _on_delete(self) -> None:
        row = self._list.currentRow()
        if row >= 0:
            self.delete_requested.emit(row)

    def _on_change_id(self) -> None:
        row = self._list.currentRow()
        if row >= 0:
            self.change_id_requested.emit(row)
