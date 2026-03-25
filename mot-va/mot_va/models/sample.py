from dataclasses import dataclass, field
from pathlib import Path

from mot_va.models.frame import Frame


@dataclass
class Sample:
    sample_id: str
    directory: Path
    frames: list[Frame] = field(default_factory=list)
