import sys

import cli


def main():
    path = sys.argv[1]
    open_file = cli.confirm("Open file?", default=False)
    if open_file:
        cli.urlopen(path)
