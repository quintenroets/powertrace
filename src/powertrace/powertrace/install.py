import sys
import threading
from types import TracebackType
from typing import cast

from .powertrace import PowerTrace


def threading_excepthook(args: threading.ExceptHookArgs) -> None:
    value = cast("BaseException", args.exc_value)
    PowerTrace(value, repeat=False).visualize_traceback()


def excepthook(
    _type: type[BaseException],
    value: BaseException,
    _traceback: TracebackType | None,
) -> None:
    PowerTrace(value, repeat=False).visualize_traceback()


def install_traceback_hooks() -> None:
    sys.excepthook = excepthook
    threading.excepthook = threading_excepthook
