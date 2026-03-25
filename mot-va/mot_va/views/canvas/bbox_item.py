from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QBrush, QColor, QFont, QPainter, QPen
from PyQt6.QtWidgets import (
    QGraphicsRectItem,
    QGraphicsSceneHoverEvent,
    QGraphicsSceneMouseEvent,
    QStyleOptionGraphicsItem,
    QWidget,
)

from mot_va.models.bbox import BoundingBox

_GRAB_MARGIN = 6.0

class BBoxItem(QGraphicsRectItem):
    """Visual representation of a single bounding box on the canvas."""

    def __init__(
        self,
        bbox: BoundingBox,
        color: QColor,
        index: int,
    ) -> None:
        super().__init__(
            QRectF(bbox.x_min, bbox.y_min, bbox.width, bbox.height)
        )
        self.bbox = bbox
        self.color = color
        self.index = index

        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable, False)
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable, False)
        self.setAcceptHoverEvents(True)
        self._resize_mode: str | None = None
        self.on_moved_callback = None

        # Fill with semi-transparent color
        fill = QColor(color)
        fill.setAlpha(38)  # ~15%
        self.setBrush(QBrush(fill))

        # Border
        self.setPen(QPen(color, 2))

    def set_editable(self, editable: bool) -> None:
        """Enable or disable selection and movement."""
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable, editable)
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable, editable)
        if editable:
            self.setFlag(
                QGraphicsRectItem.GraphicsItemFlag.ItemSendsGeometryChanges, True
            )

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionGraphicsItem,
        widget: QWidget | None = None,
    ) -> None:
        # Draw fill
        painter.setBrush(self.brush())

        # Adjust pen for selection state
        if self.isSelected():
            pen = QPen(self.color, 3, Qt.PenStyle.DashLine)
        else:
            pen = QPen(self.color, 2)

        painter.setPen(pen)
        painter.drawRect(self.rect())

        # Draw ID label above top-left corner
        label = str(self.bbox.object_id)
        font = QFont("Sans", 15)
        font.setBold(True)
        painter.setFont(font)

        metrics = painter.fontMetrics()
        text_width = metrics.horizontalAdvance(label) + 6
        text_height = metrics.height() + 2

        label_rect = QRectF(
            self.rect().x(),
            self.rect().y() - text_height,
            text_width,
            text_height,
        )

        # Background behind label
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(self.color))
        painter.drawRect(label_rect)

        # Label text in white
        painter.setPen(QPen(QColor(255, 255, 255)))
        painter.drawText(label_rect, Qt.AlignmentFlag.AlignCenter, label)

    def sync_bbox_from_pos(self) -> None:
        """Update the BoundingBox model from the current item position."""
        rect = self.rect()
        pos = self.pos()
        self.bbox.x_min = int(rect.x() + pos.x())
        self.bbox.y_min = int(rect.y() + pos.y())
        self.bbox.x_max = self.bbox.x_min + int(rect.width())
        self.bbox.y_max = self.bbox.y_min + int(rect.height())

    def _get_resize_mode(self, pos: QPointF) -> str | None:
        rect = self.rect()
        x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()
        px, py = pos.x(), pos.y()

        left = px <= x + _GRAB_MARGIN
        right = px >= x + w - _GRAB_MARGIN
        top = py <= y + _GRAB_MARGIN
        bottom = py >= y + h - _GRAB_MARGIN

        if top and left: return 'top_left'
        if top and right: return 'top_right'
        if bottom and left: return 'bottom_left'
        if bottom and right: return 'bottom_right'
        if top: return 'top'
        if bottom: return 'bottom'
        if left: return 'left'
        if right: return 'right'
        return None

    def hoverMoveEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        if not self.flags() & QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable:
            super().hoverMoveEvent(event)
            return

        mode = self._get_resize_mode(event.pos())
        if mode in ('top_left', 'bottom_right'):
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        elif mode in ('top_right', 'bottom_left'):
            self.setCursor(Qt.CursorShape.SizeBDiagCursor)
        elif mode in ('left', 'right'):
            self.setCursor(Qt.CursorShape.SizeHorCursor)
        elif mode in ('top', 'bottom'):
            self.setCursor(Qt.CursorShape.SizeVerCursor)
        else:
            self.setCursor(Qt.CursorShape.SizeAllCursor)

        super().hoverMoveEvent(event)

    def hoverLeaveEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        self.setCursor(Qt.CursorShape.ArrowCursor)
        super().hoverLeaveEvent(event)

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton and (self.flags() & QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable):
            mode = self._get_resize_mode(event.pos())
            if mode:
                self._resize_mode = mode
                self._start_rect = self.rect()
                self._start_pos_scene = event.scenePos()
                event.accept()
                return

        self._resize_mode = None
        self._start_pos = self.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        if self._resize_mode:
            diff = event.scenePos() - self._start_pos_scene
            dx, dy = diff.x(), diff.y()

            rect = QRectF(self._start_rect)
            if 'left' in self._resize_mode:
                rect.setLeft(rect.left() + dx)
            elif 'right' in self._resize_mode:
                rect.setRight(rect.right() + dx)

            if 'top' in self._resize_mode:
                rect.setTop(rect.top() + dy)
            elif 'bottom' in self._resize_mode:
                rect.setBottom(rect.bottom() + dy)

            # Enforce minimum size
            if rect.width() < 5:
                if 'left' in self._resize_mode:
                    rect.setLeft(rect.right() - 5)
                else:
                    rect.setRight(rect.left() + 5)

            if rect.height() < 5:
                if 'top' in self._resize_mode:
                    rect.setTop(rect.bottom() - 5)
                else:
                    rect.setBottom(rect.top() + 5)

            self.setRect(rect)
            return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        if self._resize_mode:
            self._resize_mode = None
            self.sync_bbox_from_pos()
            if getattr(self, "on_moved_callback", None):
                self.on_moved_callback(self.index)
            event.accept()
            return

        super().mouseReleaseEvent(event)
        if hasattr(self, "_start_pos") and self.pos() != self._start_pos:
            if getattr(self, "on_moved_callback", None):
                self.on_moved_callback(self.index)

