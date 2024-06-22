import os

import pexpect
import powertrace


def test_error_handling() -> None:
    powertrace.install_traceback_hooks()
    # make visualization in current tab
    os.environ.pop("DISPLAY", None)
    process = pexpect.spawn("python -c 'raise Exception'")
    process.expect(".*Exception.*")
