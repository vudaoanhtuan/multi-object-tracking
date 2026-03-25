from pathlib import Path

from mot_va.models.frame import Frame
from mot_va.models.project import Project
from mot_va.models.sample import Sample


def scan_dataset(root: Path) -> Project:
    """Scan a directory for MOT dataset samples.

    Looks for directories matching sample_* pattern, each containing
    a frames/ subdirectory with .jpeg files.
    """
    project = Project(root_dir=root)

    sample_dirs = sorted(
        d for d in root.iterdir()
        if d.is_dir() and d.name.startswith("sample_")
    )

    for sample_dir in sample_dirs:
        frames_dir = sample_dir / "frames"
        if not frames_dir.is_dir():
            continue

        sample = Sample(
            sample_id=sample_dir.name,
            directory=sample_dir,
        )

        label_dir = sample_dir / "mot_label"
        image_files = sorted(frames_dir.glob("*.jpeg"))

        for img_path in image_files:
            frame_id = img_path.stem
            label_path = label_dir / f"{frame_id}.txt"
            sample.frames.append(
                Frame(
                    frame_id=frame_id,
                    image_path=img_path,
                    label_path=label_path,
                )
            )

        if sample.frames:
            project.samples.append(sample)

    return project
