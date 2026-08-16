from powertrace.context import context

from .powertrace import PowerTrace
from .traceback import Traceback


def visualize_traceback(
    traceback: Traceback | None = None,
    *,
    exit_after: bool = True,
    repeat: bool = True,
) -> None:
    if traceback is None:
        traceback = Traceback()
    context.config.exit_after = exit_after
    context.config.repeat = repeat
    PowerTrace(traceback).visualize_traceback()
