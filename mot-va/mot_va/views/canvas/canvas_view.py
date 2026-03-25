from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter
from PyQt6.QtWidgets import QGraphicsView

from mot_va.views.canvas.canvas_scene import CanvasScene

_ZOOM_FACTOR = 1.15
_MIN_ZOOM = 0.1
_MAX_ZOOM = 20.0


class CanvasView(QGraphicsView):
    """Graphics view with zoom and pan support."""

    def __init__(self, scene: CanvasScene) -> None:
        super().__init__(scene)
        self._zoom_level = 1.0

        self.setRenderHints(
            QPainter.RenderHint.Antialiasing
            | QPainter.RenderHint.SmoothPixmapTransform
        )
        self.setViewportUpdateMode(
            QGraphicsView.ViewportUpdateMode.FullViewportUpdate
        )
        self.setTransformationAnchor(
            QGraphicsView.ViewportAnchor.AnchorUnderMouse
        )
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

    def fit_to_scene(self) -> None:
        """Fit the scene content to the viewport, maximizing image size."""
        scene = self.scene()
        if scene and not scene.sceneRect().isEmpty():
            self.resetTransform()
            self._zoom_level = 1.0
            self.fitInView(scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
            # Calculate actual zoom level after fitInView
            self._zoom_level = self.transform().m11()

    def wheelEvent(self, event) -> None:  # type: ignore[override]
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            angle = event.angleDelta().y()
            if angle > 0:
                factor = _ZOOM_FACTOR
            elif angle < 0:
                factor = 1.0 / _ZOOM_FACTOR
            else:
                return

            new_zoom = self._zoom_level * factor
            if _MIN_ZOOM <= new_zoom <= _MAX_ZOOM:
                self._zoom_level = new_zoom
                self.scale(factor, factor)
        else:
            super().wheelEvent(event)

    def set_draw_mode(self, enabled: bool) -> None:
        """Switch between draw mode (no drag) and pan mode (hand drag)."""
        if enabled:
            self.setDragMode(QGraphicsView.DragMode.NoDrag)
            self.setCursor(Qt.CursorShape.CrossCursor)
        else:
            self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
            self.unsetCursor()

    def resizeEvent(self, event) -> None:  # type: ignore[override]
        """Re-fit image when the view is resized."""
        super().resizeEvent(event)
        self.fit_to_scene()
