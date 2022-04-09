def load_ipython_extension(ip):
    from . import monkeypatch, config
    from rich import pretty, traceback

    pretty.install()
    # first install traceback monkeypatch to make the traceback work in notebooks as well
    monkeypatch.install()
    traceback.install(show_locals=config.show_locals())
