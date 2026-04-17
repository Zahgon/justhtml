from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast
from urllib.parse import quote

from .selector import query
from .serialize import to_html

if TYPE_CHECKING:
    from .serialize import HTMLContext
    from .tokens import Doctype


def _markdown_escape_text(s: str) -> str:
    pass


def _markdown_code_span(s: str | None) -> str:
    pass


def _markdown_backtick_fence(s: str | None, *, minimum: int) -> str:
    pass


def _markdown_thematic_or_setext_line(s: str, marker: str, *, minimum_markers: int) -> bool:
    pass


def _markdown_escape_line_start(s: str) -> tuple[str, int] | None:
    pass


def _markdown_link_destination(url: str) -> str:
    """Return a Markdown-safe link destination.

    We primarily care about avoiding Markdown formatting injection and broken
    parsing for URLs that contain whitespace or parentheses.

    CommonMark supports destinations wrapped in angle brackets:
    `[text](<https://example.com/a(b)c>)`
    """
    pass


class _MarkdownBuilder:
    __slots__ = ("_buf", "_newline_count", "_pending_space")

    _buf: list[str]
    _newline_count: int
    _pending_space: bool

    def __init__(self) -> None:
        self._buf = []
        self._newline_count = 0
        self._pending_space = False

    def _rstrip_last_segment(self) -> None:
        pass

    def newline(self, count: int = 1) -> None:
        pass

    def ensure_newlines(self, count: int) -> None:
        pass

    def raw(self, s: str) -> None:
        pass

    def text(self, s: str, preserve_whitespace: bool = False) -> None:
        pass

    def finish(self) -> str:
        pass


# Type alias for any node type
NodeType = "Node | Element | Template | Text | Comment | Document | DocumentFragment"


def _to_text_collect(node: Any, parts: list[str], strip: bool) -> None:
    # Iterative traversal avoids recursion overhead on large documents.
    pass


_TEXT_BLOCK_ELEMENTS: frozenset[str] = frozenset(
    {
        "address",
        "article",
        "aside",
        "blockquote",
        "body",
        "dd",
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
        "hr",
        "html",
        "li",
        "main",
        "nav",
        "ol",
        "p",
        "pre",
        "section",
        "table",
        "tbody",
        "td",
        "tfoot",
        "th",
        "thead",
        "tr",
        "ul",
    }
)

_TEXT_BREAK_ELEMENTS: frozenset[str] = frozenset({"br"})


def _to_text_break(chunks: list[list[str]]) -> None:
    pass


def _to_text_collect_block_chunks(node: Any, chunks: list[list[str]], strip: bool) -> None:
    # Depth-first walk that inserts chunk boundaries for block-level elements.
    # This lets callers join chunks with a separator (e.g. "\n") without
    # introducing separators inside inline elements like <b> or <span>.
    pass


class Node:
    __slots__ = (
        "_origin_col",
        "_origin_line",
        "_origin_pos",
        "_source_html",
        "attrs",
        "children",
        "data",
        "name",
        "namespace",
        "parent",
    )

    name: str
    parent: Node | Element | Template | None
    attrs: dict[str, str | None] | None
    children: list[Any] | None
    data: str | Doctype | None
    namespace: str | None
    _origin_pos: int | None
    _origin_line: int | None
    _origin_col: int | None
    _source_html: str | None

    def __init__(
        self,
        name: str,
        attrs: dict[str, str | None] | None = None,
        data: str | Doctype | None = None,
        namespace: str | None = None,
    ) -> None:
        self.name = name
        self.parent = None
        self.data = data
        self._source_html = None
        self._origin_pos = None
        self._origin_line = None
        self._origin_col = None

        if name.startswith("#") or name == "!doctype":
            self.namespace = namespace
            if name == "#comment" or name == "!doctype":
                self.children = None
                self.attrs = None
            else:
                self.children = []
                self.attrs = attrs if attrs is not None else {}
        else:
            self.namespace = namespace or "html"
            self.children = []
            self.attrs = attrs if attrs is not None else {}

    def append_child(self, node: Any) -> None:
        pass

    @property
    def origin_offset(self) -> int | None:
        """Best-effort origin offset (0-indexed) in the source HTML, if known."""
        pass

    @property
    def origin_line(self) -> int | None:
        pass

    @property
    def origin_col(self) -> int | None:
        pass

    @property
    def origin_location(self) -> tuple[int, int] | None:
        pass

    def remove_child(self, node: Any) -> None:
        pass

    def to_html(
        self,
        indent: int = 0,
        indent_size: int = 2,
        pretty: bool = True,
        *,
        context: HTMLContext | None = None,
        quote: str = '"',
    ) -> str:
        """Convert node to HTML string."""
        pass

    def query(self, selector: str) -> list[Any]:
        """
        Query this subtree using a CSS selector.

        Args:
            selector: A CSS selector string

        Returns:
            A list of matching nodes

        Raises:
            ValueError: If the selector is invalid
        """
        pass

    def query_one(self, selector: str) -> Any | None:
        """Return the first matching descendant for a CSS selector, or None."""
        pass

    @property
    def text(self) -> str:
        """Return the node's own text value.

        For text nodes this is the node data. For other nodes this is an empty
        string. Use `to_text()` to get textContent semantics.
        """
        pass

    def to_text(
        self,
        separator: str = " ",
        strip: bool = True,
        *,
        separator_blocks_only: bool = False,
    ) -> str:
        """Return the concatenated text of this node's descendants.

        - `separator` controls how text nodes are joined (default: a single space).
        - `strip=True` strips each text node and drops empty segments.
        - `separator_blocks_only=True` only applies `separator` between block-level
          elements, avoiding separators inside inline elements (like `<b>`).
        Template element contents are included via `template_content`.
        """
        pass

    def to_markdown(self, html_passthrough: bool = False) -> str:
        """Return a GitHub Flavored Markdown representation of this subtree.

        This is a pragmatic HTML->Markdown converter intended for readability.
        - Tables and images are preserved as raw HTML.
        - Unknown elements fall back to rendering their children.
        """
        pass

    def insert_before(self, node: Any, reference_node: Any | None) -> None:
        """
        Insert a node before a reference node.

        Args:
            node: The node to insert
            reference_node: The node to insert before. If None, append to end.

        Raises:
            ValueError: If reference_node is not a child of this node
        """
        pass

    def replace_child(self, new_node: Any, old_node: Any) -> Any:
        """
        Replace a child node with a new node.

        Args:
            new_node: The new node to insert
            old_node: The child node to replace

        Returns:
            The replaced node (old_node)

        Raises:
            ValueError: If old_node is not a child of this node
        """
        pass

    def has_child_nodes(self) -> bool:
        """Return True if this node has children."""
        pass

    def clone_node(self, deep: bool = False, override_attrs: dict[str, str | None] | None = None) -> Node:
        """
        Clone this node.

        Args:
            deep: If True, recursively clone children.
            override_attrs: Optional dictionary to use as attributes for the clone.

        Returns:
            A new node that is a copy of this node.
        """
        pass


