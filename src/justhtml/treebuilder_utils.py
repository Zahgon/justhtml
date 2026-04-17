from __future__ import annotations

import enum
from typing import TYPE_CHECKING

from .constants import (
    HTML4_PUBLIC_PREFIXES,
    LIMITED_QUIRKY_PUBLIC_PREFIXES,
    QUIRKY_PUBLIC_MATCHES,
    QUIRKY_PUBLIC_PREFIXES,
    QUIRKY_SYSTEM_MATCHES,
)

if TYPE_CHECKING:
    from .tokens import Doctype


class InsertionMode(enum.IntEnum):
    INITIAL = 0
    BEFORE_HTML = 1
    BEFORE_HEAD = 2
    IN_HEAD = 3
    IN_HEAD_NOSCRIPT = 4
    AFTER_HEAD = 5
    TEXT = 6
    IN_BODY = 7
    AFTER_BODY = 8
    AFTER_AFTER_BODY = 9
    IN_TABLE = 10
    IN_TABLE_TEXT = 11
    IN_CAPTION = 12
    IN_COLUMN_GROUP = 13
    IN_TABLE_BODY = 14
    IN_ROW = 15
    IN_CELL = 16
    IN_FRAMESET = 17
    AFTER_FRAMESET = 18
    AFTER_AFTER_FRAMESET = 19
    IN_SELECT = 20
    IN_TEMPLATE = 21


def is_all_whitespace(text: str) -> bool:
    pass


def contains_prefix(haystack: tuple[str, ...], needle: str) -> bool:
    pass


def doctype_error_and_quirks(doctype: Doctype, iframe_srcdoc: bool = False) -> tuple[bool, str]:
    pass
