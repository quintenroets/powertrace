import os
import sys
import threading
import traceback
from dataclasses import dataclass
from functools import cached_property
from types import TracebackType

import cli
from rich.console import Console
from rich.traceback import Traceback

from . import config
from .path import Path

tb_handled: bool = False
tb_mutex = threading.Lock()


@dataclass
class ExcInfo:
    type: type = None
    value: BaseException = None
    traceback: TracebackType = None
    exit_after: bool = True
    repeat: bool = True
    disable_show_locals: bool = False

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
        except Exception as e:  # noqa
            # last resort when custom error handling fails
            traceback.print_exc()

    def safe_show(self):
        if self.type not in (KeyboardInterrupt, SystemExit, None, RecursionError):
            with tb_mutex:
                # only visualize the first traceback for crashing threads
                self.single_threaded_show()

    def single_threaded_show(self):
        global tb_handled
        if not tb_handled or (self.in_main_thread and self.repeat):
            tb_handled = True
            self.show_single()

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
        from . import monkeypatch  # noqa: autoimport

        monkeypatch.run_custom_handlers(self.type, self.value)

        self.save(Path.log)
        if self.type and self.show_locals:
            self.save(Path.short_log, include_locals=False)

        self.visualize_in_console()
        self.exit()

    def exit(self):
        if self.exit_after and not self.in_main_thread:
            os._exit(1)  # force exit
            sys.exit(1)  # stop execution after error in threads as well

    @classmethod
    def visualize_in_console(cls):
        command = f"cat {Path.log.console}; read"
        try:
            process = cli.start(command, console=True, title="Exception")
            process.communicate()  # make sure opening cli has finished before exiting
        except FileNotFoundError:
            # opening new window failed -> just show in current window
            cli.run("cat", Path.log.console)

    def save(self, path: Path, include_locals: bool = None):
        if include_locals is None:
            include_locals = self.show_locals

        with path.console.open("w") as fp:
            console = Console(file=fp, record=True, force_terminal=True)
            traceback_message = self.construct_message(show_locals=include_locals)
            console.print(traceback_message)
            console.save_text(str(path))
