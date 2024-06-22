import os
from dataclasses import dataclass

from superpathlib import Path


@dataclass
class Config:
    output_path: Path | None = None
    secrets_path: Path | None = None
    show_full_traceback: bool = os.environ.get("full_traceback", "false") != "false"
