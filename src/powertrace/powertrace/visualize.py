from ..context import context
from .powertrace import PowerTrace
from .traceback import Traceback


def visualize_traceback(
    traceback: Traceback | None = None, exit_after: bool = True, repeat: bool = True
) -> None:
    """
    Can be called on any given moment to visualize the current stack trace
    param exit: stop execution after visualizing stack trace
    """
    if traceback is None:
        traceback = Traceback()
    context.config.exit_after = exit_after
    context.config.repeat = repeat
    PowerTrace(traceback).visualize_traceback()
