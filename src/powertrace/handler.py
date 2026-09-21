import os
import pdb  # noqa: T100
import subprocess
import sys
import threading
from collections.abc import Iterator
from traceback import print_exception, walk_tb

from rich.console import Console, Group
from rich.constrain import Constrain
from rich.panel import Panel
from rich.text import Text
from rich.traceback import Traceback

mutex = threading.Lock()


def handle(exception: BaseException, *, exit_after: bool = True) -> None:
    if isinstance(exception, RecursionError):
        print_exception(exception)
    else:
        with mutex:
            report(exception)
            if exit_after and threading.current_thread() is not threading.main_thread():
                os._exit(1)  # pragma: nocover


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
    console = Console(stderr=True, force_terminal=True)
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
