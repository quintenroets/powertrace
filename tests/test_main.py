import os
import sys
import threading
from collections.abc import Iterator
from contextlib import contextmanager
from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

import powertrace
from powertrace.powertrace import visualizer
from powertrace.powertrace.install import excepthook
from powertrace.powertrace.powertrace import PowerTrace
from powertrace.powertrace.visualizer import TraceVisualizer


@contextmanager
def window_server(*, output_is_observed: bool) -> Iterator[None]:
    with (
        patch.dict(os.environ, {"DISPLAY": ":0"}),
        patch.object(visualizer, "stream_is_observed", return_value=output_is_observed),
    ):
        yield


@pytest.fixture(autouse=True)
def reset_traceback_handled() -> None:
    PowerTrace.traceback_handled = False


@pytest.fixture(autouse=True)
def outside_ci(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)


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
        excepthook(exception_type, exception_type(), exception.__traceback__)


@patch("cli.run_in_new_tab")
@window_server(output_is_observed=False)
@patch.dict(os.environ, {"FULL_TRACEBACK": "true"})
def test_powertrace(mocked_run: MagicMock) -> None:
    verify_powertrace()
    mocked_run.assert_called_once()


@patch.object(PowerTrace, "_visualize_traceback", side_effect=RuntimeError)
@window_server(output_is_observed=False)
def test_exception_recovery(mocked_visualize: MagicMock) -> None:
    verify_powertrace()
    mocked_visualize.assert_called_once()


@patch("cli.run_in_new_tab")
@patch.object(TraceVisualizer, "visualize_traceback_atomic", side_effect=RuntimeError)
@window_server(output_is_observed=False)
def test_atomic_exception_recovery(
    mocked_visualize: MagicMock,
    mocked_run: MagicMock,
) -> None:
    verify_powertrace()
    mocked_run.assert_not_called()
    mocked_visualize.assert_called()


@patch("cli.run_in_new_tab")
@window_server(output_is_observed=False)
def test_repeat(mocked_run: MagicMock) -> None:
    try:
        raise ValueError  # noqa: TRY301
    except ValueError:
        powertrace.visualize_traceback()
        powertrace.visualize_traceback()
        powertrace.visualize_traceback(repeat=False)
    assert mocked_run.call_count == 2  # noqa: PLR2004


@patch("cli.run")
@patch("cli.run_in_new_tab", side_effect=FileNotFoundError)
@window_server(output_is_observed=False)
def test_fallback_to_visualize_in_active_tab(
    mocked_run_in_new_tab: MagicMock,
    mocked_run: MagicMock,
) -> None:
    verify_powertrace()
    mocked_run.assert_called_once()
    mocked_run_in_new_tab.assert_called_once()


@patch("cli.run")
@patch("pdb.post_mortem")
@patch("sys.stdin.isatty", new=MagicMock(return_value=True))
@patch.dict(os.environ, {"POWERTRACE_DEBUG": "1"})
@window_server(output_is_observed=True)
def test_visualize_in_active_tab(
    mocked_post_mortem: MagicMock,
    mocked_run: MagicMock,
) -> None:
    # make visualization in current tab
    verify_powertrace()
    mocked_run.assert_called_once()
    mocked_post_mortem.assert_called_once()


def test_recursion_error_handling() -> None:
    verify_powertrace(exception_type=RecursionError)


@window_server(output_is_observed=True)
@patch.object(TraceVisualizer, "disable_show_locals", new=True)
def test_show_locals() -> None:
    verify_powertrace()


def test_stream_to_file_is_observed(tmp_path: Path) -> None:
    with (tmp_path / "stream").open("w") as stream:
        assert visualizer.stream_is_observed(stream)


def test_stream_to_devnull_is_not_observed() -> None:
    with Path(os.devnull).open("w") as stream:
        assert not visualizer.stream_is_observed(stream)


def test_stream_without_fileno_is_not_observed() -> None:
    assert not visualizer.stream_is_observed(StringIO())
