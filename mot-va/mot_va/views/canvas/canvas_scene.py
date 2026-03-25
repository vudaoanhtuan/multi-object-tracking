from PyQt6.QtCore import QPointF, QRectF, Qt, pyqtSignal
from PyQt6.QtGui import QBrush, QColor, QPen, QPixmap
from PyQt6.QtWidgets import (
    QGraphicsPixmapItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsSceneMouseEvent,
)

from mot_va.models.bbox import BoundingBox
from mot_va.models.frame import Frame
from mot_va.services import color_registry
from mot_va.views.canvas.bbox_item import BBoxItem


class CanvasScene(QGraphicsScene):
    """Scene holding the frame image and bounding box items."""

    bbox_drawn = pyqtSignal(QRectF)
    bbox_selected_signal = pyqtSignal(int)  # index of selected bbox

    def __init__(self) -> None:
        super().__init__()
        self._pixmap_item: QGraphicsPixmapItem | None = None
        self._bbox_items: list[BBoxItem] = []
        self._drawing = False
        self._draw_mode = False
        self._draw_start: QPointF | None = None
        self._rubber_band: QGraphicsRectItem | None = None

    @property
    def bbox_items(self) -> list[BBoxItem]:
        return self._bbox_items

    def set_frame(self, frame: Frame, pixmap: QPixmap) -> None:
        """Display a frame image and its bounding boxes."""
        self.clear()
        self._bbox_items.clear()

        self._pixmap_item = self.addPixmap(pixmap)
        self._pixmap_item.setZValue(-1)
        self.setSceneRect(QRectF(pixmap.rect().toRectF()))

        for i, bbox in enumerate(frame.bboxes):
            color = color_registry.get_color(bbox.object_id)
            item = BBoxItem(bbox, color, i)
            self.addItem(item)
            self._bbox_items.append(item)

    def set_draw_mode(self, enabled: bool) -> None:
        """Enable or disable bbox drawing mode."""
        self._draw_mode = enabled

    def set_editable(self, editable: bool) -> None:
        """Enable or disable editing on all bbox items."""
        for item in self._bbox_items:
            item.set_editable(editable)

    def add_bbox_item(self, bbox: BoundingBox) -> BBoxItem:
        """Add a new bbox item to the scene."""
        index = len(self._bbox_items)
        color = color_registry.get_color(bbox.object_id)
        item = BBoxItem(bbox, color, index)
        self.addItem(item)
        self._bbox_items.append(item)
        return item

    def remove_bbox_item(self, index: int) -> None:
        """Remove a bbox item by index."""
        if 0 <= index < len(self._bbox_items):
            item = self._bbox_items.pop(index)
            self.removeItem(item)
            # Re-index remaining items
            for i, it in enumerate(self._bbox_items):
                it.index = i

    def selected_bbox_index(self) -> int | None:
        """Return the index of the currently selected bbox, or None."""
        for item in self._bbox_items:
            if item.isSelected():
                return item.index
        return None

    def select_bbox(self, index: int) -> None:
        """Programmatically select a bbox by index."""
        self.clearSelection()
        if 0 <= index < len(self._bbox_items):
            self._bbox_items[index].setSelected(True)

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        if self._draw_mode and event.button() == Qt.MouseButton.LeftButton:
            self._drawing = True
            self._draw_start = event.scenePos()
            self._rubber_band = QGraphicsRectItem()
            self._rubber_band.setPen(QPen(QColor(255, 255, 0), 2, Qt.PenStyle.DashLine))
            self._rubber_band.setBrush(QBrush(QColor(255, 255, 0, 30)))
            self.addItem(self._rubber_band)
            return

        super().mousePressEvent(event)

        # Emit selection signal
        for item in self._bbox_items:
            if item.isSelected():
                self.bbox_selected_signal.emit(item.index)
                return

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        if self._drawing and self._draw_start and self._rubber_band:
            rect = QRectF(self._draw_start, event.scenePos()).normalized()
            self._rubber_band.setRect(rect)
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        if self._drawing and self._rubber_band:
            rect = self._rubber_band.rect()
            self.removeItem(self._rubber_band)
            self._rubber_band = None
            self._drawing = False
            self._draw_start = None

            # Only emit if rect has meaningful size
            if rect.width() > 5 and rect.height() > 5:
                self.bbox_drawn.emit(rect)
            return
        super().mouseReleaseEvent(event)
