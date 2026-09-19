import os
import pdb  # noqa: T100
import subprocess
import sys
import threading
from collections.abc import Iterator
from traceback import print_exception, walk_tb
from types import TracebackType
from typing import cast

from rich.console import Console, Group
from rich.constrain import Constrain
from rich.panel import Panel
from rich.text import Text
from rich.traceback import Traceback

mutex = threading.Lock()
handled = threading.Event()


def install_traceback_hooks() -> None:
    sys.excepthook = excepthook
    threading.excepthook = threading_excepthook


def excepthook(
    _type: type[BaseException],
    value: BaseException,
    _traceback: TracebackType | None,
) -> None:
    handle(value, repeat=False)


def threading_excepthook(args: threading.ExceptHookArgs) -> None:
    value = cast("BaseException", args.exc_value)
    handle(value, repeat=False)


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
    output = Group(traceback, *generate_output_panels(exception))
    console = Console(force_terminal=True)
    with console.capture() as capture:
        console.print(Constrain(output, traceback.width))
    sys.stderr.write(capture.get())


def should_show_locals(exception: BaseException) -> bool:
    full_traceback = os.environ.get("FULL_TRACEBACK", "false") != "false"
    frames = walk_tb(exception.__traceback__)
    names = (frame.f_code.co_name for frame, _ in frames)
    # rendering locals while loading the entry point recurses infinitely and aborts
    return full_traceback and "importlib_load_entry_point" not in names


def generate_output_panels(exception: BaseException) -> Iterator[Panel]:
    for error in walk_chain(exception):
        if isinstance(error, subprocess.CalledProcessError):
            output = error.stderr or error.output or ""
            if isinstance(output, bytes):
                output = output.decode(errors="backslashreplace")
            content = Text.from_ansi(output.strip())
            if content.plain.strip():
                yield Panel(content, title="output", border_style="traceback.border")


def walk_chain(exception: BaseException | None) -> Iterator[BaseException]:
    while exception is not None:
        yield exception
        context = None if exception.__suppress_context__ else exception.__context__
        exception = exception.__cause__ or context
