def load_ipython_extension(_: int) -> None:
    from rich import pretty, traceback  # noqa: PLC0415

    from powertrace.context import context  # noqa: PLC0415

    from . import rich_monkeypatch  # noqa: PLC0415

    pretty.install()
    # first install monkeypatch to make the traceback work in notebooks as well
    rich_monkeypatch.install()
    traceback.install(show_locals=context.show_full_traceback)
