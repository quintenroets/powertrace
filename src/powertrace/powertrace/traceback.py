from functools import cache
from traceback import walk_tb
from typing import Any

from rich.traceback import Traceback as RichTraceback

from .. import models
from ..models import Path


class Traceback(models.Traceback):
    @cache
    def construct_message(self, show_locals: bool) -> RichTraceback:
        return (
            RichTraceback()
            if self.type_ is None or self.value is None
            else RichTraceback.from_exception(
                self.type_, self.value, self.traceback, show_locals=show_locals
            )
        )

    @property
    def filename(self) -> Path | None:
        frame_summary = None
        for frame_summary, _ in walk_tb(self.traceback):
            pass
        return frame_summary and self.extract_path(frame_summary)

    @classmethod
    def extract_path(cls, frame_summary: Any) -> Path | None:
        path = Path(frame_summary.f_code.co_filename)
        return path if path.exists() else None
