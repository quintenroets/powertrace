import _thread
import importlib
import subprocess
import sys
import threading
from unittest.mock import MagicMock, patch

import pytest
from rich.traceback import Traceback

import powertrace
from powertrace.reporting import display, report_failure


@pytest.fixture
def installed_hooks(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "excepthook", sys.excepthook)
    monkeypatch.setattr(threading, "excepthook", threading.excepthook)
    powertrace.install_traceback_hooks()


@pytest.mark.usefixtures("installed_hooks")
@patch("powertrace.reporting.report_failure")
def test_except_hook(mocked_report: MagicMock) -> None:
    error = ValueError()
    sys.excepthook(ValueError, error, None)
    mocked_report.assert_called_once_with(error, abort=False)


@pytest.mark.usefixtures("installed_hooks")
def test_interrupt_except_hook(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delitem(sys.modules, "powertrace.reporting")
    sys.excepthook(KeyboardInterrupt, KeyboardInterrupt(), None)
    assert "powertrace.reporting" not in sys.modules


@pytest.mark.usefixtures("installed_hooks")
@patch("powertrace.reporting.report_failure")
def test_threading_except_hook(mocked_report: MagicMock) -> None:
    error = ValueError()
    args = threading.ExceptHookArgs((ValueError, error, None, None))
    threading.excepthook(args)
    mocked_report.assert_called_once_with(error, abort=True)


def test_hooks_installed_without_threading_import(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(sys, "excepthook", sys.excepthook)
    monkeypatch.setattr(_thread, "_excepthook", _thread._excepthook)  # noqa: SLF001
    monkeypatch.delitem(sys.modules, "threading")
    powertrace.install_traceback_hooks()
    assert "threading" not in sys.modules
    reimported = importlib.import_module("threading")
    assert reimported.excepthook is powertrace.main.threading_excepthook


@pytest.mark.parametrize("full_traceback", [True, False])
@patch.object(Traceback, "from_exception", wraps=Traceback.from_exception)
def test_show_locals(
    mocked_from_exception: MagicMock,
    full_traceback: bool,  # noqa: FBT001
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("FULL_TRACEBACK", str(full_traceback).lower())
    display(RuntimeError())
    assert mocked_from_exception.call_args.kwargs["show_locals"] == full_traceback


@patch.object(Traceback, "from_exception", side_effect=RuntimeError)
def test_exception_recovery(
    mocked_from_exception: MagicMock,
    capsys: pytest.CaptureFixture[str],
) -> None:
    display(ValueError())
    assert mocked_from_exception.call_count == 2  # noqa: PLR2004
    assert "ValueError" in capsys.readouterr().err


@patch("powertrace.reporting.print_rich_exception")
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
    report_failure(RuntimeError(), abort=False)
    assert mocked_post_mortem.called == interactive


class DerivedRecursionError(RecursionError):
    pass


@patch("powertrace.reporting.print_exception")
def test_exception_subclass_handling(mocked_print_exception: MagicMock) -> None:
    display(DerivedRecursionError())
    (exception,) = mocked_print_exception.call_args.args
    assert isinstance(exception, DerivedRecursionError)


message = "error message"
process_error = subprocess.CalledProcessError(1, "command", stderr=message.encode())


def test_subprocess_error(capsys: pytest.CaptureFixture[str]) -> None:
    display(process_error)
    assert message in capsys.readouterr().err


def test_subprocess_error_chain(capsys: pytest.CaptureFixture[str]) -> None:
    try:
        try:
            raise RuntimeError from process_error  # noqa: TRY301
        except RuntimeError:
            raise ValueError  # noqa: B904
    except ValueError as error:
        display(error)
    assert message in capsys.readouterr().err
