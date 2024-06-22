import os
from dataclasses import dataclass


@dataclass
class Config:
    show_full_traceback: bool = os.environ.get("full_traceback", "false") != "false"
    exit_after: bool = True
    repeat: bool = True
