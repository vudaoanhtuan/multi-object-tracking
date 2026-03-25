from PyQt6.QtGui import QColor

# 20 visually distinct colors for object IDs
_PALETTE = [
    QColor(230, 25, 75),    # Red
    QColor(60, 180, 75),    # Green
    QColor(0, 130, 200),    # Blue
    QColor(255, 225, 25),   # Yellow
    QColor(245, 130, 48),   # Orange
    QColor(145, 30, 180),   # Purple
    QColor(70, 240, 240),   # Cyan
    QColor(240, 50, 230),   # Magenta
    QColor(210, 245, 60),   # Lime
    QColor(250, 190, 212),  # Pink
    QColor(0, 128, 128),    # Teal
    QColor(220, 190, 255),  # Lavender
    QColor(170, 110, 40),   # Brown
    QColor(255, 250, 200),  # Beige
    QColor(128, 0, 0),      # Maroon
    QColor(170, 255, 195),  # Mint
    QColor(128, 128, 0),    # Olive
    QColor(255, 215, 180),  # Apricot
    QColor(0, 0, 128),      # Navy
    QColor(128, 128, 128),  # Grey
]


def get_color(object_id: int) -> QColor:
    """Return a deterministic color for the given object ID."""
    return _PALETTE[object_id % len(_PALETTE)]
