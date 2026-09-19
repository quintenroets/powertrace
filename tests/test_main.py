import os
import sys
import threading
from unittest.mock import MagicMock, patch

import pytest
from rich.traceback import Traceback

import powertrace
from powertrace.handler import excepthook, handled


@pytest.fixture(autouse=True)
def reset_handled() -> None:
    handled.clear()


def test_install_hooks() -> None:
    powertrace.install_traceback_hooks()


@patch("powertrace.handler.handle")
def test_except_hook(mocked_handle: MagicMock) -> None:
    powertrace.install_traceback_hooks()
    sys.excepthook(ValueError, ValueError(), None)
    mocked_handle.assert_called_once()


@patch("powertrace.main.install_powertrace_hooks")
def test_interrupt_except_hook(mocked_install: MagicMock) -> None:
    powertrace.install_traceback_hooks()
    sys.excepthook(KeyboardInterrupt, KeyboardInterrupt(), None)
    mocked_install.assert_not_called()


@patch("powertrace.handler.handle")
def test_threading_except_hook(mocked_handle: MagicMock) -> None:
    powertrace.install_traceback_hooks()
    args = threading.ExceptHookArgs((ValueError, ValueError(), None, None))
    threading.excepthook(args)
    mocked_handle.assert_called_once()


def verify_powertrace(exception_type: type[Exception] = RuntimeError) -> None:
    try:
        raise exception_type()  # noqa: TRY301
    except exception_type as error:
        exception = error
    excepthook(exception_type, exception, exception.__traceback__)


@patch.dict(os.environ, {"FULL_TRACEBACK": "true"})
def test_powertrace(capsys: pytest.CaptureFixture[str]) -> None:
    verify_powertrace()
    assert capsys.readouterr().err


@patch.object(Traceback, "from_exception", side_effect=RuntimeError)
def test_exception_recovery(
    mocked_from_exception: MagicMock,
    capsys: pytest.CaptureFixture[str],
) -> None:
    verify_powertrace(ValueError)
    assert mocked_from_exception.call_count == 2  # noqa: PLR2004
    assert "ValueError" in capsys.readouterr().err


@patch("powertrace.handler.print_rich_exception")
def test_repeat(mocked_print_rich_exception: MagicMock) -> None:
    try:
        raise ValueError  # noqa: TRY301
    except ValueError:
        powertrace.visualize_traceback()
        powertrace.visualize_traceback()
        powertrace.visualize_traceback(repeat=False)
    assert mocked_print_rich_exception.call_count == 2  # noqa: PLR2004


def test_without_current_exception(capsys: pytest.CaptureFixture[str]) -> None:
    powertrace.visualize_traceback()
    assert not capsys.readouterr().err


@patch("pdb.post_mortem")
@patch("sys.stdin.isatty", new=MagicMock(return_value=True))
@patch.dict(os.environ, {"POWERTRACE_DEBUG": "1"})
def test_post_mortem(mocked_post_mortem: MagicMock) -> None:
    verify_powertrace()
    mocked_post_mortem.assert_called_once()


class DerivedRecursionError(RecursionError):
    pass


@patch("powertrace.handler.print_exception")
def test_exception_subclass_handling(mocked_print_exception: MagicMock) -> None:
    verify_powertrace(exception_type=DerivedRecursionError)
    (exception,) = mocked_print_exception.call_args.args
    assert isinstance(exception, DerivedRecursionError)
