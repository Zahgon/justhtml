# ruff: noqa: S101, PLW2901

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .constants import (
    BUTTON_SCOPE_TERMINATORS,
    DEFAULT_SCOPE_TERMINATORS,
    DEFINITION_SCOPE_TERMINATORS,
    FOREIGN_ATTRIBUTE_ADJUSTMENTS,
    FOREIGN_BREAKOUT_ELEMENTS,
    FORMAT_MARKER,
    FORMATTING_ELEMENTS,
    HTML_INTEGRATION_POINT_SET,
    IMPLIED_END_TAGS,
    LIST_ITEM_SCOPE_TERMINATORS,
    MATHML_ATTRIBUTE_ADJUSTMENTS,
    MATHML_TEXT_INTEGRATION_POINT_SET,
    SPECIAL_ELEMENTS,
    SVG_ATTRIBUTE_ADJUSTMENTS,
    SVG_TAG_NAME_ADJUSTMENTS,
    TABLE_ALLOWED_CHILDREN,
    TABLE_FOSTER_TARGETS,
    TABLE_SCOPE_TERMINATORS,
)
from .errors import generate_error_message
from .node import Comment, Document, DocumentFragment, Element, Node, Template, Text
from .tokens import AnyToken, CharacterTokens, CommentToken, DoctypeToken, EOFToken, ParseError, Tag, TokenSinkResult
from .treebuilder_modes import TreeBuilderModesMixin
from .treebuilder_utils import (
    InsertionMode,
    is_all_whitespace,
)

if TYPE_CHECKING:
    from collections.abc import Callable


