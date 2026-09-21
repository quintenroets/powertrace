import _thread
import importlib
import os
import sys
import threading
from unittest.mock import MagicMock, patch

import pytest

import powertrace


@pytest.fixture
def installed_hooks(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "excepthook", sys.excepthook)
    monkeypatch.setattr(threading, "excepthook", threading.excepthook)
    monkeypatch.setattr(powertrace.hooks, "failed", False)
    powertrace.install()


@pytest.mark.usefixtures("installed_hooks")
@patch("powertrace.reporting.report_failure")
def test_except_hook(mocked_report: MagicMock) -> None:
    error = ValueError()
    sys.excepthook(ValueError, error, None)
    mocked_report.assert_called_once_with(error)


@pytest.mark.usefixtures("installed_hooks")
def test_interrupt_except_hook(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delitem(sys.modules, "powertrace.reporting")
    sys.excepthook(KeyboardInterrupt, KeyboardInterrupt(), None)
    assert "powertrace.reporting" not in sys.modules


@pytest.mark.usefixtures("installed_hooks")
@patch("powertrace.reporting.report_failure")
def test_threading_except_hook(mocked_report: MagicMock) -> None:
    error = ValueError()
    thread = threading.Thread(daemon=False)
    args = threading.ExceptHookArgs((ValueError, error, None, thread))
    threading.excepthook(args)
    mocked_report.assert_called_once_with(error)
    assert powertrace.hooks.failed


def test_exit_if_failed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(powertrace.hooks, "failed", True)
    mocked_exit = MagicMock()
    monkeypatch.setattr(os, "_exit", mocked_exit)
    powertrace.hooks.exit_if_failed()
    mocked_exit.assert_called_once_with(1)


def test_hooks_installed_without_threading_import(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(sys, "excepthook", sys.excepthook)
    monkeypatch.setattr(_thread, "_excepthook", _thread._excepthook)  # noqa: SLF001
    monkeypatch.delitem(sys.modules, "threading")
    powertrace.install()
    assert "threading" not in sys.modules
    reimported = importlib.import_module("threading")
    assert reimported.excepthook is powertrace.hooks.threading_excepthook


@patch("powertrace.reporting.print_rich_exception")
def test_current_exception(mocked_print_rich_exception: MagicMock) -> None:
    try:
        raise ValueError  # noqa: TRY301
    except ValueError:
        powertrace.show_exception()
    mocked_print_rich_exception.assert_called_once()


def test_without_current_exception(capsys: pytest.CaptureFixture[str]) -> None:
    powertrace.show_exception()
    assert not capsys.readouterr().err
