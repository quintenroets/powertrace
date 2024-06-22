from __future__ import annotations

import threading
from dataclasses import dataclass
from types import TracebackType
from typing import TypeVar

T = TypeVar("T", bound="Traceback")


@dataclass
class Traceback:
    type_: type[BaseException] | None = None
    value: BaseException | None = None
    traceback: TracebackType | None = None

    @classmethod
    def from_info(cls: type[T], info: threading.ExceptHookArgs) -> T:
        return cls(info.exc_type, info.exc_value, info.exc_traceback)

    @classmethod
    def from_tuple(
        cls: type[T],
        type_: type[BaseException],
        value: BaseException,
        traceback: TracebackType | None,
    ) -> T:
        return cls(type_, value, traceback)

    @property
    def as_tuple(
        self,
    ) -> tuple[type[BaseException] | None, BaseException | None, TracebackType | None]:
        return self.type_, self.value, self.traceback
