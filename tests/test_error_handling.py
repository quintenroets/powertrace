import os

import pexpect
from superpathlib import Path

import tbhandler


def test_error_handling():
    tbhandler.install()
    # make visualization in current tab
    os.environ.pop("DISPLAY", None)
    process = pexpect.spawn("python -c 'raise Exception'")
    process.expect(".*Exception.*")


def test_exception_file_open():
    tbhandler.install()
    process = pexpect.spawn(f"ask_open_exception_file {Path.draft}")
    process.sendline("")
    process.expect(pexpect.EOF)
