import superpathlib


class BasePath(superpathlib.Path):
    @property
    def console(self):
        return self.with_stem("." + self.stem)


class Path(BasePath):
    log_folder = BasePath.assets / ".error"
    log = log_folder / "error.txt"
    short_log = log_folder / "short_error.txt"
