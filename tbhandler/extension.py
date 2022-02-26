def load_ipython_extension(ip):
    from rich import pretty
    from . import monkeypatch
    from rich.traceback import install

    pretty.install()
    # first install traceback monkeypatch to make the traceback work in notebooks as well
    monkeypatch.install()
    install(show_locals=True)
