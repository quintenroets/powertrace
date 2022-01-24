from rich.traceback import *


@group()
def _render_stack(self, stack: Stack) -> RenderResult:
    path_highlighter = PathHighlighter()
    theme = self.theme
    code_cache: Dict[str, str] = {}

    def read_code(filename: str) -> str:
        """Read files, and cache results on filename.

        Args:
            filename (str): Filename to read

        Returns:
            str: Contents of file
        """
        code = code_cache.get(filename)
        if code is None:
            with open(filename, "rt", encoding="utf-8", errors="replace") as code_file:
                code = code_file.read()
            code_cache[filename] = code
        return code

    def render_locals(frame: Frame) -> Iterable[ConsoleRenderable]:
        if frame.locals:
            yield render_scope(
                frame.locals,
                title="locals",
                indent_guides=self.indent_guides,
                max_length=self.locals_max_length,
                max_string=self.locals_max_string,
            )

    for first, frame in loop_first(stack.frames):
        text = Text.assemble(
            path_highlighter(Text(frame.filename, style="pygments.string")),
            (":", "pygments.text"),
            (str(frame.lineno), "pygments.number"),
            " in ",
            (frame.name, "pygments.function"),
            style="pygments.text",
        )
        if not frame.filename.startswith("<") and not first:
            yield ""
        yield text
        if frame.filename.startswith("<"):
            yield from render_locals(frame)
            continue
        try:
            code = read_code(frame.filename)
            lexer_name = self._guess_lexer(frame.filename, code)
            syntax = Syntax(
                code,
                lexer_name,
                theme=theme,
                line_numbers=True,
                line_range=(
                    frame.lineno - self.extra_lines,
                    frame.lineno + self.extra_lines,
                ),
                highlight_lines={frame.lineno},
                word_wrap=self.word_wrap,
                code_width=88,
                indent_guides=self.indent_guides,
                dedent=False,
            )
            yield ""

        except FileNotFoundError:
            """
            CHANGED BEHAVIOUR
            """
            if frame.locals:
                if "get_ipython" not in frame.locals:
                    yield (
                        Columns(
                            [*render_locals(frame)],
                            padding=1,
                        )
                    )
            else:
                yield Text.assemble(
                    (f"\n{error}", "traceback.error"),
                )

        except Exception as error:
            yield Text.assemble(
                (f"\n{error}", "traceback.error"),
            )
        else:
            yield (
                Columns(
                    [
                        syntax,
                        *render_locals(frame),
                    ],
                    padding=1,
                )
                if frame.locals
                else syntax
            )


def install():
    Traceback._render_stack = _render_stack
