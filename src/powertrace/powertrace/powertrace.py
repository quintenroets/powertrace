import sys
import traceback
from dataclasses import dataclass
from typing import ClassVar, cast

from ..context import context
from .traceback import Traceback
from .visualizer import TraceVisualizer


@dataclass
class PowerTrace:
    traceback: Traceback
    tb_handled: ClassVar[bool] = False
    skipped_exception_types: tuple[type[BaseException] | None, ...] = (
        KeyboardInterrupt,
        SystemExit,
        RecursionError,
        BrokenPipeError,
    )
    use_original_handler: tuple[type[BaseException], ...] = (RecursionError,)

    def visualize_traceback(self) -> None:
        try:
            self._visualize_traceback()
        except Exception:  # noqa: E722
            # use builtin traceback visualization when custom visualization fails
            traceback.print_exc()

    def _visualize_traceback(self) -> None:
        if self.traceback.type_ not in self.skipped_exception_types:
            with context.visualization_mutex:
                # only visualize the first traceback for crashing threads
                self.visualize_traceback_atomic()
        elif self.traceback.type_ in self.use_original_handler:
            value = cast(BaseException, None)
            sys.__excepthook__(self.traceback.type_, value, self.traceback.traceback)

    def visualize_traceback_atomic(self) -> None:
        if not context.traceback_handled or context.repeat:
            context.set_traceback_handled()
            self._visualize_traceback_atomic()

    def _visualize_traceback_atomic(self) -> None:
        visualizer = TraceVisualizer(traceback=self.traceback)
        try:
            visualizer.visualize_traceback_atomic()
        except:  # noqa
            visualizer.disable_show_locals = True
            try:
                # try without locals when message construction fails
                visualizer.visualize_traceback_atomic()
            except Exception:
                # visualize failure to construct message
                visualizer.traceback = Traceback()
                visualizer.visualize_traceback_atomic()
