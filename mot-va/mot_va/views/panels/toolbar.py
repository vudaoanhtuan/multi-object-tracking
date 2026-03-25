from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox,
    QLabel,
    QPushButton,
    QSizePolicy,
    QToolBar,
)


class ToolBar(QToolBar):
    """Top bar: mode switch, draw, save, discard, frame navigation, open dataset."""

    open_requested = pyqtSignal()
    save_requested = pyqtSignal()
    discard_requested = pyqtSignal()
    mode_changed = pyqtSignal(str)  # "annotation" or "view"
    prev_frame = pyqtSignal()
    next_frame = pyqtSignal()
    draw_mode_toggled = pyqtSignal(bool)
    auto_save_toggled = pyqtSignal(bool)
    zoom_in_requested = pyqtSignal()
    zoom_out_requested = pyqtSignal()

    def __init__(self) -> None:
        super().__init__("Main Toolbar")
        self.setMovable(False)

        # Open button
        self._open_btn = QPushButton("Open...")
        self._open_btn.clicked.connect(self.open_requested)
        self.addWidget(self._open_btn)

        self.addSeparator()

        # Mode toggle
        self._mode_btn = QPushButton("Edit Mode")
        self._mode_btn.setCheckable(True)
        self._mode_btn.setChecked(True)
        self._mode_btn.toggled.connect(self._on_mode_toggled)
        self.addWidget(self._mode_btn)

        self.addSeparator()

        # Draw button (checkable, only enabled in edit mode)
        self._draw_btn = QPushButton("Draw (A)")
        self._draw_btn.setCheckable(True)
        self._draw_btn.setEnabled(True)
        self._draw_btn.toggled.connect(self._on_draw_toggled)
        self.addWidget(self._draw_btn)

        self.addSeparator()

        # Zoom controls
        self._zoom_in_btn = QPushButton("Zoom In")
        self._zoom_in_btn.clicked.connect(self.zoom_in_requested)
        self.addWidget(self._zoom_in_btn)

        self._zoom_out_btn = QPushButton("Zoom Out")
        self._zoom_out_btn.clicked.connect(self.zoom_out_requested)
        self.addWidget(self._zoom_out_btn)

        self.addSeparator()

        # Frame navigation
        self._prev_btn = QPushButton("<")
        self._prev_btn.setFixedWidth(30)
        self._prev_btn.clicked.connect(self.prev_frame)
        self.addWidget(self._prev_btn)

        self._frame_label = QLabel(" No frame ")
        self.addWidget(self._frame_label)

        self._next_btn = QPushButton(">")
        self._next_btn.setFixedWidth(30)
        self._next_btn.clicked.connect(self.next_frame)
        self.addWidget(self._next_btn)

        spacer = QLabel()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.addWidget(spacer)

        # Auto Save toggle (enabled by default)
        self._auto_save_action = self.addAction("Auto Save")
        self._auto_save_action.setCheckable(True)
        self._auto_save_action.setChecked(True)
        self._auto_save_action.toggled.connect(self._on_auto_save_toggled)

        self.addSeparator()

        # Discard button
        self._discard_btn = QPushButton("Discard")
        self._discard_btn.setEnabled(False)
        self._discard_btn.clicked.connect(self.discard_requested)
        self.addWidget(self._discard_btn)

        # Save button
        self._save_btn = QPushButton("Save")
        self._save_btn.setEnabled(False)
        self._save_btn.clicked.connect(self.save_requested)
        self.addWidget(self._save_btn)

    def set_frame_label(self, text: str) -> None:
        self._frame_label.setText(f" {text} ")

    def set_dirty(self, dirty: bool) -> None:
        """Gray out Save/Discard when not dirty or when auto-save is on."""
        allow = dirty and not self._auto_save_action.isChecked()
        self._save_btn.setEnabled(allow)
        self._discard_btn.setEnabled(allow)

    def is_auto_save(self) -> bool:
        return self._auto_save_action.isChecked()

    def _on_auto_save_toggled(self, checked: bool) -> None:
        # When auto-save is toggled on, gray out Save/Discard
        if checked:
            self._save_btn.setEnabled(False)
            self._discard_btn.setEnabled(False)
        self.auto_save_toggled.emit(checked)

    def current_mode(self) -> str:
        return "edit" if self._mode_btn.isChecked() else "view"

    def set_draw_active(self, active: bool) -> None:
        """Programmatically set draw button state without emitting signal."""
        self._draw_btn.blockSignals(True)
        self._draw_btn.setChecked(active)
        self._draw_btn.blockSignals(False)

    def _on_mode_toggled(self, checked: bool) -> None:
        if checked:
            self._mode_btn.setText("Edit Mode")
            mode = "edit"
        else:
            self._mode_btn.setText("View Mode")
            mode = "view"
            
        self._draw_btn.setEnabled(checked)
        if not checked:
            self.set_draw_active(False)
        self.mode_changed.emit(mode)

    def _on_draw_toggled(self, checked: bool) -> None:
        self.draw_mode_toggled.emit(checked)
