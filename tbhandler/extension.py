def load_ipython_extension(ip):
    from rich import pretty, traceback

    from . import config, monkeypatch

    pretty.install()
    # first install monkeypatch to make the traceback work in notebooks as well
    monkeypatch.install()
    traceback.install(show_locals=config.show_locals())
