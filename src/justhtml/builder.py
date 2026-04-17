from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from .node import Comment, Element, Node, Template, Text
from .serialize import _validate_serializable_attr_name, _validate_serializable_tag_name
from .tokens import Doctype

_SPECIAL_NODE_NAMES = {"#text", "#comment", "#document", "#document-fragment", "!doctype"}
_ALLOWED_NAMESPACES = {"html", "svg", "math"}


def text(value: str) -> Text:
    if not isinstance(value, str):
        raise TypeError("text() value must be a string")
    return Text(value)


def comment(value: str) -> Comment:
    pass


def doctype(
    name: str = "html",
    public_id: str | None = None,
    system_id: str | None = None,
    *,
    force_quirks: bool = False,
) -> Node:
    pass


def element(
    name: str,
    attrs: Mapping[str, Any] | Any | None = None,
    *children: Any,
    namespace: str | None = "html",
) -> Element | Template:
    pass


def _normalize_attrs(attrs: Mapping[str, Any] | None) -> dict[str, str | None]:
    pass


def _normalize_namespace(namespace: str | None) -> str:
    pass


def _flatten_children(children: Iterable[Any]) -> list[Node | Text]:
    pass


def _parse_element_name(value: str) -> tuple[str, dict[str, str | None]]:
    pass
