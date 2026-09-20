import subprocess
import sys
import threading
from unittest.mock import MagicMock, patch

import pytest
from rich.traceback import Traceback

import powertrace
from powertrace.handler import handle


@pytest.fixture
def installed_hooks(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "excepthook", sys.excepthook)
    monkeypatch.setattr(threading, "excepthook", threading.excepthook)
    powertrace.install_traceback_hooks()


@pytest.mark.usefixtures("installed_hooks")
@patch("powertrace.handler.handle")
def test_except_hook(mocked_handle: MagicMock) -> None:
    sys.excepthook(ValueError, ValueError(), None)
    mocked_handle.assert_called_once()


@pytest.mark.usefixtures("installed_hooks")
@patch("powertrace.main.install_powertrace_hooks")
def test_interrupt_except_hook(mocked_install: MagicMock) -> None:
    sys.excepthook(KeyboardInterrupt, KeyboardInterrupt(), None)
    mocked_install.assert_not_called()


@pytest.mark.usefixtures("installed_hooks")
@patch("powertrace.handler.handle")
def test_threading_except_hook(mocked_handle: MagicMock) -> None:
    args = threading.ExceptHookArgs((ValueError, ValueError(), None, None))
    threading.excepthook(args)
    mocked_handle.assert_called_once()


@pytest.mark.parametrize("full_traceback", [True, False])
@patch.object(Traceback, "from_exception", wraps=Traceback.from_exception)
def test_show_locals(
    mocked_from_exception: MagicMock,
    full_traceback: bool,  # noqa: FBT001
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("FULL_TRACEBACK", str(full_traceback).lower())
    handle(RuntimeError())
    assert mocked_from_exception.call_args.kwargs["show_locals"] == full_traceback


@patch.object(Traceback, "from_exception", side_effect=RuntimeError)
def test_exception_recovery(
    mocked_from_exception: MagicMock,
    capsys: pytest.CaptureFixture[str],
) -> None:
    handle(ValueError())
    assert mocked_from_exception.call_count == 2  # noqa: PLR2004
    assert "ValueError" in capsys.readouterr().err


@patch("powertrace.handler.print_rich_exception")
def test_current_exception(mocked_print_rich_exception: MagicMock) -> None:
    try:
        raise ValueError  # noqa: TRY301
    except ValueError:
        powertrace.visualize_traceback()
    mocked_print_rich_exception.assert_called_once()


def test_without_current_exception(capsys: pytest.CaptureFixture[str]) -> None:
    powertrace.visualize_traceback()
    assert not capsys.readouterr().err


@pytest.mark.parametrize("interactive", [True, False])
@patch("pdb.post_mortem")
def test_post_mortem(
    mocked_post_mortem: MagicMock,
    interactive: bool,  # noqa: FBT001
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("POWERTRACE_DEBUG", "1")
    monkeypatch.setattr(sys.stdin, "isatty", lambda: interactive)
    handle(RuntimeError())
    assert mocked_post_mortem.called == interactive


class DerivedRecursionError(RecursionError):
    pass


@patch("powertrace.handler.print_exception")
def test_exception_subclass_handling(mocked_print_exception: MagicMock) -> None:
    handle(DerivedRecursionError())
    (exception,) = mocked_print_exception.call_args.args
    assert isinstance(exception, DerivedRecursionError)


message = "error message"
process_error = subprocess.CalledProcessError(1, "command", stderr=message.encode())


def test_subprocess_error(capsys: pytest.CaptureFixture[str]) -> None:
    handle(process_error)
    assert message in capsys.readouterr().err


def test_subprocess_error_context(capsys: pytest.CaptureFixture[str]) -> None:
    try:
        try:
            raise process_error
        except subprocess.CalledProcessError:
            raise RuntimeError  # noqa: B904
    except RuntimeError as error:
        handle(error)
    assert message in capsys.readouterr().err


def test_subprocess_error_cause(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(RuntimeError) as info:
        raise RuntimeError from process_error
    handle(info.value)
    assert message in capsys.readouterr().err
