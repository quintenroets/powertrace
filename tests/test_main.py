import os
import sys
import threading
from unittest.mock import MagicMock, patch

import powertrace
from powertrace.notebook import load_ipython_extension


def test_install_hooks() -> None:
    powertrace.install_traceback_hooks()


def test_extension() -> None:
    load_ipython_extension(0)


@patch("cli.run_in_console")
def test_powertrace(mocked_run: MagicMock) -> None:
    os.environ["DISPLAY"] = ":0.0"
    try:
        raise ValueError
    except ValueError:
        powertrace.visualize_traceback(repeat=False)
    mocked_run.assert_called_once()


@patch("cli.run_in_console")
def test_only_visualized_once(mocked_run: MagicMock) -> None:
    os.environ["DISPLAY"] = ":0.0"
    try:
        raise ValueError
    except ValueError:
        powertrace.visualize_traceback()
        powertrace.visualize_traceback(repeat=False)
    mocked_run.assert_called_once()


@patch("powertrace.powertrace.visualize.visualize_traceback")
def test_except_hook(mocked_visualize: MagicMock) -> None:
    powertrace.install_traceback_hooks()
    sys.excepthook(ValueError, ValueError(), None)
    mocked_visualize.assert_called_once()


@patch("powertrace.powertrace.visualize.visualize_traceback")
def test_threading_except_hook(mocked_visualize: MagicMock) -> None:
    powertrace.install_traceback_hooks()
    args = threading.ExceptHookArgs((ValueError, ValueError(), None, None))
    threading.excepthook(args)
    mocked_visualize.assert_called_once()


def test_visualize_in_active_tab() -> None:
    # make visualization in current tab
    os.environ.pop("DISPLAY", None)
    try:
        raise ValueError
    except ValueError:
        powertrace.visualize_traceback()
