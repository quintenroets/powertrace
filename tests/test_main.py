import sys
import threading
from unittest.mock import MagicMock, patch

import pytest

import powertrace
from powertrace.context import Context, context
from powertrace.notebook import load_ipython_extension
from powertrace.powertrace.install import excepthook
from powertrace.powertrace.powertrace import PowerTrace
from powertrace.powertrace.visualizer import TraceVisualizer

new_tab_context = patch.object(Context, "can_visualize_in_new_tab", new=True)
no_new_tab_context = patch.object(Context, "can_visualize_in_new_tab", new=False)


@pytest.fixture(autouse=True)
def reset_traceback_handled() -> None:
    context._traceback_handled = False  # noqa: SLF001


def test_install_hooks() -> None:
    powertrace.install_traceback_hooks()


def test_extension() -> None:
    load_ipython_extension(0)


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


def verify_powertrace(exception_type: type[Exception] = RuntimeError) -> None:
    try:
        raise exception_type()  # noqa: TRY301
    except exception_type as exception:
        excepthook(exception_type, exception_type(), exception.__traceback__)


@patch("cli.run_in_console")
@new_tab_context
def test_powertrace(mocked_run: MagicMock) -> None:
    verify_powertrace()
    mocked_run.assert_called_once()


@patch.object(PowerTrace, "_visualize_traceback", side_effect=RuntimeError)
@new_tab_context
def test_exception_recovery(mocked_visualize: MagicMock) -> None:
    verify_powertrace()
    mocked_visualize.assert_called_once()


@patch("cli.run_in_console")
@patch.object(TraceVisualizer, "visualize_traceback_atomic", side_effect=RuntimeError)
@new_tab_context
def test_atomic_exception_recovery(
    mocked_visualize: MagicMock,
    mocked_run: MagicMock,
) -> None:
    verify_powertrace()
    mocked_run.assert_not_called()
    mocked_visualize.assert_called()


@patch("cli.run_in_console")
@new_tab_context
def test_only_visualized_once(mocked_run: MagicMock) -> None:
    try:
        raise ValueError  # noqa: TRY301
    except ValueError:
        powertrace.visualize_traceback()
        powertrace.visualize_traceback(repeat=False)
    mocked_run.assert_called_once()


@patch("cli.run")
@patch("cli.run_in_console", side_effect=FileNotFoundError)
@new_tab_context
def test_fallback_to_visualize_in_active_tab(
    mocked_run_in_console: MagicMock,
    mocked_run: MagicMock,
) -> None:
    verify_powertrace()
    mocked_run.assert_called_once()
    mocked_run_in_console.assert_called_once()


@patch("cli.run")
@patch("pdb.post_mortem")
@patch.object(Context, "should_debug", new=True)
@no_new_tab_context
def test_visualize_in_active_tab(
    mocked_post_mortem: MagicMock,
    mocked_run: MagicMock,
) -> None:
    # make visualization in current tab
    verify_powertrace()
    mocked_run.assert_called_once()
    mocked_post_mortem.assert_called_once()


@no_new_tab_context
def test_recursion_error_handling() -> None:
    verify_powertrace(exception_type=RecursionError)


@no_new_tab_context
@patch.object(TraceVisualizer, "disable_show_locals", new=True)
def test_show_locals() -> None:
    verify_powertrace()


@patch("os.environ", new={"DISPLAY": ":0.0"})
def test_can_visualize_in_same_tab() -> None:
    assert context.can_visualize_in_new_tab
