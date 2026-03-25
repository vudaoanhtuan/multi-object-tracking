from pathlib import Path

from mot_va.models.bbox import BoundingBox


def read_mot_labels(path: Path) -> list[BoundingBox]:
    """Read MOT labels from a text file.

    Each line: object_id, x_min, y_min, x_max, y_max
    Returns empty list if file does not exist.
    """
    if not path.exists():
        return []

    bboxes: list[BoundingBox] = []
    for line in path.read_text().strip().splitlines():
        parts = [p.strip() for p in line.split(",")]
        if len(parts) != 5:
            continue
        obj_id, x_min, y_min, x_max, y_max = (int(p) for p in parts)
        bboxes.append(BoundingBox(obj_id, x_min, y_min, x_max, y_max))
    return bboxes


def write_mot_labels(path: Path, bboxes: list[BoundingBox]) -> None:
    """Write MOT labels to a text file.

    Creates parent directories if needed.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"{b.object_id}, {b.x_min}, {b.y_min}, {b.x_max}, {b.y_max}"
        for b in bboxes
    ]
    path.write_text("\n".join(lines) + "\n" if lines else "")
