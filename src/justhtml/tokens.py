from __future__ import annotations

from typing import Literal


class Tag:
    __slots__ = ("attrs", "end_pos", "kind", "name", "self_closing", "start_pos")

    START: Literal[0] = 0
    END: Literal[1] = 1

    kind: int
    name: str
    attrs: dict[str, str | None]
    end_pos: int | None
    self_closing: bool
    start_pos: int | None

    def __init__(
        self,
        kind: int,
        name: str,
        attrs: dict[str, str | None] | None,
        self_closing: bool = False,
        start_pos: int | None = None,
        end_pos: int | None = None,
    ) -> None:
        self.kind = kind
        self.name = name
        self.attrs = attrs if attrs is not None else {}
        self.self_closing = bool(self_closing)
        self.start_pos = start_pos
        self.end_pos = end_pos


class CharacterTokens:
    __slots__ = ("data",)

    data: str

    def __init__(self, data: str) -> None:
        self.data = data


class CommentToken:
    __slots__ = ("data", "start_pos")

    data: str
    start_pos: int | None

    def __init__(self, data: str, start_pos: int | None = None) -> None:
        self.data = data
        self.start_pos = start_pos


class Doctype:
    __slots__ = ("force_quirks", "name", "public_id", "system_id")

    name: str | None
    public_id: str | None
    system_id: str | None
    force_quirks: bool

    def __init__(
        self,
        name: str | None = None,
        public_id: str | None = None,
        system_id: str | None = None,
        force_quirks: bool = False,
    ) -> None:
        self.name = name
        self.public_id = public_id
        self.system_id = system_id
        self.force_quirks = bool(force_quirks)


class DoctypeToken:
    __slots__ = ("doctype",)

    doctype: Doctype

    def __init__(self, doctype: Doctype) -> None:
        self.doctype = doctype


class EOFToken:
    __slots__ = ()


AnyToken = Tag | CharacterTokens | CommentToken | DoctypeToken | EOFToken


class TokenSinkResult:
    __slots__ = ()

    Continue: Literal[0] = 0
    Plaintext: Literal[1] = 1


class ParseError:
    """Represents a parse error with location information."""

    __slots__ = ("_end_column", "_source_html", "category", "code", "column", "line", "message")

    category: str
    code: str
    line: int | None
    column: int | None
    message: str
    _source_html: str | None
    _end_column: int | None

    __hash__ = None  # type: ignore[assignment]  # Unhashable since we define __eq__

    def __init__(
        self,
        code: str,
        line: int | None = None,
        column: int | None = None,
        category: str = "parse",
        message: str | None = None,
        source_html: str | None = None,
        end_column: int | None = None,
    ) -> None:
        self.category = category
        self.code = code
        self.line = line
        self.column = column
        self.message = message or code
        self._source_html = source_html
        self._end_column = end_column

    def __repr__(self) -> str:
        if self.line is not None and self.column is not None:
            if self.category != "parse":
                return f"ParseError({self.code!r}, line={self.line}, column={self.column}, category={self.category!r})"
            return f"ParseError({self.code!r}, line={self.line}, column={self.column})"
        if self.category != "parse":
            return f"ParseError({self.code!r}, category={self.category!r})"
        return f"ParseError({self.code!r})"

    def __str__(self) -> str:
        if self.line is not None and self.column is not None:
            if self.message != self.code:
                return f"({self.line},{self.column}): {self.code} - {self.message}"
            return f"({self.line},{self.column}): {self.code}"
        if self.message != self.code:
            return f"{self.code} - {self.message}"
        return self.code

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ParseError):
            return NotImplemented
        return (
            self.category == other.category
            and self.code == other.code
            and self.line == other.line
            and self.column == other.column
        )

    def as_exception(self, end_column: int | None = None) -> SyntaxError:
        """Convert to a SyntaxError-like exception with source highlighting.

        This uses Python 3.11+ enhanced error display to show the exact
        location in the HTML source where the error occurred.

        Args:
            end_column: Optional end column for highlighting a range.
                       If None, attempts to highlight the full tag at the error position.

        Returns:
            A SyntaxError instance configured to display the error location.
        """
        pass
