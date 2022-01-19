import sys
import _thread as thread

"""
This file is executed before every script so performance is critical.
The hooks below are never called for most scripts, so we only install them when they are needed. 
Lazy importing & installing limits total overhead of this complete file to nanosecond scale.
"""


sys_excepthook = sys.excepthook
thread_excepthook = thread._excepthook


def is_notebook():
    try:
        notebook = get_ipython().__class__.__name__ == 'ZMQInteractiveShell'
    except NameError:
        notebook = False
    return notebook


def install_tbhandler():
    """
    Reset to default excepthandlers when working in a notebook
    """
    if is_notebook():
        sys.excepthook = sys_excepthook
        thread._excepthook = thread_excepthook
    else:
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


sys.excepthook = excepthook
sys.displayhook = displayhook
thread._excepthook = threading_excepthook
