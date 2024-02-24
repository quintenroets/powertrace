import cli
from superpathlib import Path


def main():
    template_content = get_template_content()
    path = get_sitecustomize_path()
    while path.text != template_content:
        cli.run("rm", path, root=True)
        path = get_sitecustomize_path()


def get_sitecustomize_path():
    command = 'python3 -c "import sitecustomize; print(sitecustomize.__file__)"'
    result = cli.get(command)
    return Path(result)


def get_template_content():
    template_path = Path(__file__).parent.parent / "sitecustomize.py"
    return template_path.text
