def load_ipython_extension(ip):
    from rich import pretty, traceback  # noqa: autoimport

    from . import config, monkeypatch  # noqa: autoimport

    pretty.install()
    # first install traceback monkeypatch to make the traceback work in notebooks as well
    monkeypatch.install()
    traceback.install(show_locals=config.show_locals())
