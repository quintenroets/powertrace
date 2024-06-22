import os
import sys
import threading
from dataclasses import dataclass
from functools import cached_property

from package_utils.context import Context as Context_

from ..models import Config


@dataclass
class Context(Context_[None, Config, None]):
    def __post_init__(self) -> None:
        self._traceback_handled = False

    @property
    def is_running_in_ci(self) -> bool:
        return "GITHUB_ACTIONS" in os.environ

    @property
    def show_full_traceback(self) -> bool:
        return os.environ.get("full_traceback", "false") != "false"

    @property
    def is_running_in_main_thread(self) -> bool:
        return threading.current_thread() is threading.main_thread()

    @property
    def repeat(self) -> bool:
        return self.config.repeat and self.is_running_in_main_thread

    @cached_property
    def visualization_mutex(self) -> threading.Lock:
        return threading.Lock()

    @property
    def traceback_handled(self) -> bool:
        return self._traceback_handled

    def set_traceback_handled(self) -> None:
        self._traceback_handled = True

    @property
    def should_debug(self) -> bool:
        return "POWERTRACE_DEBUG" in os.environ and sys.stdin.isatty()

    @property
    def can_visualize_in_new_tab(self) -> bool:
        return "DISPLAY" in os.environ and "localhost" not in os.environ["DISPLAY"]


context = Context(Config=Config)
