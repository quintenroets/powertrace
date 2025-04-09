from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, TypeVar

from typing_extensions import Self

if TYPE_CHECKING:
    import threading
    from types import TracebackType

T = TypeVar("T", bound="Traceback")


@dataclass(unsafe_hash=True)
class Traceback:
    type_: type[BaseException] | None = None
    value: BaseException | None = None
    traceback: TracebackType | None = None

    @classmethod
    def from_info(cls, info: threading.ExceptHookArgs) -> Self:
        return cls(info.exc_type, info.exc_value, info.exc_traceback)

    @classmethod
    def from_tuple(
        cls,
        type_: type[BaseException],
        value: BaseException,
        traceback: TracebackType | None,
    ) -> Self:
        return cls(type_, value, traceback)
