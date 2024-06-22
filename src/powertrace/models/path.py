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

    @classmethod
    @classproperty
    def config(cls: type[T]) -> T:
        path = cls.assets / "config" / "config.yaml"
        return cast(T, path)

    @property
    def with_console_suffix(self):
        return self.with_stem("." + self.stem)

    # log = log_folder / "error.txt"
    # short_log = log_folder / "short_error.txt"
