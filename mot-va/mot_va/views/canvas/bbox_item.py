from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtGui import QBrush, QColor, QFont, QPainter, QPen
from PyQt6.QtWidgets import QGraphicsRectItem, QStyleOptionGraphicsItem, QWidget

from mot_va.models.bbox import BoundingBox


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
        font = QFont("Sans", 10)
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
