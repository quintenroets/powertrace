import subprocess
import sys
from unittest.mock import MagicMock, patch

import pytest
from rich.traceback import Traceback

from powertrace.reporting import display, report_failure

message = "error message"
process_error = subprocess.CalledProcessError(1, "command", stderr=message.encode())


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


@pytest.mark.parametrize("interactive", [True, False])
@patch("pdb.post_mortem")
def test_post_mortem(
    mocked_post_mortem: MagicMock,
    interactive: bool,  # noqa: FBT001
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("POWERTRACE_DEBUG", "1")
    monkeypatch.setattr(sys.stdin, "isatty", lambda: interactive)
    report_failure(RuntimeError())
    assert mocked_post_mortem.called == interactive


class DerivedRecursionError(RecursionError):
    pass


@patch("powertrace.reporting.print_exception")
def test_exception_subclass_handling(mocked_print_exception: MagicMock) -> None:
    display(DerivedRecursionError())
    (exception,) = mocked_print_exception.call_args.args
    assert isinstance(exception, DerivedRecursionError)


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
