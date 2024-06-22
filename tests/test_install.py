import powertrace


def test_install_hooks() -> None:
    powertrace.install_traceback_hooks()
