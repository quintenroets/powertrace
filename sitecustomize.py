import builtins
import sys
import threading

from superpathlib import Path

"""
This file is executed before every script so performance is critical.
The hooks and builtins below are never called for most scripts,
so we only install them when they are needed.
Lazy imports & installs limit the total overhead of this file to the microseconds scale.
"""


def install_tbhandler():
    import tbhandler

    tbhandler.install()


def excepthook(*args):
    install_tbhandler()
    sys.excepthook(*args)


def threading_excepthook(*args):
    install_tbhandler()
    threading.excepthook(*args)


def displayhook(value):
    from rich import pretty

    pretty.install()
    sys.displayhook(value)


def is_notebook():
    try:
        notebook = get_ipython().__class__.__name__ == "ZMQInteractiveShell"
    except NameError:
        notebook = False
    return notebook


#  Notebook setup is done in separate extension
if not is_notebook():
    sys.excepthook = excepthook
    sys.displayhook = displayhook
    threading.excepthook = threading_excepthook

############################
# ADD NEW BUILTINS
# Only use for quick debugging.
# Always import properly in projects where it is used permanently.
############################


def pprint(*items):
    from rich import pretty

    for item in items:
        pretty.pprint(item)


class Timer:
    def __new__(cls, *args, **kwargs):
        from libs.timer import Timer

        builtins.Timer = Timer
        return builtins.Timer(*args, **kwargs)


def timing(function):
    from libs.timer import timing

    builtins.timing = timing
    return builtins.timing(function)


builtins.pprint = pprint
builtins.Path = Path
builtins.Timer = Timer
builtins.timing = timing
