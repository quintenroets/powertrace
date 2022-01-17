import sys
import tbhandler


def displayhook(value):
    # only install after first display usage
    # save startup time for scripts that dont use display
    from rich import pretty
    pretty.install()
    sys.displayhook(value)


tbhandler.install()
sys.displayhook = displayhook
