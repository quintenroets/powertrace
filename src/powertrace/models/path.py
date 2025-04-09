from typing import TypeVar, cast

import superpathlib
from simple_classproperty import classproperty
from typing_extensions import Self

T = TypeVar("T", bound="Path")


class Path(superpathlib.Path):
    @classmethod
    @classproperty
<<<<<<< HEAD
    def logs(cls: type[T]) -> T:
        path = cls.script_assets / ".tracebacks"
        return cast(T, path)

    @property
    def with_console_suffix(self: T) -> T:
        return self.with_stem("." + self.stem)

    @classmethod
    @classproperty
    def log(cls: type[T]) -> T:
        path = cls.logs / "traceback.txt"
        return cast(T, path)

    @classmethod
    @classproperty
    def short_log(cls: type[T]) -> T:
        path = cls.logs / "short_traceback.txt"
        return cast(T, path)
=======
    def source_root(cls) -> Self:
        return cls(__file__).parent.parent

    @classmethod
    @classproperty
    def assets(cls) -> Self:
        path = cls.script_assets / cls.source_root.name
        return cast("Self", path)

    @classmethod
    @classproperty
    def config(cls) -> Self:
        path = cls.assets / "config" / "config.yaml"
        return cast("Self", path)
>>>>>>> template
