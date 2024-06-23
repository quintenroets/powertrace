import sys
import threading
from types import TracebackType

from . import visualize
from .traceback import Traceback


def threading_excepthook(info: threading.ExceptHookArgs) -> None:
    traceback_info = Traceback.from_info(info)
    visualize.visualize_traceback(traceback_info, repeat=False)


def excepthook(
    type_: type[BaseException], value: BaseException, traceback: TracebackType | None
) -> None:
    traceback_info = Traceback.from_tuple(type_, value, traceback)
    visualize.visualize_traceback(traceback_info, repeat=False)


def install_traceback_hooks() -> None:
    sys.excepthook = excepthook
    threading.excepthook = threading_excepthook
