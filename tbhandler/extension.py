def load_ipython_extension(ip):
    from rich import pretty
    pretty.install()
    
    # first install traceback monkeypatch to make the traceback work in notebooks as well
    from . import monkeypatch
    monkeypatch.install()
    
    from rich.traceback import install
    install(show_locals=True)