class Document(Node):
    __slots__ = ()

    def __init__(self) -> None:
        super().__init__("#document")

    def clone_node(self, deep: bool = False, override_attrs: dict[str, str | None] | None = None) -> Document:
        pass


class DocumentFragment(Node):
    __slots__ = ()

    def __init__(self) -> None:
        super().__init__("#document-fragment")

    def clone_node(self, deep: bool = False, override_attrs: dict[str, str | None] | None = None) -> DocumentFragment:
        pass


class Comment(Node):
    __slots__ = ()

    def __init__(self, data: str | None = None) -> None:
        super().__init__("#comment", data=data)

    def clone_node(self, deep: bool = False, override_attrs: dict[str, str | None] | None = None) -> Comment:
        pass


class Element(Node):
    __slots__ = (
        "_end_tag_end",
        "_end_tag_present",
        "_end_tag_start",
        "_self_closing",
        "_start_tag_end",
        "_start_tag_start",
        "template_content",
    )

    template_content: Node | None
    children: list[Any]
    attrs: dict[str, str | None]
    _start_tag_start: int | None
    _start_tag_end: int | None
    _end_tag_start: int | None
    _end_tag_end: int | None
    _end_tag_present: bool
    _self_closing: bool

    def __init__(self, name: str, attrs: dict[str, str | None] | None, namespace: str | None) -> None:
        self.name = name
        self.parent = None
        self.data = None
        self.namespace = namespace
        self.children = []
        self.attrs = attrs if attrs is not None else {}
        self.template_content = None
        self._source_html = None
        self._origin_pos = None
        self._origin_line = None
        self._origin_col = None
        self._start_tag_start = None
        self._start_tag_end = None
        self._end_tag_start = None
        self._end_tag_end = None
        self._end_tag_present = False
        self._self_closing = False

    def clone_node(self, deep: bool = False, override_attrs: dict[str, str | None] | None = None) -> Element:
        pass


class Template(Element):
    __slots__ = ()

    def __init__(
        self,
        name: str,
        attrs: dict[str, str | None] | None = None,
        data: str | None = None,
        namespace: str | None = None,
    ) -> None:
        super().__init__(name, attrs, namespace)
        if self.namespace == "html":
            self.template_content = DocumentFragment()
        else:
            self.template_content = None

    def clone_node(self, deep: bool = False, override_attrs: dict[str, str | None] | None = None) -> Template:
        pass


def _clone_subtree_iterative(root: Any) -> Any:
    pass


class Text:
    __slots__ = ("_origin_col", "_origin_line", "_origin_pos", "data", "name", "namespace", "parent")

    data: str | None
    name: str
    namespace: None
    parent: Node | Element | Template | None
    _origin_pos: int | None
    _origin_line: int | None
    _origin_col: int | None

    def __init__(self, data: str | None) -> None:
        self.data = data
        self.parent = None
        self.name = "#text"
        self.namespace = None
        self._origin_pos = None
        self._origin_line = None
        self._origin_col = None

    @property
    def origin_offset(self) -> int | None:
        """Best-effort origin offset (0-indexed) in the source HTML, if known."""
        pass

    @property
    def origin_line(self) -> int | None:
        pass

    @property
    def origin_col(self) -> int | None:
        pass

    @property
    def origin_location(self) -> tuple[int, int] | None:
        pass

    @property
    def text(self) -> str:
        """Return the text content of this node."""
        pass

    def to_text(
        self,
        separator: str = " ",
        strip: bool = True,
        *,
        separator_blocks_only: bool = False,
    ) -> str:
        pass

    def to_markdown(self, html_passthrough: bool = False) -> str:
        pass

    @property
    def children(self) -> list[Any]:
        """Return empty list for Text (leaf node)."""
        pass

    def has_child_nodes(self) -> bool:
        """Return False for Text."""
        pass

    def clone_node(self, deep: bool = False) -> Text:
        pass


_MARKDOWN_BLOCK_ELEMENTS: frozenset[str] = frozenset(
    {
        "p",
        "div",
        "section",
        "article",
        "header",
        "footer",
        "main",
        "nav",
        "aside",
        "blockquote",
        "pre",
        "ul",
        "ol",
        "li",
        "hr",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "table",
    }
)


def _to_markdown_walk(
    node: Any,
    builder: _MarkdownBuilder,
    preserve_whitespace: bool,
    list_depth: int,
    in_link: bool = False,
    html_passthrough: bool = False,
) -> None:
    pass
