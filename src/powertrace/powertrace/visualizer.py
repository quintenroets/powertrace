import os
import pdb  # noqa: T100
import sys
from dataclasses import dataclass
from traceback import walk_tb

from rich.console import Console

from .traceback import Traceback


@dataclass
class TraceVisualizer:
    traceback: Traceback
    disable_show_locals: bool = False

    def visualize_traceback_atomic(self) -> None:
        console = Console(force_terminal=True)
        message = self.traceback.construct_message(show_locals=self.should_show_locals)
        with console.capture() as capture:
            console.print(message)
        sys.stderr.write(capture.get())
        if "POWERTRACE_DEBUG" in os.environ and sys.stdin.isatty():
            pdb.post_mortem(self.traceback.traceback)

    @property
    def should_show_locals(self) -> bool:
        show_full_traceback = os.environ.get("FULL_TRACEBACK", "false") != "false"
        names = (frame.f_code.co_name for frame, _ in walk_tb(self.traceback.traceback))
        loading_error = "importlib_load_entry_point" in names
        # generating locals on error during initial loading leads
        # to infinite recursive traceback handling and abortion
        return show_full_traceback and not (loading_error or self.disable_show_locals)
