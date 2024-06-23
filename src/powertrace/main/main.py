"""This file can be imported included in sitecustomize files.

In that case, the code below is executed before every script. As a
result, its runtime performance is critical. The hooks and functions
below are never called for most scripts. We only install them when they
are needed. Lazy imports & installs limit the total overhead of this
file to the microseconds scale.
"""

import sys
import threading
from typing import Any


def visualize_traceback(exit_after: bool = True, repeat: bool = True) -> None:
    """
    Visualize the current traceback.
    """
    from powertrace.powertrace.visualize import visualize_traceback

    visualize_traceback(exit_after=exit_after, repeat=repeat)


def install_powertrace_hooks() -> None:
    from powertrace.powertrace import install

    install.install_traceback_hooks()


def excepthook(*args: Any) -> None:
    install_powertrace_hooks()
    sys.excepthook(*args)


def threading_excepthook(*args: Any) -> None:
    install_powertrace_hooks()
    threading.excepthook(*args)


def install_traceback_hooks() -> None:
    sys.excepthook = excepthook
    threading.excepthook = threading_excepthook
