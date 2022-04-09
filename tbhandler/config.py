import os


def show_locals():
    return os.environ.get("full_traceback", "false") != "false"
