import _thread as thread
import os
import sys
import threading
from dataclasses import dataclass
from functools import cached_property
from types import TracebackType

import cli
from plib import Path
from rich.console import Console
from rich.traceback import Traceback

from . import config

tb_handled: bool = False
tb_mutex = threading.Lock()


@dataclass
class EXC_INFO:
    type: Exception = None
    value: str = None
    traceback: TracebackType = None

    @cached_property
    def message(self):
        return self.construct_message(show_locals=True)

    @cached_property
    def short_message(self):
        return self.construct_message()

    def construct_message(self, show_locals: bool = False) -> Traceback:
        return (
            Traceback.from_exception(
                self.type, self.value, self.traceback, show_locals=show_locals
            )
            if self.type
            else Traceback()
        )


def threading_excepthook(info):
    return excepthook(info.exc_type, info.exc_value, info.exc_traceback)


def excepthook(exc_type, exc_value, traceback):
    if exc_type not in (KeyboardInterrupt, SystemExit):
        show(EXC_INFO(exc_type, exc_value, traceback))


def show(exc_info: EXC_INFO = EXC_INFO(), exit_after: bool = True, repeat: bool = True):
    """
    Can be called on any given moment to visualize the current stack trace
    param exit: stop execution after visualizing stack trace
    """
    with tb_mutex:
        # only visualize the first traceback for crashing threads
        global tb_handled
        if not tb_handled or (
            threading.current_thread() is threading.main_thread() and repeat
        ):
            tb_handled = True
            try:
                _show(exc_info, exit_after)
            except Exception:
                # constructing rich traceback can fail: visualize this as well
                _show(exit_after=exit_after)


def _show(exc_info: EXC_INFO = None, exit_after=True):
    from . import monkeypatch  # noqa: autoimport

    monkeypatch.run_custom_handlers(exc_info.type, exc_info.value)

    log_folder = Path.assets / ".error"
    console_log_path = log_folder / "console.txt"

    loading_error = any(
        frame.name == "importlib_load_entry_point"
        for frame in exc_info.short_message.trace.stacks[0].frames
    )
    # generating locals on error during initial loading leads to infinite recursive traceback handling and abortion
    show_locals = config.show_locals() and not loading_error
    traceback = exc_info.message if show_locals else exc_info.short_message
    save_traceback(traceback, log_folder / "console.txt", log_folder / "error.txt")

    if exc_info.type and show_locals:
        with Path.tempfile() as path:
            save_traceback(
                exc_info.short_message,
                path,
                log_folder / "short.txt",
            )

    process = cli.start(
        f"cat {console_log_path}; read", console=True, title="Exception"
    )
    process.communicate()  # make sure opening cli has finished before exiting

    if exit and threading.current_thread() is not threading.main_thread():
        os._exit(1)  # force exit
        sys.exit(1)  # stop execution after error in threads as well


def save_traceback(traceback: Traceback, dest: Path, text_dest: Path = None):
    with dest.open("w") as fp:
        console = Console(file=fp, record=True, force_terminal=True)
        console.print(traceback)
        if text_dest is not None:
            console.save_text(text_dest)


def install():
    sys.excepthook = excepthook
    thread._excepthook = threading_excepthook
