"""HTML serialization utilities for JustHTML DOM nodes."""

# ruff: noqa: PERF401

from __future__ import annotations

import re
from enum import Enum
from typing import Any
from urllib.parse import quote as url_quote

from .constants import FOREIGN_ATTRIBUTE_ADJUSTMENTS, SPECIAL_ELEMENTS, VOID_ELEMENTS, WHITESPACE_PRESERVING_ELEMENTS

# Matches characters that prevent an attribute value from being unquoted.
# Note: This matches the logic of the previous loop-based implementation.
# It checks for space characters, quotes, equals sign, and greater-than.
_UNQUOTED_ATTR_VALUE_INVALID = re.compile(r'[ \t\n\f\r"\'=>]')
_LITERAL_TEXT_SERIALIZATION_ELEMENTS = frozenset({"script", "style"})
_SERIALIZABLE_TAG_NAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9:_-]*$")
_SERIALIZABLE_ATTR_NAME_RE = re.compile(r"^[A-Za-z_:][A-Za-z0-9:._-]*$")


class HTMLContext(str, Enum):
    HTML = "html"
    # Serialize node to HTML markup, then JS-string escape the resulting HTML.
    # Use this when embedding HTML markup into a JavaScript string literal.
    JS_STRING = "js_string"
    # Serialize node to HTML markup, then escape it for a quoted HTML attribute value.
    # This is useful for attributes that are later parsed as HTML (e.g. iframe[srcdoc]).
    HTML_ATTR_VALUE = "html_attr_value"
    # Serialize node to text, then percent-encode it.
    # Use this for URL attributes like href or src.
    URL = "url"


def _escape_text(text: str | None) -> str:
    pass


def _validate_serializable_tag_name(name: str) -> str:
    pass


def _validate_serializable_attr_name(name: str) -> str:
    pass


def _serialize_comment_data(data: str | None) -> str:
    pass


def _serialize_text_for_parent(text: str | None, parent_name: str | None) -> str:
    pass


def _escape_js_string(value: str, *, quote: str = '"') -> str:
    pass


def _escape_url_value(value: str) -> str:
    pass


def _choose_attr_quote(value: str | None, forced_quote_char: str | None = None) -> str:
    pass


def _escape_attr_value(value: str | None, quote_char: str) -> str:
    pass


def _can_unquote_attr_value(value: str | None) -> bool:
    pass


def _serialize_doctype(node: Any) -> str:
    pass


def serialize_start_tag(
    name: str,
    attrs: dict[str, str | None] | None,
    *,
    quote_attr_values: bool = True,
    minimize_boolean_attributes: bool = True,
    quote_char: str | None = None,
    use_trailing_solidus: bool = False,
    is_void: bool = False,
) -> str:
    pass


def serialize_end_tag(name: str) -> str:
    pass


def _node_to_html_compact(node: Any) -> str:
    """Serialize a node subtree to compact HTML (no newlines/indentation).

    This is a hot path for `to_html(..., pretty=False)`, so it is implemented
    iteratively to avoid recursion overhead and per-node list allocations.
    """
    pass


def to_html(
    node: Any,
    indent: int = 0,
    indent_size: int = 2,
    *,
    pretty: bool = True,
    context: HTMLContext | None = None,
    quote: str = '"',
) -> str:
    """Convert node to HTML string."""
    pass


def _collapse_html_whitespace(text: str) -> str:
    """Collapse HTML whitespace runs to a single space and trim edges.

    This matches how HTML rendering treats most whitespace in text nodes, and is
    used only for pretty-printing in non-preformatted contexts.
    """
    pass


def _normalize_formatting_whitespace(text: str) -> str:
    """Normalize formatting whitespace within a text node.

    Converts newlines/tabs/CR/FF to regular spaces and collapses runs that
    include such formatting whitespace to a single space.

    Pure space runs are preserved as-is (so existing double-spaces remain).
    """
    pass


def _is_whitespace_text_node(node: Any) -> bool:
    pass


def _is_blocky_element(node: Any) -> bool:
    # Treat elements as block-ish if they are block-level *or* contain any block-level
    # descendants. This keeps pretty-printing readable for constructs like <a><div>...</div></a>.
    pass


_LAYOUT_BLOCK_ELEMENTS = {
    "address",
    "article",
    "aside",
    "blockquote",
    "body",
    "caption",
    "center",
    "dd",
    "details",
    "dialog",
    "dir",
    "div",
    "dl",
    "dt",
    "fieldset",
    "figcaption",
    "figure",
    "footer",
    "form",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "header",
    "hgroup",
    "hr",
    "html",
    "iframe",
    "li",
    "listing",
    "main",
    "marquee",
    "menu",
    "nav",
    "noframes",
    "noscript",
    "ol",
    "p",
    "plaintext",
    "pre",
    "search",
    "section",
    "summary",
    "table",
    "tbody",
    "td",
    "tfoot",
    "th",
    "thead",
    "tr",
    "ul",
}


_FORMAT_SEP = object()


def _is_layout_blocky_element(node: Any) -> bool:
    # Similar to _is_blocky_element(), but limited to actual layout blocks.
    # This avoids turning inline-ish "special" elements like <script> into
    # multiline pretty-print breaks in contexts like <p>.
    pass


def _pretty_renders_nonempty(node: Any, *, in_pre: bool) -> bool:
    pass


def _is_formatting_whitespace_text(data: str) -> bool:
    # Formatting whitespace is something users typically don't intend to preserve
    # exactly (e.g. newlines/indentation, or large runs of spaces).
    pass


def _should_pretty_indent_children(children: list[Any]) -> bool:
    pass


def _node_to_html(node: Any, indent: int = 0, indent_size: int = 2, *, in_pre: bool) -> str:
    """Helper to convert a node to HTML using an explicit stack."""
    pass


def to_test_format(node: Any, indent: int = 0) -> str:
    """Convert node to html5lib test format string.

    This format is used by html5lib-tests for validating parser output.
    Uses '| ' prefixes and specific indentation rules.
    """
    pass


def _node_to_test_format(node: Any, indent: int) -> str:
    """Helper to convert a node to test format."""
    pass


def _qualified_name(node: Any) -> str:
    """Get the qualified name of a node (with namespace prefix if needed)."""
    pass


def _attrs_to_test_format(node: Any, indent: int) -> list[str]:
    """Format element attributes for test output."""
    pass


def _doctype_to_test_format(node: Any) -> str:
    """Format DOCTYPE node for test output."""
    pass
