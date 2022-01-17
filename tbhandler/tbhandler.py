import sys


def errorhandler(exc_type, exc_value, traceback):
    if exc_type != KeyboardInterrupt:
        show(exc_type, exc_value, traceback)


def show(exc_type=None, exc_value=None, traceback=None):
    """
    most of the time no exception => save time by only importing on exception
    """

    import cli

    from plib import Path
    from rich.console import Console
    from rich.traceback import Traceback

    log_file = Path.assets / '.error.txt'

    traceback = Traceback.from_exception(exc_type, exc_value, traceback) if exc_type else Traceback()
    with log_file.open('w') as fp:
        console = Console(file=fp, record=True, force_terminal=True)
        console.print(traceback)
        console.save_text(log_file.with_stem('error'))

    process = cli.start(f'cat {log_file}; read', console=True)
    process.communicate()  # make sure opening cli has finished before exiting


def install():
    sys.excepthook = errorhandler
