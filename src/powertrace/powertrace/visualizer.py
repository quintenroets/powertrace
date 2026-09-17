import os
import pdb  # noqa: T100
import stat
import sys
import time
from dataclasses import dataclass
from typing import TextIO

import cli
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

        self.visualize_in_console()
        if "POWERTRACE_DEBUG" in os.environ and sys.stdin.isatty():
            pdb.post_mortem(self.traceback.traceback)

    @property
    def should_show_locals(self) -> bool:
        show_full_traceback = os.environ.get("FULL_TRACEBACK", "false") != "false"
        trace_without_locals = self.traceback.construct_message(show_locals=False).trace
        frames = trace_without_locals.stacks[0].frames
        loading_error_keyword = "importlib_load_entry_point"
        loading_error = any(frame.name == loading_error_keyword for frame in frames)
        # generating locals on error during initial loading leads
        # to infinite recursive traceback handling and abortion
        return show_full_traceback and not (loading_error or self.disable_show_locals)

    def visualize_in_console(self) -> None:
        if should_visualize_in_new_tab():
            try:
                self.visualize_in_new_tab()
            except FileNotFoundError:
                self.visualize_in_active_tab()
        else:
            self.visualize_in_active_tab()

    @classmethod
    def visualize_in_new_tab(cls) -> None:
        command = f"cat {Path.log.with_console_suffix}; read && exit"
        process = cli.run_in_new_tab(command, title="Exception")
        process.communicate()  # make sure opening cli has finished before exiting

    @classmethod
    def visualize_in_active_tab(cls) -> None:
        cli.run("cat", Path.log.with_console_suffix, stdout=sys.stderr)
        if "GITHUB_ACTIONS" in os.environ:
            time.sleep(2)  # pragma: nocover

    def save(self, path: Path, *, show_locals: bool | None = None) -> None:
        if show_locals is None:
            show_locals = self.should_show_locals

        with path.with_console_suffix.open("w") as fp:
            console = Console(file=fp, record=True, force_terminal=True)
            message = self.traceback.construct_message(show_locals=show_locals)
            console.print(message)
            console.save_text(str(path))


def should_visualize_in_new_tab() -> bool:
    display = os.environ.get("DISPLAY")
    has_window_server = display is not None and "localhost" not in display
    streams = (sys.stderr, sys.stdout)
    output_is_observed = any(stream_is_observed(stream) for stream in streams)
    return has_window_server and not output_is_observed


def stream_is_observed(stream: TextIO) -> bool:
    try:
        fd = stream.fileno()
        mode = os.fstat(fd).st_mode
    except (OSError, ValueError):
        return False
    return (
        os.isatty(fd)
        or stat.S_ISFIFO(mode)
        or stat.S_ISREG(mode)
        or stat.S_ISSOCK(mode)
    )
