from dataclasses import dataclass, field
from pathlib import Path

from mot_va.models.sample import Sample


@dataclass
class Project:
    root_dir: Path
    samples: list[Sample] = field(default_factory=list)
