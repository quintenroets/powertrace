from typing import TypeVar, cast

import superpathlib
from simple_classproperty import classproperty
from typing_extensions import Self

T = TypeVar("T", bound="Path")


class Path(superpathlib.Path):
    @classmethod
    @classproperty
    def logs(cls) -> Self:
        path = cls.script_assets / ".tracebacks"
        return cast("Self", path)

    @property
    def with_console_suffix(self) -> Self:
        return self.with_stem("." + self.stem)

    @classmethod
    @classproperty
    def log(cls) -> Self:
        path = cls.logs / "traceback.txt"
        return cast("Self", path)

    @classmethod
    @classproperty
    def short_log(cls) -> Self:
        path = cls.logs / "short_traceback.txt"
        return cast("Self", path)
