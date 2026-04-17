# CSS Selector implementation for JustHTML
# Supports a subset of CSS selectors for querying the DOM

from __future__ import annotations

from functools import lru_cache
from typing import Any


class SelectorError(ValueError):
    """Raised when a CSS selector is invalid."""


# Token types for the CSS selector lexer
class TokenType:
    TAG: str = "TAG"  # div, span, etc.
    ID: str = "ID"  # #foo
    CLASS: str = "CLASS"  # .bar
    UNIVERSAL: str = "UNIVERSAL"  # *
    ATTR_START: str = "ATTR_START"  # [
    ATTR_END: str = "ATTR_END"  # ]
    ATTR_OP: str = "ATTR_OP"  # =, ~=, |=, ^=, $=, *=
    STRING: str = "STRING"  # "value" or 'value' or unquoted
    COMBINATOR: str = "COMBINATOR"  # >, +, ~, or whitespace (descendant)
    COMMA: str = "COMMA"  # ,
    COLON: str = "COLON"  # :
    PAREN_OPEN: str = "PAREN_OPEN"  # (
    PAREN_CLOSE: str = "PAREN_CLOSE"  # )
    EOF: str = "EOF"


class Token:
    __slots__ = ("type", "value")

    type: str
    value: str | None

    def __init__(self, token_type: str, value: str | None = None) -> None:
        self.type = token_type
        self.value = value

    def __repr__(self) -> str:
        return f"Token({self.type}, {self.value!r})"


class SelectorTokenizer:
    """Tokenizes a CSS selector string into tokens."""

    __slots__ = ("length", "pos", "selector")

    selector: str
    pos: int
    length: int

    def __init__(self, selector: str) -> None:
        self.selector = selector
        self.pos = 0
        self.length = len(selector)

    def _peek(self, offset: int = 0) -> str:
        pass

    def _advance(self) -> str:
        pass

    def _skip_whitespace(self) -> None:
        pass

    def _is_name_start(self, ch: str) -> bool:
        # CSS identifier start: letter, underscore, or non-ASCII
        pass

    def _is_name_char(self, ch: str) -> bool:
        # CSS identifier continuation: name-start or digit
        pass

    def _read_name(self) -> str:
        pass

    def _read_string(self, quote: str) -> str:
        # Skip opening quote
        pass

    def _read_unquoted_attr_value(self) -> str:
        # Read an unquoted attribute value (CSS identifier)
        pass

    def tokenize(self) -> list[Token]:
        pass


# AST Node types for parsed selectors


class SimpleSelector:
    """A single simple selector (tag, id, class, attribute, or pseudo-class)."""

    __slots__ = ("arg", "name", "operator", "type", "value")

    TYPE_TAG: str = "tag"
    TYPE_ID: str = "id"
    TYPE_CLASS: str = "class"
    TYPE_UNIVERSAL: str = "universal"
    TYPE_ATTR: str = "attr"
    TYPE_PSEUDO: str = "pseudo"

    type: str
    name: str | None
    operator: str | None
    value: str | None
    arg: str | None

    def __init__(
        self,
        selector_type: str,
        name: str | None = None,
        operator: str | None = None,
        value: str | None = None,
        arg: str | None = None,
    ) -> None:
        self.type = selector_type
        self.name = name
        self.operator = operator
        self.value = value
        self.arg = arg  # For :not() and :nth-child()

    def __repr__(self) -> str:
        parts = [f"SimpleSelector({self.type!r}"]
        if self.name:
            parts.append(f", name={self.name!r}")
        if self.operator:
            parts.append(f", op={self.operator!r}")
        if self.value is not None:
            parts.append(f", value={self.value!r}")
        if self.arg is not None:
            parts.append(f", arg={self.arg!r}")
        parts.append(")")
        return "".join(parts)


class CompoundSelector:
    """A sequence of simple selectors (e.g., div.foo#bar)."""

    __slots__ = ("selectors",)

    selectors: list[SimpleSelector]

    def __init__(self, selectors: list[SimpleSelector] | None = None) -> None:
        self.selectors = selectors or []

    def __repr__(self) -> str:
        return f"CompoundSelector({self.selectors!r})"


class ComplexSelector:
    """A chain of compound selectors with combinators."""

    __slots__ = ("parts",)

    parts: list[tuple[str | None, CompoundSelector]]

    def __init__(self) -> None:
        # List of (combinator, compound_selector) tuples
        # First item has combinator=None
        self.parts = []

    def __repr__(self) -> str:
        return f"ComplexSelector({self.parts!r})"


class SelectorList:
    """A comma-separated list of complex selectors."""

    __slots__ = ("selectors",)

    selectors: list[ComplexSelector]

    def __init__(self, selectors: list[ComplexSelector] | None = None) -> None:
        self.selectors = selectors or []

    def __repr__(self) -> str:
        return f"SelectorList({self.selectors!r})"


# Type alias for parsed selectors
ParsedSelector = ComplexSelector | SelectorList


