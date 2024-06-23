import os
import pdb
import sys
import time
from dataclasses import dataclass

import cli
from rich.console import Console

from ..context import context
from ..models import Path
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
        if context.should_debug:
            pdb.post_mortem(self.traceback.traceback)
        self.exit()

    @property
    def should_show_locals(self) -> bool:
        trace_without_locals = self.traceback.construct_message(show_locals=False).trace
        frames = trace_without_locals.stacks[0].frames
        loading_error_keyword = "importlib_load_entry_point"
        loading_error = any(frame.name == loading_error_keyword for frame in frames)
        # generating locals on error during initial loading leads
        # to infinite recursive traceback handling and abortion
        return context.show_full_traceback and not (
            loading_error or self.disable_show_locals
        )

    def visualize_in_console(self) -> None:
        if context.can_visualize_in_new_tab:
            try:
                self.visualize_in_new_tab()
            except FileNotFoundError:
                self.visualize_in_active_tab()
        else:
            self.visualize_in_active_tab()

    def visualize_in_new_tab(self) -> None:
        confirm_command = (
            "read"
            if self.traceback.filename is None
            else f"ask_open_exception_file {self.traceback.filename} || read"
        )
        command = f"cat {Path.log.with_console_suffix}; {confirm_command}"
        process = cli.run_in_console(command, title="Exception")
        process.communicate()  # make sure opening cli has finished before exiting

    @classmethod
    def visualize_in_active_tab(cls) -> None:
        cli.run("cat", Path.log.with_console_suffix)
        if context.is_running_in_ci:
            time.sleep(2)

    def save(self, path: Path, show_locals: bool | None = None) -> None:
        if show_locals is None:
            show_locals = self.should_show_locals

        with path.with_console_suffix.open("w") as fp:
            console = Console(file=fp, record=True, force_terminal=True)
            message = self.traceback.construct_message(show_locals=show_locals)
            console.print(message)
            console.save_text(str(path))

    @classmethod
    def exit(cls) -> None:
        if context.config.exit_after and not context.is_running_in_main_thread:
            os._exit(1)  # force exit
            sys.exit(1)  # stop execution after error in threads as well
