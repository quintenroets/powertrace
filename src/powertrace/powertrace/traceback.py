from functools import cache

from rich.traceback import Traceback as RichTraceback

from powertrace import models


class Traceback(models.Traceback):
    @cache  # noqa: B019
    def construct_message(self, *, show_locals: bool) -> RichTraceback:
        return (
            RichTraceback()
            if self.type_ is None or self.value is None
            else RichTraceback.from_exception(
                self.type_,
                self.value,
                self.traceback,
                show_locals=show_locals,
            )
        )