class SelectorParser:
    """Parses a list of tokens into a selector AST."""

    __slots__ = ("pos", "tokens")

    tokens: list[Token]
    pos: int

    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.pos = 0

    def _peek(self) -> Token:
        pass

    def _advance(self) -> Token:
        pass

    def _expect(self, token_type: str) -> Token:
        pass

    def parse(self) -> ParsedSelector:
        """Parse a complete selector (possibly comma-separated list)."""
        pass

    def _parse_complex_selector(self) -> ComplexSelector | None:
        """Parse a complex selector (compound selectors with combinators)."""
        pass

    def _parse_compound_selector(self) -> CompoundSelector | None:
        """Parse a compound selector (sequence of simple selectors)."""
        pass

    def _parse_attribute_selector(self) -> SimpleSelector:
        """Parse an attribute selector [attr], [attr=value], etc."""
        pass

    def _parse_pseudo_selector(self) -> SimpleSelector:
        """Parse a pseudo-class selector like :first-child or :not(selector)."""
        pass


class SelectorMatcher:
    """Matches selectors against DOM nodes."""

    __slots__ = ()

    def _unquote_pseudo_arg(self, arg: str) -> str:
        pass

    def matches(self, node: Any, selector: ParsedSelector | CompoundSelector | SimpleSelector) -> bool:
        """Check if a node matches a parsed selector."""
        pass

    def _matches_complex(self, node: Any, selector: ComplexSelector) -> bool:
        """Match a complex selector (with combinators)."""
        pass

    def _matches_compound(self, node: Any, compound: CompoundSelector) -> bool:
        """Match a compound selector (all simple selectors must match)."""
        pass

    def _matches_simple(self, node: Any, selector: SimpleSelector) -> bool:
        """Match a simple selector against a node."""
        pass

    def _matches_attribute(self, node: Any, selector: SimpleSelector) -> bool:
        """Match an attribute selector."""
        pass

    def _matches_pseudo(self, node: Any, selector: SimpleSelector) -> bool:
        """Match a pseudo-class selector."""
        pass

    def _get_element_children(self, parent: Any) -> list[Any]:
        """Get only element children (exclude text, comments, etc.)."""
        pass

    def _get_previous_sibling(self, node: Any) -> Any | None:
        """Get the previous element sibling. Returns None if node is first or not found."""
        pass

    def _is_first_child(self, node: Any) -> bool:
        """Check if node is the first element child of its parent."""
        pass

    def _is_last_child(self, node: Any) -> bool:
        """Check if node is the last element child of its parent."""
        pass

    def _is_first_of_type(self, node: Any) -> bool:
        """Check if node is the first sibling of its type."""
        pass

    def _is_last_of_type(self, node: Any) -> bool:
        """Check if node is the last sibling of its type."""
        pass

    def _parse_nth_expression(self, expr: str | None) -> tuple[int, int] | None:
        """Parse an nth-child expression like '2n+1', 'odd', 'even', '3'."""
        pass

    def _matches_nth(self, index: int, a: int, b: int) -> bool:
        """Check if 1-based index matches An+B formula."""
        pass

    def _matches_nth_child(self, node: Any, arg: str | None) -> bool:
        """Match :nth-child(An+B)."""
        pass

    def _matches_nth_of_type(self, node: Any, arg: str | None) -> bool:
        """Match :nth-of-type(An+B)."""
        pass


def parse_selector(selector_string: str) -> ParsedSelector:
    """Parse a CSS selector string into an AST.

    Note: parsing is cached internally via an LRU cache (see
    `_parse_selector_cached`) to keep repeated selector use cheap.
    """
    pass


@lru_cache(maxsize=512)
def _parse_selector_cached(selector_string: str) -> ParsedSelector:
    pass


# Global matcher instance
_matcher: SelectorMatcher = SelectorMatcher()


def _is_simple_tag_selector(selector: str) -> bool:
    pass


def _selector_allows_non_elements(selector: ParsedSelector | CompoundSelector | SimpleSelector) -> bool:
    pass


def _query_descendants_tag(node: Any, tag_lower: str, results: list[Any]) -> None:
    pass


def query(root: Any, selector_string: str) -> list[Any]:
    """
    Query the DOM tree starting from root, returning all matching nodes.

    Searches descendants of root, not including root itself (matching browser
    behavior for querySelectorAll).

    Args:
        root: The root node to search from
        selector_string: A CSS selector string

    Returns:
        A list of matching nodes

    Performance notes:
    - Simple tag-only selectors like "div" use a fast descendant-scan path.
    - Other selectors are parsed via an internal LRU cache (up to 512 distinct
      selector strings) to reduce repeated parse overhead.
    """
    pass


def _query_descendants(
    node: Any,
    selector: ParsedSelector,
    results: list[Any],
    *,
    allow_non_elements: bool = False,
) -> None:
    """Search for matching nodes in descendants."""
    pass


def matches(node: Any, selector_string: str) -> bool:
    """
    Check if a node matches a CSS selector.

    Args:
        node: The node to check
        selector_string: A CSS selector string

    Returns:
        True if the node matches, False otherwise
    """
    pass
