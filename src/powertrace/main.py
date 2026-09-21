"""
Can be included in sitecustomize files.

In that case, the code below is executed before every script. As a
result, its runtime performance is critical. The hooks and functions
below are never called for most scripts. We only import the reporting
module when it is needed. Lazy imports limit the total overhead of this
file to the microseconds scale.
"""

import _thread
import sys

TYPE_CHECKING = False

if TYPE_CHECKING:
    import threading
    from types import TracebackType


def visualize_traceback() -> None:
    """
    Visualize the current traceback.
    """
    exception = sys.exception()
    if exception is not None:
        from . import reporting  # noqa: PLC0415

        reporting.display(exception)


def excepthook(
    type_: type[BaseException],
    value: BaseException,
    _traceback: "TracebackType | None",
) -> None:
    # importing libraries clears interpreter's interrupt exit status
    if not issubclass(type_, KeyboardInterrupt):
        from . import reporting  # noqa: PLC0415

        reporting.report_failure(value, abort=False)


def threading_excepthook(args: "threading.ExceptHookArgs") -> None:
    if not issubclass(args.exc_type, KeyboardInterrupt | SystemExit):
        from typing import cast  # noqa: PLC0415

        from . import reporting  # noqa: PLC0415

        reporting.report_failure(cast("BaseException", args.exc_value), abort=True)


def install_traceback_hooks() -> None:
    sys.excepthook = excepthook
    if "threading" in sys.modules:
        import threading  # noqa: PLC0415

        threading.excepthook = threading_excepthook
    else:
        # threading copies _thread._excepthook into its excepthook at import time
        _thread._excepthook = threading_excepthook  # noqa: SLF001
