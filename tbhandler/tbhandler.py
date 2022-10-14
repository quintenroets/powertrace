import sys
import threading

from .exc_info import ExcInfo


def threading_excepthook(info: threading.ExceptHookArgs):
    ExcInfo(info.exc_type, info.exc_value, info.exc_traceback).show()


def excepthook(exc_type, exc_value, exc_traceback):
    ExcInfo(exc_type, exc_value, exc_traceback).show()


def show(exc_info: ExcInfo = None, exit_after: bool = True, repeat: bool = True):
    """
    Can be called on any given moment to visualize the current stack trace
    param exit: stop execution after visualizing stack trace
    """
    if exc_info is None:
        exc_info = ExcInfo(exit_after=exit_after, repeat=repeat)
    exc_info.show()


def install():
    sys.excepthook = excepthook
    threading.excepthook = threading_excepthook
