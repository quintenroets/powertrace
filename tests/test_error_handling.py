import os

import pexpect
import tbhandler
from superpathlib import Path


def test_error_handling() -> None:
    tbhandler.install()
    # make visualization in current tab
    os.environ.pop("DISPLAY", None)
    process = pexpect.spawn("python -c 'raise Exception'")
    process.expect(".*Exception.*")


def test_exception_file_open() -> None:
    tbhandler.install()
    process = pexpect.spawn(f"ask_open_exception_file {Path.draft}")
    process.sendline("")
    process.expect(pexpect.EOF)
