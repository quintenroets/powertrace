from powertrace.main import main


def test_install_hooks() -> None:
    main.install_traceback_hooks()
