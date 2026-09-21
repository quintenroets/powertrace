"""Lazy imports let sitecustomize import this module at negligible cost."""

import _thread
import atexit
import os
import sys

TYPE_CHECKING = False

if TYPE_CHECKING:
    import threading
    from types import TracebackType

failed = False


def show_exception() -> None:
    exception = sys.exception()
    if exception is not None:
        from . import reporting  # noqa: PLC0415

        reporting.display(exception)


def install() -> None:
    sys.excepthook = excepthook
    atexit.register(exit_if_failed)
    if "threading" in sys.modules:
        import threading  # noqa: PLC0415

        threading.excepthook = threading_excepthook
    else:
        # threading copies _thread._excepthook into its excepthook at import time
        _thread._excepthook = threading_excepthook  # noqa: SLF001


def excepthook(
    type_: type[BaseException],
    value: BaseException,
    _traceback: "TracebackType | None",
) -> None:
    # importing libraries clears interpreter's interrupt exit status
    if not issubclass(type_, KeyboardInterrupt):
        from . import reporting  # noqa: PLC0415

        reporting.report_failure(value)


def threading_excepthook(args: "threading.ExceptHookArgs") -> None:
    global failed  # noqa: PLW0603
    if not issubclass(args.exc_type, KeyboardInterrupt | SystemExit):
        from typing import cast  # noqa: PLC0415

        from . import reporting  # noqa: PLC0415

        if not cast("threading.Thread", args.thread).daemon:
            failed = True
        reporting.report_failure(cast("BaseException", args.exc_value))


def exit_if_failed() -> None:
    if failed:
        sys.stdout.flush()
        sys.stderr.flush()
        os._exit(1)
