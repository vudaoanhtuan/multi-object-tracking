from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QSpinBox,
    QVBoxLayout,
)

from mot_va.services import color_registry


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
        self.resize(300, 400)
        self._final_selected_id: int | None = None

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Double-click an ID or select one and click OK:"))

        # List Widget for existing and new IDs
        self._list_widget = QListWidget()
        layout.addWidget(self._list_widget)

        # Populate existing IDs
        for oid in sorted(existing_ids):
            item = self._create_colored_item(oid, f"Existing ID: {oid}")
            self._list_widget.addItem(item)
            if suggested_id == oid:
                item.setSelected(True)

        # Determine initial new ID
        next_id = max(existing_ids, default=-1) + 1
        if suggested_id is not None and suggested_id not in existing_ids:
            next_id = suggested_id

        # Pseudo new object ID item
        self._new_id_item = self._create_colored_item(next_id, f"New ID: {next_id}")
        self._list_widget.addItem(self._new_id_item)

        if suggested_id is None or suggested_id not in existing_ids:
            self._new_id_item.setSelected(True)

        self._list_widget.itemDoubleClicked.connect(self._on_item_double_clicked)

        # Spinbox for changing the new ID
        spin_layout = QHBoxLayout()
        spin_layout.addWidget(QLabel("Set New ID:"))
        self._spin = QSpinBox()
        self._spin.setMinimum(0)
        self._spin.setMaximum(9999)
        self._spin.setValue(next_id)
        self._spin.valueChanged.connect(self._on_spinbox_changed)
        spin_layout.addWidget(self._spin)
        layout.addLayout(spin_layout)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _create_colored_item(self, obj_id: int, text: str) -> QListWidgetItem:
        """Create a list item with a colored icon based on the object ID."""
        color = color_registry.get_color(obj_id)
        pixmap = QPixmap(16, 16)
        pixmap.fill(color)
        icon = QIcon(pixmap)
        
        item = QListWidgetItem(icon, text)
        item.setData(Qt.ItemDataRole.UserRole, obj_id)
        return item

    def _on_spinbox_changed(self, value: int) -> None:
        """Update the pseudo new object item when spinbox changes."""
        color = color_registry.get_color(value)
        pixmap = QPixmap(16, 16)
        pixmap.fill(color)
        
        self._new_id_item.setIcon(QIcon(pixmap))
        self._new_id_item.setText(f"New ID: {value}")
        self._new_id_item.setData(Qt.ItemDataRole.UserRole, value)

    def _on_item_double_clicked(self, item: QListWidgetItem) -> None:
        """Accept the dialog when an item is double-clicked."""
        self._final_selected_id = item.data(Qt.ItemDataRole.UserRole)
        self.accept()

    def selected_id(self) -> int | None:
        """Return the chosen ID, or None if cancelled."""
        if self.result() != QDialog.DialogCode.Accepted:
            return None
        
        if self._final_selected_id is not None:
            return self._final_selected_id
            
        selected_items = self._list_widget.selectedItems()
        if selected_items:
            return selected_items[0].data(Qt.ItemDataRole.UserRole)
            
        return None
