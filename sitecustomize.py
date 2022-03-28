import builtins
import sys

import _thread as thread


"""
This file is executed before every script so performance is critical.
The hooks and builtins below are never called for most scripts, so we only install them when they are needed. 
Lazy importing & installing limits total overhead of this complete file to nanosecond scale.
"""


def install_tbhandler():
    import tbhandler

    tbhandler.install()


def excepthook(*args):
    install_tbhandler()
    sys.excepthook(*args)


def threading_excepthook(*args):
    install_tbhandler()
    thread._excepthook(*args)


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
    thread._excepthook = threading_excepthook

"""
ADD NEW BUILTINS: only for quick debugging: always import properly in projects where it is used permanently
"""


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
builtins.Timer = Timer
builtins.timing = timing
