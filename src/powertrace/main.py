"""
Can be included in sitecustomize files.

In that case, the code below is executed before every script. As a
result, its runtime performance is critical. The hooks and functions
below are never called for most scripts. We only install them when they
are needed. Lazy imports & installs limit the total overhead of this
file to the microseconds scale.
"""

import _thread
import sys
from typing import Any


def visualize_traceback(*, exit_after: bool = True) -> None:
    """
    Visualize the current traceback.
    """
    from . import handler  # noqa: PLC0415

    exception = sys.exception()
    if exception is not None:
        handler.handle(exception, exit_after=exit_after)


def install_powertrace_hooks() -> None:
    from . import handler  # noqa: PLC0415

    handler.install_traceback_hooks()


def excepthook(type_: type[BaseException], *args: Any) -> None:
    # importing libraries clears interpreter's interrupt exit status
    if not issubclass(type_, KeyboardInterrupt):
        install_powertrace_hooks()
        sys.excepthook(type_, *args)


def threading_excepthook(*args: Any) -> None:
    import threading  # noqa: PLC0415

    install_powertrace_hooks()
    threading.excepthook(*args)


def install_traceback_hooks() -> None:
    sys.excepthook = excepthook
    if "threading" in sys.modules:
        import threading  # noqa: PLC0415

        threading.excepthook = threading_excepthook
    else:
        # threading copies _thread._excepthook into its excepthook at import time
        _thread._excepthook = threading_excepthook  # noqa: SLF001
