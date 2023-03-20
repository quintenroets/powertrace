import sys

import cli


def main():
    path = sys.argv[1]
    open_file = cli.confirm("Open file?", default=False)
    if open_file:
        pycharm_is_open = cli.is_success("xdotool search --onlyvisible pycharm")
        opener = "pycharm-professional" if pycharm_is_open else "kate"
        cli.run(opener, path, wait=False)
    sys.exit(open_file)
