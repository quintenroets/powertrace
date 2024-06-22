import sys
import threading
from types import TracebackType

from ..context import context
from .powertrace import PowerTrace
from .traceback import Traceback


def threading_excepthook(info: threading.ExceptHookArgs) -> None:
    traceback_info = Traceback.from_info(info)
    visualize_traceback(traceback_info)


def excepthook(
    type_: type[BaseException], value: BaseException, traceback: TracebackType | None
) -> None:
    traceback_info = Traceback.from_tuple(type_, value, traceback)
    visualize_traceback(traceback_info)


def visualize_traceback(
    traceback: Traceback | None = None, exit_after: bool = True, repeat: bool = True
) -> None:
    """
    Can be called on any given moment to visualize the current stack trace
    param exit: stop execution after visualizing stack trace
    """
    if traceback is None:
        traceback = Traceback()
    context.config.exit_after = exit_after
    context.config.repeat = repeat
    PowerTrace(traceback).visualize_traceback()


def install() -> None:
    sys.excepthook = excepthook
    threading.excepthook = threading_excepthook
