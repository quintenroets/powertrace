import os
import sys
import threading

from rich.console import Console
from rich.traceback import Traceback

import _thread as thread
import cli
from plib import Path

tbs_handled = set({})
tb_mutex = threading.Lock()


def threading_excepthook(info):
    return excepthook(info.exc_type, info.exc_value, info.exc_traceback)


def excepthook(exc_type, exc_value, traceback):
    if exc_type not in (KeyboardInterrupt, SystemExit):
        show(exc_type, exc_value, traceback)


def show(
    exc_type=None,
    exc_value=None,
    traceback=None,
    exit=True,
    repeat=True,
):
    """
    Can be called on any given moment to visualize the current stack trace
    param exit: stop execution after visualizing stack trace
    """
    with tb_mutex:
        # only visualize the first traceback for crashing threads
        if not tbs_handled or (
            threading.current_thread() is threading.main_thread() and repeat
        ):
            tbs_handled.add(traceback)
            try:
                _show(exc_type, exc_value, traceback, exit)
            except Exception as e:
                # constructing rich traceback can fail: visualize this as well
                _show(exit=exit)


def _show(exc_type=None, exc_value=None, traceback=None, exit=True):
    from .monkeypatch import custom_handlers  # slow import

    custom_handlers(exc_type, exc_value)

    log_file = Path.assets / ".error_console.txt"
    show_locals = os.environ.get("full_traceback", "false") != "false"

    traceback_message = (
        Traceback.from_exception(
            exc_type, exc_value, traceback, show_locals=show_locals
        )
        if exc_type
        else Traceback()
    )

    with log_file.open("w") as fp:
        console = Console(file=fp, record=True, force_terminal=True)
        console.print(traceback_message)
        console.save_text(log_file.with_stem(".error"))

    if exc_type:
        traceback_message_short = Traceback.from_exception(
            exc_type, exc_value, traceback
        )
        with Path.tempfile() as path:
            with path.open("w") as fp:
                console = Console(file=fp, record=True, force_terminal=True)
                console.print(traceback_message_short)
                console.save_text(log_file.with_stem(".error_short"))

    process = cli.start(f"cat {log_file}; read", console=True)
    process.communicate()  # make sure opening cli has finished before exiting

    if exit and threading.current_thread() is not threading.main_thread():
        os._exit(1)  # force exit
        sys.exit(1)  # stop execution after error in threads as well


def install():
    sys.excepthook = excepthook
    thread._excepthook = threading_excepthook
