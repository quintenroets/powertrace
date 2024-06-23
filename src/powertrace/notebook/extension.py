def load_ipython_extension(_: int) -> None:
    from rich import pretty, traceback

    from ..context import context
    from . import rich_monkeypatch

    pretty.install()
    # first install monkeypatch to make the traceback work in notebooks as well
    rich_monkeypatch.install()
    traceback.install(show_locals=context.show_full_traceback)
