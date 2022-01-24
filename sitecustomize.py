import builtins
import sys

import _thread as thread


"""
This file is executed before every script so performance is critical.
The hooks below are never called for most scripts, so we only install them when they are needed. 
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


def pprint(item):
    from rich import pretty

    builtins.pprint = pretty.pprint
    builtins.pprint(item)


#  Notebook setup is done in separate extension
if not is_notebook():
    sys.excepthook = excepthook
    sys.displayhook = displayhook
    thread._excepthook = threading_excepthook

builtins.pprint = pprint  # only for quick debugging: always import properly in projects where it is used permanently
