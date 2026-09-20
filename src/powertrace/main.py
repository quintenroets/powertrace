"""
Can be included in sitecustomize files.

In that case, the code below is executed before every script. As a
result, its runtime performance is critical. The hooks and functions
below are never called for most scripts. We only import the handler when
it is needed. Lazy imports limit the total overhead of this file to the
microseconds scale.
"""

import _thread
import sys

TYPE_CHECKING = False

if TYPE_CHECKING:
    import threading
    from types import TracebackType


def visualize_traceback(*, exit_after: bool = True) -> None:
    """
    Visualize the current traceback.
    """
    from . import handler  # noqa: PLC0415

    exception = sys.exception()
    if exception is not None:
        handler.handle(exception, exit_after=exit_after)


def excepthook(
    type_: type[BaseException],
    value: BaseException,
    _traceback: "TracebackType | None",
) -> None:
    # importing libraries clears interpreter's interrupt exit status
    if not issubclass(type_, KeyboardInterrupt):
        from . import handler  # noqa: PLC0415

        handler.handle(value)


def threading_excepthook(args: "threading.ExceptHookArgs") -> None:
    from typing import cast  # noqa: PLC0415

    from . import handler  # noqa: PLC0415

    handler.handle(cast("BaseException", args.exc_value))


def install_traceback_hooks() -> None:
    sys.excepthook = excepthook
    if "threading" in sys.modules:
        import threading  # noqa: PLC0415

        threading.excepthook = threading_excepthook
    else:
        # threading copies _thread._excepthook into its excepthook at import time
        _thread._excepthook = threading_excepthook  # noqa: SLF001
