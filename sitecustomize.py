import sys

"""
This file is executed before every script so performance is critical.
Lazily importing & installing limits overhead to nanosecond scale.
"""

def excepthook(*args):
    import tbhandler
    tbhandler.install()
    sys.excepthook(*args)


def displayhook(value):
    # only install after first display usage
    # save startup time for scripts that dont use display
    from rich import pretty
    pretty.install()
    sys.displayhook(value)


sys.displayhook = displayhook
sys.excepthook = excepthook
