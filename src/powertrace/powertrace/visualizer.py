import os
import pdb  # noqa: T100
import sys
from dataclasses import dataclass
from traceback import walk_tb

from rich.console import Console

from powertrace.models import Path

from .traceback import Traceback


@dataclass
class TraceVisualizer:
    traceback: Traceback
    disable_show_locals: bool = False

    def visualize_traceback_atomic(self) -> None:
        self.save(Path.log)
        if self.traceback.type_ and self.should_show_locals:
            self.save(Path.short_log, show_locals=False)

        sys.stderr.write(Path.log.with_console_suffix.read_text())
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

    def save(self, path: Path, *, show_locals: bool | None = None) -> None:
        if show_locals is None:
            show_locals = self.should_show_locals

        with path.with_console_suffix.open("w") as fp:
            console = Console(file=fp, record=True, force_terminal=True)
            message = self.traceback.construct_message(show_locals=show_locals)
            console.print(message)
            console.save_text(str(path))
