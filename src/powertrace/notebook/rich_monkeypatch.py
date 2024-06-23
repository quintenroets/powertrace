from collections.abc import Iterable

from rich.traceback import (
    Columns,
    ConsoleRenderable,
    Frame,
    PathHighlighter,
    RenderResult,
    Stack,
    Syntax,
    Text,
    Traceback,
    group,
    render_scope,
)


@group()
def _render_stack(self: Traceback, stack: Stack) -> RenderResult:  # pragma: nocover
    path_highlighter = PathHighlighter()
    theme = self.theme
    code_cache: dict[str, str] = {}

    def read_code(filename: str) -> str:
        """Read files, and cache results on filename.

        Args:
            filename (str): Filename to read

        Returns:
            str: Contents of file
        """
        code = code_cache.get(filename)
        if code is None:
            with open(filename, encoding="utf-8", errors="replace") as code_file:
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

    exclude_frames: range | None = None
    if self.max_frames != 0:
        exclude_frames = range(
            self.max_frames // 2,
            len(stack.frames) - self.max_frames // 2,
        )

    excluded = False
    for frame_index, frame in enumerate(stack.frames):
        if exclude_frames and frame_index in exclude_frames:
            excluded = True
            continue

        if excluded:
            assert exclude_frames is not None
            yield Text(
                f"\n... {len(exclude_frames)} frames hidden ...",
                justify="center",
                style="traceback.error",
            )
            excluded = False

        first = frame_index == 1
        frame_filename = frame.filename
        suppressed = any(frame_filename.startswith(path) for path in self.suppress)

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
        if not suppressed:
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
                CHANGED BEHAVIOUR.
                """
                if not frame.locals or "get_ipython" not in frame.locals:
                    yield (
                        Columns(
                            [*render_locals(frame)],
                            padding=1,
                        )
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


def install() -> None:
    Traceback._render_stack = _render_stack  # type: ignore[method-assign]
