import sys
import threading
from types import TracebackType
from typing import cast

from .powertrace import handle


def threading_excepthook(args: threading.ExceptHookArgs) -> None:
    value = cast("BaseException", args.exc_value)
    handle(value, repeat=False)


def excepthook(
    _type: type[BaseException],
    value: BaseException,
    _traceback: TracebackType | None,
) -> None:
    handle(value, repeat=False)


def install_traceback_hooks() -> None:
    sys.excepthook = excepthook
    threading.excepthook = threading_excepthook
