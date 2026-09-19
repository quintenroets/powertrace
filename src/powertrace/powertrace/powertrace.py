import os
import pdb  # noqa: T100
import sys
import threading
from traceback import print_exception, walk_tb

from rich.console import Console
from rich.traceback import Traceback

mutex = threading.Lock()
handled = threading.Event()


def handle(
    exception: BaseException,
    *,
    exit_after: bool = True,
    repeat: bool = True,
) -> None:
    if isinstance(exception, RecursionError):
        print_exception(exception)
    elif not isinstance(exception, KeyboardInterrupt | SystemExit | BrokenPipeError):
        in_main_thread = threading.current_thread() is threading.main_thread()
        with mutex:
            # only handle the first exception from crashing threads
            if (repeat and in_main_thread) or not handled.is_set():
                handled.set()
                report(exception)
                if exit_after and not in_main_thread:  # pragma: nocover
                    os._exit(1)


def report(exception: BaseException) -> None:
    try:
        print_rich_exception(exception)
    except Exception as error:  # noqa: BLE001
        print_exception(error)
        print_exception(exception)
    if "POWERTRACE_DEBUG" in os.environ and sys.stdin.isatty():
        pdb.post_mortem(exception.__traceback__)


def print_rich_exception(exception: BaseException) -> None:
    exc_info = type(exception), exception, exception.__traceback__
    show_locals = should_show_locals(exception)
    try:
        traceback = Traceback.from_exception(*exc_info, show_locals=show_locals)
    except Exception:  # noqa: BLE001
        traceback = Traceback.from_exception(*exc_info, show_locals=False)
    console = Console(force_terminal=True)
    with console.capture() as capture:
        console.print(traceback)
    sys.stderr.write(capture.get())


def should_show_locals(exception: BaseException) -> bool:
    full_traceback = os.environ.get("FULL_TRACEBACK", "false") != "false"
    frames = walk_tb(exception.__traceback__)
    names = (frame.f_code.co_name for frame, _ in frames)
    # rendering locals while loading the entry point recurses infinitely and aborts
    return full_traceback and "importlib_load_entry_point" not in names