class TreeBuilder(TreeBuilderModesMixin):
    __slots__ = (
        "_body_end_handlers",
        "_body_start_handlers",
        "_body_token_handlers",
        "_mode_handlers",
        "_pending_end_tag_end",
        "_pending_end_tag_name",
        "_pending_end_tag_start",
        "active_formatting",
        "collect_errors",
        "document",
        "errors",
        "form_element",
        "fragment_context",
        "fragment_context_element",
        "frameset_ok",
        "head_element",
        "iframe_srcdoc",
        "ignore_lf",
        "insert_from_table",
        "mode",
        "open_elements",
        "original_mode",
        "pending_table_text",
        "pending_table_text_should_error",
        "quirks_mode",
        "scripting_enabled",
        "table_text_original_mode",
        "template_modes",
        "tokenizer",
        "tokenizer_state_override",
        "track_tag_spans",
    )

    _body_end_handlers: dict[str, Callable[[TreeBuilder, Any], Any]]
    _body_start_handlers: dict[str, Callable[[TreeBuilder, Any], Any]]
    _body_token_handlers: dict[str, Callable[[TreeBuilder, Any], Any]]
    _mode_handlers: dict[InsertionMode, Callable[[TreeBuilder, Any], Any]]
    _pending_end_tag_name: str | None
    _pending_end_tag_start: int | None
    _pending_end_tag_end: int | None
    track_tag_spans: bool
    active_formatting: list[Any]
    collect_errors: bool
    document: Node
    errors: list[ParseError]
    form_element: Any | None
    fragment_context: Any | None
    fragment_context_element: Any | None
    frameset_ok: bool
    head_element: Any | None
    iframe_srcdoc: bool
    ignore_lf: bool
    insert_from_table: bool
    mode: InsertionMode
    open_elements: list[Any]
    original_mode: InsertionMode | None  # type: ignore[assignment]
    pending_table_text: list[str]
    pending_table_text_should_error: bool
    quirks_mode: str
    scripting_enabled: bool
    table_text_original_mode: InsertionMode | None  # type: ignore[assignment]
    template_modes: list[InsertionMode]
    tokenizer: Any | None
    tokenizer_state_override: Any | None  # type: ignore[assignment]

    def __init__(
        self,
        fragment_context: Any | None = None,
        iframe_srcdoc: bool = False,
        collect_errors: bool = False,
        scripting_enabled: bool = True,
        track_tag_spans: bool = False,
    ) -> None:
        self.fragment_context = fragment_context
        self.iframe_srcdoc = iframe_srcdoc
        self.collect_errors = collect_errors
        self.scripting_enabled = bool(scripting_enabled)
        self.track_tag_spans = bool(track_tag_spans)
        self.errors = []
        self.tokenizer = None  # Set by parser after tokenizer is created
        self.fragment_context_element = None
        if fragment_context is not None:
            self.document = DocumentFragment()
        else:
            self.document = Document()
        self.mode = InsertionMode.INITIAL
        self.original_mode = None
        self.table_text_original_mode = None
        self.open_elements = []
        self._pending_end_tag_name = None
        self._pending_end_tag_start = None
        self._pending_end_tag_end = None
        self.head_element = None
        self.form_element = None
        self.frameset_ok = True
        self.quirks_mode = "no-quirks"
        self.ignore_lf = False
        self.active_formatting = []
        self.pending_table_text_should_error = False
        self.insert_from_table = False
        self.pending_table_text = []
        self.template_modes = []
        self.tokenizer_state_override = None
        if fragment_context is not None:
            # Fragment parsing per HTML5 spec
            root = self._create_element("html", None, {})
            self.document.append_child(root)
            self.open_elements.append(root)
            # Set mode based on context element name
            namespace = fragment_context.namespace
            context_name = fragment_context.tag_name or ""
            name = context_name.lower()

            # Create a fake context element to establish foreign content context
            # Per spec: "Create an element for the token in the given namespace"
            if namespace and namespace not in {None, "html"}:
                adjusted_name = context_name
                if namespace == "svg":
                    adjusted_name = self._adjust_svg_tag_name(context_name)
                context_element = self._create_element(adjusted_name, namespace, {})
                root.append_child(context_element)
                self.open_elements.append(context_element)
                self.fragment_context_element = context_element

            # For html context, don't pre-create head/body - start in BEFORE_HEAD mode
            # This allows frameset and other elements to be inserted properly
            if name == "html":
                self.mode = InsertionMode.BEFORE_HEAD
            # Table modes only apply to HTML namespace fragments (namespace is None or "html")
            elif namespace in {None, "html"} and name in {"tbody", "thead", "tfoot"}:
                self.mode = InsertionMode.IN_TABLE_BODY
            elif namespace in {None, "html"} and name == "tr":
                self.mode = InsertionMode.IN_ROW
            elif namespace in {None, "html"} and name in {"td", "th"}:
                self.mode = InsertionMode.IN_CELL
            elif namespace in {None, "html"} and name == "caption":
                self.mode = InsertionMode.IN_CAPTION
            elif namespace in {None, "html"} and name == "colgroup":
                self.mode = InsertionMode.IN_COLUMN_GROUP
            elif namespace in {None, "html"} and name == "table":
                self.mode = InsertionMode.IN_TABLE
            else:
                self.mode = InsertionMode.IN_BODY
            # For fragments, frameset_ok starts as False per HTML5 spec
            # This prevents frameset from being inserted in fragment contexts
            self.frameset_ok = False

    def _set_quirks_mode(self, mode: str) -> None:
        pass

    def _parse_error(self, code: str, tag_name: str | None = None, token: AnyToken | None = None) -> None:
        pass

    def _has_element_in_scope(
        self, target: str, terminators: set[str] | None = None, check_integration_points: bool = True
    ) -> bool:
        pass

    def _has_element_in_button_scope(self, target: str) -> bool:
        pass

    def _pop_until_inclusive(self, name: str) -> None:
        # Callers ensure element exists on stack
        pass

    def _close_p_element(self) -> bool:
        pass

    def process_token(self, token: Any) -> Any:
        # Optimization: Use type() identity check instead of isinstance
        pass

    def finish(self) -> Node:
        pass

    # Insertion mode dispatch ------------------------------------------------

    def _append_comment_to_document(self, text: str) -> None:
        pass

    def _append_comment(self, text: str, parent: Any | None = None) -> None:
        pass

    def _append_text(self, text: str) -> None:
        pass

    def _current_node_or_html(self) -> Any:
        pass

    def _create_root(self, attrs: dict[str, str | None]) -> Any:
        pass

    def _insert_element(self, tag: Any, *, push: bool, namespace: str = "html") -> Any:
        pass

    def _insert_phantom(self, name: str) -> Any:
        pass

    def _insert_body_if_missing(self) -> None:
        pass

    def _create_element(self, name: str, namespace: str | None, attrs: dict[str, str | None]) -> Any:
        pass

    def _maybe_mark_end_tag(self, node: Any) -> None:
        pass

    def _pop_current(self) -> Any:
        pass

    def _in_scope(self, name: str) -> bool:
        pass

    def _close_element_by_name(self, name: str) -> None:
        # Simple element closing - pops from the named element onwards
        # Used for explicit closing (e.g., when button start tag closes existing button)
        # Caller guarantees name is on the stack via _has_in_scope check
        pass

    def _any_other_end_tag(self, name: str) -> None:
        # Spec: "Any other end tag" in IN_BODY mode
        # Loop through stack backwards (always terminates: html is special)
        pass

    def _add_missing_attributes(self, node: Any, attrs: dict[str, str]) -> None:
        pass

    def _remove_from_open_elements(self, node: Any) -> bool:
        pass

    def _is_special_element(self, node: Any) -> bool:
        pass

    def _find_active_formatting_index(self, name: str) -> int | None:
        pass

    def _find_active_formatting_index_by_node(self, node: Any) -> int | None:
        pass

    def _clone_attributes(self, attrs: dict[str, str | None]) -> dict[str, str | None]:
        pass

    def _attrs_signature(self, attrs: dict[str, str | None]) -> tuple[tuple[str, str], ...]:
        pass

    def _find_active_formatting_duplicate(self, name: str, attrs: dict[str, str | None]) -> int | None:
        pass

    def _has_active_formatting_entry(self, name: str) -> bool:
        pass

    def _remove_last_active_formatting_by_name(self, name: str) -> None:
        pass

    def _remove_last_open_element_by_name(self, name: str) -> None:
        pass

    def _append_active_formatting_entry(self, name: str, attrs: dict[str, str | None], node: Any) -> None:
        pass

    def _clear_active_formatting_up_to_marker(self) -> None:
        pass

    def _push_formatting_marker(self) -> None:
        pass

    def _remove_formatting_entry(self, index: int) -> None:
        pass

    def _reconstruct_active_formatting_elements(self) -> None:
        pass

    def _insert_node_at(self, parent: Any, index: int, node: Any) -> None:
        pass

    def _find_last_on_stack(self, name: str) -> Any | None:
        pass

    def _clear_stack_until(self, names: set[str] | frozenset[str]) -> None:
        # All callers include "html" in names, so this always terminates via break
        pass

    def _generate_implied_end_tags(self, exclude: str | None = None) -> None:
        # Always terminates: html is not in IMPLIED_END_TAGS
        pass

    def _has_in_table_scope(self, name: str) -> bool:
        pass

    def _close_table_cell(self) -> bool:
        pass

    def _end_table_cell(self, name: str) -> None:
        pass

    def _flush_pending_table_text(self) -> None:
        pass

    def _close_table_element(self) -> bool:
        pass

    def _reset_insertion_mode(self) -> None:
        # Walk stack backwards - html element always terminates
        pass

    def _should_foster_parenting(self, target: Any, *, for_tag: str | None = None, is_text: bool = False) -> bool:
        pass

    def _lower_ascii(self, value: str) -> str:
        pass

    def _adjust_svg_tag_name(self, name: str) -> str:
        pass

    def _prepare_foreign_attributes(self, namespace: str, attrs: dict[str, str | None]) -> dict[str, str | None]:
        pass

    def _node_attribute_value(self, node: Any, name: str) -> str | None:
        pass

    def _is_html_integration_point(self, node: Any) -> bool:
        # annotation-xml is an HTML integration point only with specific encoding values
        pass

    def _is_mathml_text_integration_point(self, node: Any) -> bool:
        pass

    def _adjusted_current_node(self) -> Any:
        pass

    def _should_use_foreign_content(self, token: AnyToken) -> bool:
        pass

    def _foreign_breakout_font(self, tag: Any) -> bool:
        pass

    def _pop_until_html_or_integration_point(self) -> None:
        # Always terminates: html element has html namespace
        pass

    def _process_foreign_content(self, token: AnyToken) -> Any | None:
        pass

    def _appropriate_insertion_location(
        self, override_target: Any | None = None, *, foster_parenting: bool = False
    ) -> tuple[Any, int]:
        pass

    def _populate_selectedcontent(self, root: Any) -> None:
        """Populate selectedcontent elements with content from selected option.

        Per HTML5 spec: selectedcontent mirrors the content of the selected option,
        or the first option if none is selected.
        """
        pass

    def _find_elements(self, node: Any, name: str, result: list[Any]) -> None:
        """Find all elements with given name using iterative preorder traversal."""
        pass

    def _find_element(self, node: Any, name: str) -> Any | None:
        """Find first element with given name using iterative preorder traversal."""
        pass

    def _clone_children(self, source: Any, target: Any) -> None:
        """Deep clone all children from source to target."""
        pass

    def _has_in_scope(self, name: str) -> bool:
        pass

    def _has_in_list_item_scope(self, name: str) -> bool:
        pass

    def _has_in_definition_scope(self, name: str) -> bool:
        pass

    def _has_any_in_scope(self, names: set[str]) -> bool:
        # Always terminates: html is in DEFAULT_SCOPE_TERMINATORS
        pass

    def process_characters(self, data: str) -> Any:
        """Optimized path for character tokens."""
        pass
