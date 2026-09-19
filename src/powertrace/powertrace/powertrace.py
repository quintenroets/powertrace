import os
import sys
import threading
import traceback
from dataclasses import dataclass
from typing import ClassVar

from .visualizer import TraceVisualizer


@dataclass
class PowerTrace:
    exception: BaseException
    exit_after: bool = True
    repeat: bool = True
    skipped_exception_types: tuple[type[BaseException], ...] = (
        KeyboardInterrupt,
        SystemExit,
        RecursionError,
        BrokenPipeError,
    )
    use_original_handler: tuple[type[BaseException], ...] = (RecursionError,)
    visualization_mutex: ClassVar[threading.Lock] = threading.Lock()
    traceback_handled: ClassVar[bool] = False

    def visualize_traceback(self) -> None:
        try:
            self._visualize_traceback()
        except Exception:  # noqa: BLE001
            # use builtin traceback visualization when custom visualization fails
            traceback.print_exc()

    def _visualize_traceback(self) -> None:
        type_ = type(self.exception)
        if type_ not in self.skipped_exception_types:
            with PowerTrace.visualization_mutex:
                # only visualize the first traceback for crashing threads
                self.visualize_traceback_atomic()
        elif type_ in self.use_original_handler:
            sys.__excepthook__(type_, self.exception, self.exception.__traceback__)

    def visualize_traceback_atomic(self) -> None:
        is_main_thread = threading.current_thread() is threading.main_thread()
        if not PowerTrace.traceback_handled or (self.repeat and is_main_thread):
            PowerTrace.traceback_handled = True
            self._visualize_traceback_atomic()
            if self.exit_after and not is_main_thread:  # pragma: nocover
                os._exit(1)

    def _visualize_traceback_atomic(self) -> None:
        visualizer = TraceVisualizer(self.exception)
        try:
            visualizer.visualize_traceback_atomic()
        except Exception:  # noqa: BLE001
            visualizer.disable_show_locals = True
            try:
                visualizer.visualize_traceback_atomic()
            except Exception as exception:  # noqa: BLE001
                # visualize failure to construct message
                visualizer.exception = exception
                visualizer.visualize_traceback_atomic()
