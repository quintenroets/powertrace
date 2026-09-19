import os
import sys
import threading
from unittest.mock import MagicMock, patch

import pytest

import powertrace
from powertrace.powertrace.install import excepthook
from powertrace.powertrace.powertrace import PowerTrace
from powertrace.powertrace.visualizer import TraceVisualizer


@pytest.fixture(autouse=True)
def reset_traceback_handled() -> None:
    PowerTrace.traceback_handled = False


def test_install_hooks() -> None:
    powertrace.install_traceback_hooks()


@patch.object(PowerTrace, "visualize_traceback")
def test_except_hook(mocked_visualize: MagicMock) -> None:
    powertrace.install_traceback_hooks()
    sys.excepthook(ValueError, ValueError(), None)
    mocked_visualize.assert_called_once()


@patch("powertrace.main.main.install_powertrace_hooks")
def test_interrupt_except_hook(mocked_install: MagicMock) -> None:
    powertrace.install_traceback_hooks()
    sys.excepthook(KeyboardInterrupt, KeyboardInterrupt(), None)
    mocked_install.assert_not_called()


@patch.object(PowerTrace, "visualize_traceback")
def test_threading_except_hook(mocked_visualize: MagicMock) -> None:
    powertrace.install_traceback_hooks()
    args = threading.ExceptHookArgs((ValueError, ValueError(), None, None))
    threading.excepthook(args)
    mocked_visualize.assert_called_once()


def verify_powertrace(exception_type: type[Exception] = RuntimeError) -> None:
    try:
        raise exception_type()  # noqa: TRY301
    except exception_type as exception:
        excepthook(exception_type, exception, exception.__traceback__)


@patch.dict(os.environ, {"FULL_TRACEBACK": "true"})
def test_powertrace(capsys: pytest.CaptureFixture[str]) -> None:
    verify_powertrace()
    assert capsys.readouterr().err


@patch.object(PowerTrace, "_visualize_traceback", side_effect=RuntimeError)
def test_exception_recovery(mocked_visualize: MagicMock) -> None:
    verify_powertrace()
    mocked_visualize.assert_called_once()


@patch.object(TraceVisualizer, "visualize_traceback_atomic", side_effect=RuntimeError)
def test_atomic_exception_recovery(mocked_visualize: MagicMock) -> None:
    verify_powertrace()
    mocked_visualize.assert_called()


@patch.object(TraceVisualizer, "visualize_traceback_atomic")
def test_repeat(mocked_visualize: MagicMock) -> None:
    try:
        raise ValueError  # noqa: TRY301
    except ValueError:
        powertrace.visualize_traceback()
        powertrace.visualize_traceback()
        powertrace.visualize_traceback(repeat=False)
    assert mocked_visualize.call_count == 2  # noqa: PLR2004


def test_without_current_exception(capsys: pytest.CaptureFixture[str]) -> None:
    powertrace.visualize_traceback()
    assert not capsys.readouterr().err


@patch("pdb.post_mortem")
@patch("sys.stdin.isatty", new=MagicMock(return_value=True))
@patch.dict(os.environ, {"POWERTRACE_DEBUG": "1"})
def test_post_mortem(mocked_post_mortem: MagicMock) -> None:
    verify_powertrace()
    mocked_post_mortem.assert_called_once()


@patch("sys.__excepthook__")
def test_recursion_error_handling(mocked_excepthook: MagicMock) -> None:
    verify_powertrace(exception_type=RecursionError)
    type_, value, traceback = mocked_excepthook.call_args.args
    expected = (RecursionError, RecursionError, value.__traceback__)
    assert (type_, type(value), traceback) == expected


@patch.object(TraceVisualizer, "disable_show_locals", new=True)
def test_show_locals() -> None:
    verify_powertrace()
