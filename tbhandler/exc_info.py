import os
import pdb
import sys
import threading
import traceback
from dataclasses import dataclass
from functools import cached_property
from traceback import walk_tb
from types import TracebackType
from typing import ClassVar

import cli
from rich.console import Console
from rich.traceback import Traceback

from . import config
from .path import Path

tb_mutex = threading.Lock()


@dataclass
class ExcInfo:
    type: type = None
    value: BaseException = None
    traceback: TracebackType = None
    exit_after: bool = True
    repeat: bool = True
    disable_show_locals: bool = False
    tb_handled: ClassVar[bool] = False
    skipped_exception_types: tuple = (
        KeyboardInterrupt,
        SystemExit,
        RecursionError,
        BrokenPipeError,
        None,
    )
    use_original_handler: tuple = (RecursionError,)

    @property
    def in_main_thread(self):
        return threading.current_thread() is threading.main_thread()

    @property
    def show_locals(self):
        loading_error = any(
            frame.name == "importlib_load_entry_point"
            for frame in self.short_message.trace.stacks[0].frames
        )
        # generating locals on error during initial loading leads
        # to infinite recursive traceback handling and abortion
        show_locals = config.show_locals() and not (
            loading_error or self.disable_show_locals
        )
        return show_locals

    @property
    def message(self):
        return self.construct_message(show_locals=self.show_locals)

    @cached_property
    def short_message(self):
        return self.construct_message(show_locals=False)

    def construct_message(self, show_locals: bool) -> Traceback:
        return (
            Traceback.from_exception(
                self.type, self.value, self.traceback, show_locals=show_locals
            )
            if self.type
            else Traceback()
        )

    def show(self):
        try:
            self.safe_show()
        except Exception:  # noqa: E722
            # last resort when custom error handling fails
            traceback.print_exc()

    def safe_show(self):
        if self.type not in self.skipped_exception_types:
            with tb_mutex:
                # only visualize the first traceback for crashing threads
                self.single_threaded_show()
        elif self.type in self.use_original_handler:
            sys.__excepthook__(self.type, self.value, self.traceback)

    def single_threaded_show(self):
        if not self.tb_handled or (self.in_main_thread and self.repeat):
            self.__class__.tb_handled = True
            self.show_single()

    @property
    def filename(self):
        frame_summary = None
        for frame_summary, _ in walk_tb(self.traceback):
            pass
        return frame_summary and self.extract_path(frame_summary)

    @classmethod
    def extract_path(cls, frame_summary):
        path = Path(frame_summary.f_code.co_filename)
        if not path.exists():
            path = None
        return path

    def show_single(self):
        try:
            self._show_single()
        except:  # noqa
            self.disable_show_locals = True
            try:
                # try without locals when message construction fails
                self._show_single()
            except Exception:
                # visualize failure to construct message
                exc = ExcInfo(exit_after=self.exit_after)
                exc._show_single()

    def _show_single(self):
        from . import monkeypatch  # noqa: E402, autoimport

        monkeypatch.run_custom_handlers(self.type, self.value)

        self.save(Path.log)
        if self.type and self.show_locals:
            self.save(Path.short_log, include_locals=False)

        self.visualize_in_console()
        self.check_debug()
        self.exit()

    def check_debug(self):
        should_debug = "tbhanlder_DEBUG" in os.environ and sys.stdin.isatty()
        if should_debug:
            pdb.post_mortem(self.traceback)

    def exit(self):
        if self.exit_after and not self.in_main_thread:
            os._exit(1)  # force exit
            sys.exit(1)  # stop execution after error in threads as well

    def visualize_in_console(self):
        can_visualize_in_new_tab = (
            "DISPLAY" in os.environ and "localhost" not in os.environ["DISPLAY"]
        )
        if can_visualize_in_new_tab:
            try:
                self.visualize_in_new_tab()
            except FileNotFoundError:
                can_visualize_in_new_tab = False
        if not can_visualize_in_new_tab:
            self.visualize_in_active_tab()

    def visualize_in_new_tab(self):
        confirm_command = (
            "read"
            if self.filename is None
            else f"ask_open_exception_file {self.filename} || read"
        )
        command = f"cat {Path.log.console}; {confirm_command}"
        process = cli.start(command, console=True, title="Exception")
        process.communicate()  # make sure opening cli has finished before exiting

    @classmethod
    def visualize_in_active_tab(cls):
        cli.run("cat", Path.log.console)

    def save(self, path: Path, include_locals: bool = None):
        if include_locals is None:
            include_locals = self.show_locals

        with path.console.open("w") as fp:
            console = Console(file=fp, record=True, force_terminal=True)
            traceback_message = self.construct_message(show_locals=include_locals)
            console.print(traceback_message)
            console.save_text(str(path))
