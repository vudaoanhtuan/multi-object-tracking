from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QLabel,
    QSpinBox,
    QVBoxLayout,
)


class ObjectIdDialog(QDialog):
    """Dialog for assigning an object ID to a new bounding box."""

    def __init__(
        self,
        existing_ids: list[int],
        parent=None,  # type: ignore[no-untyped-def]
        suggested_id: int | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Assign Object ID")
        self._selected_id: int | None = None

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Choose an existing ID or create a new one:"))

        # Existing IDs combo
        self._mode_combo = QComboBox()
        self._mode_combo.addItem("New ID")
        for oid in sorted(existing_ids):
            self._mode_combo.addItem(f"Existing: {oid}", oid)
        self._mode_combo.currentIndexChanged.connect(self._on_mode_changed)
        layout.addWidget(self._mode_combo)

        # New ID spinner
        self._spin = QSpinBox()
        self._spin.setMinimum(0)
        self._spin.setMaximum(9999)
        if suggested_id is not None and suggested_id in existing_ids:
            self._mode_combo.setCurrentIndex(
                self._mode_combo.findData(suggested_id)
            )
            # Default fallback for spin box if user switches to "New ID"
            self._spin.setValue(max(existing_ids, default=-1) + 1)
        else:
            next_id = max(existing_ids, default=-1) + 1
            self._spin.setValue(next_id)
            self._mode_combo.setCurrentIndex(0)  # "New ID" is index 0
        layout.addWidget(self._spin)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _on_mode_changed(self, index: int) -> None:
        self._spin.setEnabled(index == 0)

    def selected_id(self) -> int | None:
        """Return the chosen ID, or None if cancelled."""
        if self.result() != QDialog.DialogCode.Accepted:
            return None
        if self._mode_combo.currentIndex() == 0:
            return self._spin.value()
        return self._mode_combo.currentData()
