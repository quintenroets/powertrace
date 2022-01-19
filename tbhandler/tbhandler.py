import cli
import sys
import _thread as thread
import threading

from plib import Path
from rich.console import Console
from rich.traceback import Traceback

tbs_handled = set({})
tb_mutex = threading.Lock()


def threading_excepthook(info):
    return excepthook(info.exc_type, info.exc_value, info.exc_traceback)


def excepthook(exc_type, exc_value, traceback):
    if exc_type not in (KeyboardInterrupt, SystemExit):
        with tb_mutex:
            if not tbs_handled:  # only visualize the first traceback
                tbs_handled.add(traceback)
                show(exc_type, exc_value, traceback)


def show(exc_type=None, exc_value=None, traceback=None, exit=True):
    """
    Can be called on any given moment to visualize the current stack trace
    param exit: stop execution after visualizing stack trace
    """
    log_file = Path.assets / '.error.txt'

    traceback = Traceback.from_exception(exc_type, exc_value, traceback, show_locals=True) if exc_type else Traceback()
    with log_file.open('w') as fp:
        console = Console(file=fp, record=True, force_terminal=True)
        console.print(traceback)
        console.save_text(log_file.with_stem('error'))

    process = cli.start(f'cat {log_file}; read', console=True)
    process.communicate()  # make sure opening cli has finished before exiting
    if exit:
        sys.exit(1)  # stop execution after error in threads as well


def install():
    sys.excepthook = excepthook
    thread._excepthook = threading_excepthook
