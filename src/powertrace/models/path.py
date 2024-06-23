from typing import TypeVar, cast

import superpathlib
from simple_classproperty import classproperty

T = TypeVar("T", bound="Path")


class Path(superpathlib.Path):
    @classmethod
    @classproperty
    def logs(cls: type[T]) -> T:
        path = cls.script_assets / ".tracebacks"
        return cast(T, path)

    @property
    def with_console_suffix(self: T) -> T:
        return self.with_stem("." + self.stem)

    @classmethod
    @classproperty
    def log(cls: type[T]) -> T:
        path = cls.logs / "error.txt"
        return cast(T, path)

    @classmethod
    @classproperty
    def short_log(cls: type[T]) -> T:
        path = cls.logs / "short_error.txt"
        return cast(T, path)
