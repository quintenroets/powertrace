import sys
import threading
from types import TracebackType

from .powertrace import PowerTrace
from .traceback import Traceback


def threading_excepthook(info: threading.ExceptHookArgs) -> None:
    traceback_info = Traceback.from_info(info)
    PowerTrace(traceback_info, repeat=False).visualize_traceback()


def excepthook(
    type_: type[BaseException],
    value: BaseException,
    traceback: TracebackType | None,
) -> None:
    traceback_info = Traceback.from_tuple(type_, value, traceback)
    PowerTrace(traceback_info, repeat=False).visualize_traceback()


def install_traceback_hooks() -> None:
    sys.excepthook = excepthook
    threading.excepthook = threading_excepthook
