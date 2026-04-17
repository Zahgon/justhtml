from __future__ import annotations

import re
from bisect import bisect_right
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable

from .entities import decode_entities_in_text
from .errors import generate_error_message
from .tokens import AnyToken, CharacterTokens, CommentToken, Doctype, DoctypeToken, EOFToken, ParseError, Tag

_ATTR_VALUE_UNQUOTED_TERMINATORS = "\t\n\f >&\"'<=`\0"
_ASCII_LOWER_TABLE = str.maketrans({chr(code): chr(code + 32) for code in range(65, 91)})
_RCDATA_ELEMENTS = {"title", "textarea"}
_RAWTEXT_SWITCH_TAGS = {
    "script",
    "style",
    "xmp",
    "iframe",
    "noembed",
    "noframes",
    "textarea",
    "title",
}

_ATTR_VALUE_DOUBLE_PATTERN = re.compile(r'["&\0]')
_ATTR_VALUE_SINGLE_PATTERN = re.compile(r"['&\0]")
_ATTR_VALUE_UNQUOTED_PATTERN = re.compile(f"[{re.escape(_ATTR_VALUE_UNQUOTED_TERMINATORS)}]")
_ATTR_VALUE_UNQUOTED_END_PATTERN = re.compile(r"[ \t\n\f>]")
_ATTR_VALUE_UNQUOTED_FAST_BAD_PATTERN = re.compile(r"""[\x00"'<=`]""")

_TAG_NAME_RUN_PATTERN = re.compile(r"[^\t\n\f />\0]+")
_ATTR_NAME_RUN_PATTERN = re.compile(r"[^\t\n\f />=\0\"'<]+")
_COMMENT_RUN_PATTERN = re.compile(r"[^-\0]+")

# XML Coercion Regex
_xml_invalid_single_chars = []
for _plane in range(17):
    _base = _plane * 0x10000
    _xml_invalid_single_chars.append(chr(_base + 0xFFFE))
    _xml_invalid_single_chars.append(chr(_base + 0xFFFF))

_XML_COERCION_PATTERN = re.compile(r"[\f\uFDD0-\uFDEF" + "".join(_xml_invalid_single_chars) + "]")


def _is_noncharacter_codepoint(codepoint: int) -> bool:
    pass


def _xml_coercion_callback(match: re.Match[str]) -> str:
    pass


def _coerce_text_for_xml(text: str) -> str:
    """Apply XML coercion to text content."""
    pass


def _coerce_comment_for_xml(text: str) -> str:
    """Apply XML coercion to comment content - handle double hyphens."""
    pass


class TokenizerOpts:
    __slots__ = (
        "discard_bom",
        "emit_bogus_markup_as_text",
        "exact_errors",
        "initial_rawtext_tag",
        "initial_state",
        "scripting_enabled",
        "xml_coercion",
    )

    discard_bom: bool
    exact_errors: bool
    initial_rawtext_tag: str | None
    initial_state: int | None
    scripting_enabled: bool
    xml_coercion: bool

    def __init__(
        self,
        exact_errors: bool = False,
        discard_bom: bool = True,
        emit_bogus_markup_as_text: bool = False,
        initial_state: int | None = None,
        initial_rawtext_tag: str | None = None,
        scripting_enabled: bool = True,
        xml_coercion: bool = False,
    ) -> None:
        self.exact_errors = bool(exact_errors)
        self.discard_bom = bool(discard_bom)
        self.emit_bogus_markup_as_text = bool(emit_bogus_markup_as_text)
        self.initial_state = initial_state
        self.initial_rawtext_tag = initial_rawtext_tag
        self.scripting_enabled = bool(scripting_enabled)
        self.xml_coercion = bool(xml_coercion)

    def copy(self) -> TokenizerOpts:
        """Return a shallow copy of these options.

        JustHTML may adjust some tokenizer options at runtime (based on e.g.
        fragment context and escape-mode sanitization). Copying avoids mutating
        a caller-provided TokenizerOpts instance.
        """
        return TokenizerOpts(
            exact_errors=self.exact_errors,
            discard_bom=self.discard_bom,
            emit_bogus_markup_as_text=self.emit_bogus_markup_as_text,
            initial_state=self.initial_state,
            initial_rawtext_tag=self.initial_rawtext_tag,
            scripting_enabled=self.scripting_enabled,
            xml_coercion=self.xml_coercion,
        )


class Tokenizer:
    DATA = 0
    TAG_OPEN = 1
    END_TAG_OPEN = 2
    TAG_NAME = 3
    BEFORE_ATTRIBUTE_NAME = 4
    ATTRIBUTE_NAME = 5
    AFTER_ATTRIBUTE_NAME = 6
    BEFORE_ATTRIBUTE_VALUE = 7
    ATTRIBUTE_VALUE_DOUBLE = 8
    ATTRIBUTE_VALUE_SINGLE = 9
    ATTRIBUTE_VALUE_UNQUOTED = 10
    AFTER_ATTRIBUTE_VALUE_QUOTED = 11
    SELF_CLOSING_START_TAG = 12
    MARKUP_DECLARATION_OPEN = 13
    COMMENT_START = 14
    COMMENT_START_DASH = 15
    COMMENT = 16
    COMMENT_END_DASH = 17
    COMMENT_END = 18
    COMMENT_END_BANG = 19
    BOGUS_COMMENT = 20
    DOCTYPE = 21
    BEFORE_DOCTYPE_NAME = 22
    DOCTYPE_NAME = 23
    AFTER_DOCTYPE_NAME = 24
    BOGUS_DOCTYPE = 25
    AFTER_DOCTYPE_PUBLIC_KEYWORD = 26
    AFTER_DOCTYPE_SYSTEM_KEYWORD = 27
    BEFORE_DOCTYPE_PUBLIC_IDENTIFIER = 28
    DOCTYPE_PUBLIC_IDENTIFIER_DOUBLE_QUOTED = 29
    DOCTYPE_PUBLIC_IDENTIFIER_SINGLE_QUOTED = 30
    AFTER_DOCTYPE_PUBLIC_IDENTIFIER = 31
    BETWEEN_DOCTYPE_PUBLIC_AND_SYSTEM_IDENTIFIERS = 32
    BEFORE_DOCTYPE_SYSTEM_IDENTIFIER = 33
    DOCTYPE_SYSTEM_IDENTIFIER_DOUBLE_QUOTED = 34
    DOCTYPE_SYSTEM_IDENTIFIER_SINGLE_QUOTED = 35
    AFTER_DOCTYPE_SYSTEM_IDENTIFIER = 36
    CDATA_SECTION = 37
    CDATA_SECTION_BRACKET = 38
    CDATA_SECTION_END = 39
    RCDATA = 40
    RCDATA_LESS_THAN_SIGN = 41
    RCDATA_END_TAG_OPEN = 42
    RCDATA_END_TAG_NAME = 43
    RAWTEXT = 44
    RAWTEXT_LESS_THAN_SIGN = 45
    RAWTEXT_END_TAG_OPEN = 46
    RAWTEXT_END_TAG_NAME = 47
    PLAINTEXT = 48
    SCRIPT_DATA_ESCAPED = 49
    SCRIPT_DATA_ESCAPED_DASH = 50
    SCRIPT_DATA_ESCAPED_DASH_DASH = 51
    SCRIPT_DATA_ESCAPED_LESS_THAN_SIGN = 52
    SCRIPT_DATA_ESCAPED_END_TAG_OPEN = 53
    SCRIPT_DATA_ESCAPED_END_TAG_NAME = 54
    SCRIPT_DATA_DOUBLE_ESCAPE_START = 55
    SCRIPT_DATA_DOUBLE_ESCAPED = 56
    SCRIPT_DATA_DOUBLE_ESCAPED_DASH = 57
    SCRIPT_DATA_DOUBLE_ESCAPED_DASH_DASH = 58
    SCRIPT_DATA_DOUBLE_ESCAPED_LESS_THAN_SIGN = 59
    SCRIPT_DATA_DOUBLE_ESCAPE_END = 60

    __slots__ = (
        "_comment_token",
        "_newline_positions",
        "_state_handlers",
        "_tag_token",
        "buffer",
        "collect_errors",
        "current_attr_name",
        "current_attr_value",
        "current_attr_value_has_amp",
        "current_char",
        "current_comment",
        "current_doctype_force_quirks",
        "current_doctype_name",
        "current_doctype_public",
        "current_doctype_system",
        "current_tag_attrs",
        "current_tag_kind",
        "current_tag_name",
        "current_tag_self_closing",
        "current_token_start_pos",
        "errors",
        "last_start_tag_name",
        "last_token_column",
        "last_token_line",
        "last_token_start_pos",
        "length",
        "opts",
        "original_tag_name",
        "pos",
        "rawtext_tag_name",
        "reconsume",
        "sink",
        "state",
        "temp_buffer",
        "text_buffer",
        "text_start_pos",
        "track_node_locations",
        "track_tag_positions",
    )

    _comment_token: CommentToken
    _newline_positions: list[int] | None
    _state_handlers: list[Callable[[Tokenizer], bool]]
    _tag_token: Tag
    buffer: str
    collect_errors: bool
    track_tag_positions: bool
    track_node_locations: bool
    current_attr_name: list[str]
    current_attr_value: list[str]
    current_attr_value_has_amp: bool
    current_char: str | None
    current_comment: list[str]
    current_doctype_force_quirks: bool
    current_doctype_name: list[str]
    current_doctype_public: list[str] | None
    current_doctype_system: list[str] | None
    current_tag_attrs: dict[str, str | None]
    current_tag_kind: int
    current_tag_name: list[str]
    current_tag_self_closing: bool
    current_token_start_pos: int
    errors: list[ParseError]
    last_start_tag_name: str | None
    last_token_column: int
    last_token_line: int
    last_token_start_pos: int | None
    length: int
    opts: TokenizerOpts
    original_tag_name: list[str]
    pos: int
    rawtext_tag_name: str | None
    reconsume: bool
    sink: Any
    state: int
    temp_buffer: list[str]
    text_buffer: list[str]
    text_start_pos: int

    # _STATE_HANDLERS is defined at the end of the file

    def __init__(
        self,
        sink: Any,
        opts: TokenizerOpts | None = None,
        *,
        collect_errors: bool = False,
        track_node_locations: bool = False,
        track_tag_positions: bool = False,
    ) -> None:
        self.sink = sink
        self.opts = opts or TokenizerOpts()
        self.collect_errors = collect_errors
        self.track_node_locations = bool(track_node_locations)
        self.track_tag_positions = bool(track_tag_positions)
        self.errors = []

        self.state = self.DATA
        self.buffer = ""
        self.length = 0
        self.pos = 0
        self.reconsume = False
        self.current_char = ""
        self.last_token_line = 1
        self.last_token_column = 0
        self.current_token_start_pos = 0
        self.last_token_start_pos = None

        # Reusable buffers to avoid per-token allocations.
        self.text_buffer = []
        self.text_start_pos = 0
        self.current_tag_name = []
        self.current_tag_attrs = {}
        self.current_attr_name = []
        self.current_attr_value = []
        self.current_attr_value_has_amp = False
        self.current_tag_self_closing = False
        self.current_tag_kind = Tag.START
        self.current_comment = []
        self.current_doctype_name = []
        self.current_doctype_public = None  # None = not set, [] = empty string
        self.current_doctype_system = None  # None = not set, [] = empty string
        self.current_doctype_force_quirks = False
        self.last_start_tag_name = None
        self.rawtext_tag_name = None
        self.original_tag_name = []
        self.temp_buffer = []
        self._tag_token = Tag(Tag.START, "", {}, False)
        self._comment_token = CommentToken("")

    def initialize(self, html: str | None) -> None:
        if html and html[0] == "\ufeff" and self.opts.discard_bom:
            html = html[1:]

        # Normalize newlines per §13.2.2.5
        if html:
            if "\r" in html:
                html = html.replace("\r\n", "\n").replace("\r", "\n")

        self.buffer = html or ""
        self.length = len(self.buffer)
        self.pos = 0
        self.reconsume = False
        self.current_char = ""
        self.last_token_line = 1
        self.last_token_column = 0
        self.current_token_start_pos = 0
        self.last_token_start_pos = None
        self.errors = []
        self.text_buffer.clear()
        self.text_start_pos = 0
        self.current_tag_name.clear()
        self.current_tag_attrs = {}
        self.current_attr_name.clear()
        self.current_attr_value.clear()
        self.current_attr_value_has_amp = False
        self.current_comment.clear()
        self.current_doctype_name.clear()
        self.current_doctype_public = None
        self.current_doctype_system = None
        self.current_doctype_force_quirks = False
        self.current_tag_self_closing = False
        self.current_tag_kind = Tag.START
        self.rawtext_tag_name = self.opts.initial_rawtext_tag
        self.temp_buffer.clear()
        self.last_start_tag_name = None
        self._tag_token.kind = Tag.START
        self._tag_token.name = ""
        self._tag_token.attrs = {}
        self._tag_token.self_closing = False
        self._tag_token.start_pos = None
        self._tag_token.end_pos = None

        initial_state = self.opts.initial_state
        if isinstance(initial_state, int):
            self.state = initial_state
        else:
            self.state = self.DATA

        # Pre-compute newline positions for O(log n) line lookups.
        # Only do this when errors are collected or when node locations are requested.
        if self.collect_errors or self.track_node_locations:
            self._newline_positions = []
            pos = -1
            buffer = self.buffer
            while True:
                pos = buffer.find("\n", pos + 1)
                if pos == -1:
                    break
                self._newline_positions.append(pos)
        else:
            self._newline_positions = None

    def _get_line_at_pos(self, pos: int) -> int:
        """Get line number (1-indexed) for a position using binary search."""
        pass

    def location_at_pos(self, pos: int) -> tuple[int, int]:
        """Return (line, column) for a 0-indexed offset in the current buffer.

        Column is 1-indexed. Newline positions are computed lazily when needed.
        """
        pass

    def step(self) -> bool:
        """Run one step of the tokenizer state machine. Returns True if EOF reached."""
        handler = self._STATE_HANDLERS[self.state]  # type: ignore[attr-defined]
        return handler(self)  # type: ignore[no-any-return]

    def run(self, html: str | None) -> None:
        pass

    # ---------------------
    # Helper methods
    # ---------------------

    def _peek_char(self, offset: int) -> str | None:
        """Peek ahead at character at current position + offset without consuming"""
        pass

    # ---------------------
    # State handlers
    # ---------------------

    def _state_data(self) -> bool:
        pass

    def _state_tag_open(self) -> bool:
        pass

    def _state_end_tag_open(self) -> bool:
        pass

    def _state_tag_name(self) -> bool:
        pass

    def _state_before_attribute_name(self) -> bool:
        pass

    def _state_attribute_name(self) -> bool:
        pass

    def _state_after_attribute_name(self) -> bool:
        pass

    def _state_before_attribute_value(self) -> bool:
        pass

    def _state_attribute_value_double(self) -> bool:
        pass

    def _state_attribute_value_single(self) -> bool:
        pass

    def _state_attribute_value_unquoted(self) -> bool:
        pass

    def _state_after_attribute_value_quoted(self) -> bool:
        """After attribute value (quoted) state per HTML5 spec §13.2.5.42"""
        pass

    def _state_self_closing_start_tag(self) -> bool:
        pass

    def _state_markup_declaration_open(self) -> bool:
        # Note: Comment handling (<!--) is optimized in DATA state fast-path
        # This code only handles DOCTYPE and CDATA, or malformed markup
        pass

    def _state_comment_start(self) -> bool:
        pass

    def _state_comment_start_dash(self) -> bool:
        pass

    def _state_comment(self) -> bool:
        pass

    def _state_comment_end_dash(self) -> bool:
        pass

    def _state_comment_end(self) -> bool:
        pass

    def _state_comment_end_bang(self) -> bool:
        pass

    def _state_bogus_comment(self) -> bool:
        pass

    def _state_doctype(self) -> bool:
        pass

    def _state_before_doctype_name(self) -> bool:
        pass

    def _state_doctype_name(self) -> bool:
        pass

    def _state_after_doctype_name(self) -> bool:
        pass

    def _state_after_doctype_public_keyword(self) -> bool:
        pass

    def _state_after_doctype_system_keyword(self) -> bool:
        pass

    def _state_before_doctype_public_identifier(self) -> bool:
        pass

    def _state_doctype_public_identifier_double_quoted(self) -> bool:
        pass

    def _state_doctype_public_identifier_single_quoted(self) -> bool:
        pass

    def _state_after_doctype_public_identifier(self) -> bool:
        pass

    def _state_between_doctype_public_and_system_identifiers(self) -> bool:
        pass

    def _state_before_doctype_system_identifier(self) -> bool:
        pass

    def _state_doctype_system_identifier_double_quoted(self) -> bool:
        pass

    def _state_doctype_system_identifier_single_quoted(self) -> bool:
        pass

    def _state_after_doctype_system_identifier(self) -> bool:
        pass

    def _state_bogus_doctype(self) -> bool:
        pass

    # ---------------------
    # Low-level helpers
    # ---------------------

    def _get_char(self) -> str | None:
        pass

    def _reconsume_current(self) -> None:
        pass

    def _append_text(self, text: str) -> None:
        """Append text to buffer, recording start position if this is the first chunk."""
        pass

    def _flush_text(self) -> None:
        pass
        # Note: process_characters never returns Plaintext or RawData
        # State switches happen via _emit_current_tag instead

    def _finish_attribute(self) -> None:
        pass

    def _emit_current_tag(self) -> bool:
        pass

    def _emit_incomplete_tag_as_text(self) -> None:
        pass

    def _emit_raw_end_tag_as_text(self, pos: int) -> bool:
        pass

    def _emit_comment(self) -> None:
        pass

    def _emit_doctype(self) -> None:
        pass

    def _emit_token(self, token: AnyToken) -> None:
        pass
        # Note: process_token never returns Plaintext or RawData for state switches
        # State switches happen via _emit_current_tag checking sink response

    def _record_token_position(self) -> None:
        """Record current position as 0-indexed column for the last emitted token.

        Per the spec, the position should be at the end of the token (after the last char).
        """
        pass

    def _record_text_end_position(self, raw_len: int) -> None:
        """Record position at end of text token (after last character).

        Uses text_start_pos + raw_len to compute where text ends, matching html5lib's
        behavior of reporting the column of the last character (1-indexed).
        """
        pass

    def _emit_error(self, code: str) -> None:
        pass

    def _emit_error_at_pos(self, code: str, pos: int) -> None:
        pass

    def _consume_if(self, literal: str) -> bool:
        pass

    def _consume_case_insensitive(self, literal: str) -> bool:
        pass

    def _consume_comment_run(self) -> bool:
        # Note: Comments are never reconsumed
        pass

    def _state_cdata_section(self) -> bool:
        # CDATA section state - consume characters until we see ']'
        pass

    def _state_cdata_section_bracket(self) -> bool:
        # Seen one ']', check for second ']'
        pass

    def _state_cdata_section_end(self) -> bool:
        # Seen ']]', check for '>'
        pass

    def _state_rcdata(self) -> bool:
        pass

    def _state_rcdata_less_than_sign(self) -> bool:
        pass

    def _state_rcdata_end_tag_open(self) -> bool:
        pass

    def _state_rcdata_end_tag_name(self) -> bool:
        # Check if this matches the opening tag name
        pass

    def _state_rawtext(self) -> bool:
        pass

    def _state_rawtext_less_than_sign(self) -> bool:
        pass

    def _state_rawtext_end_tag_open(self) -> bool:
        pass

    def _state_rawtext_end_tag_name(self) -> bool:
        # Check if this matches the opening tag name
        pass

    def _state_plaintext(self) -> bool:
        # PLAINTEXT state - consume everything as text, no end tag
        pass

    def _state_script_data_escaped(self) -> bool:
        pass

    def _state_script_data_escaped_dash(self) -> bool:
        pass

    def _state_script_data_escaped_dash_dash(self) -> bool:
        pass

    def _state_script_data_escaped_less_than_sign(self) -> bool:
        pass

    def _state_script_data_escaped_end_tag_open(self) -> bool:
        pass

    def _state_script_data_escaped_end_tag_name(self) -> bool:
        pass

    def _state_script_data_double_escape_start(self) -> bool:
        pass

    def _state_script_data_double_escaped(self) -> bool:
        pass

    def _state_script_data_double_escaped_dash(self) -> bool:
        pass

    def _state_script_data_double_escaped_dash_dash(self) -> bool:
        pass

    def _state_script_data_double_escaped_less_than_sign(self) -> bool:
        pass

    def _state_script_data_double_escape_end(self) -> bool:
        pass


Tokenizer._STATE_HANDLERS = [  # type: ignore[attr-defined]
    Tokenizer._state_data,
    Tokenizer._state_tag_open,
    Tokenizer._state_end_tag_open,
    Tokenizer._state_tag_name,
    Tokenizer._state_before_attribute_name,
    Tokenizer._state_attribute_name,
    Tokenizer._state_after_attribute_name,
    Tokenizer._state_before_attribute_value,
    Tokenizer._state_attribute_value_double,
    Tokenizer._state_attribute_value_single,
    Tokenizer._state_attribute_value_unquoted,
    Tokenizer._state_after_attribute_value_quoted,
    Tokenizer._state_self_closing_start_tag,
    Tokenizer._state_markup_declaration_open,
    Tokenizer._state_comment_start,
    Tokenizer._state_comment_start_dash,
    Tokenizer._state_comment,
    Tokenizer._state_comment_end_dash,
    Tokenizer._state_comment_end,
    Tokenizer._state_comment_end_bang,
    Tokenizer._state_bogus_comment,
    Tokenizer._state_doctype,
    Tokenizer._state_before_doctype_name,
    Tokenizer._state_doctype_name,
    Tokenizer._state_after_doctype_name,
    Tokenizer._state_bogus_doctype,
    Tokenizer._state_after_doctype_public_keyword,
    Tokenizer._state_after_doctype_system_keyword,
    Tokenizer._state_before_doctype_public_identifier,
    Tokenizer._state_doctype_public_identifier_double_quoted,
    Tokenizer._state_doctype_public_identifier_single_quoted,
    Tokenizer._state_after_doctype_public_identifier,
    Tokenizer._state_between_doctype_public_and_system_identifiers,
    Tokenizer._state_before_doctype_system_identifier,
    Tokenizer._state_doctype_system_identifier_double_quoted,
    Tokenizer._state_doctype_system_identifier_single_quoted,
    Tokenizer._state_after_doctype_system_identifier,
    Tokenizer._state_cdata_section,
    Tokenizer._state_cdata_section_bracket,
    Tokenizer._state_cdata_section_end,
    Tokenizer._state_rcdata,
    Tokenizer._state_rcdata_less_than_sign,
    Tokenizer._state_rcdata_end_tag_open,
    Tokenizer._state_rcdata_end_tag_name,
    Tokenizer._state_rawtext,
    Tokenizer._state_rawtext_less_than_sign,
    Tokenizer._state_rawtext_end_tag_open,
    Tokenizer._state_rawtext_end_tag_name,
    Tokenizer._state_plaintext,
    Tokenizer._state_script_data_escaped,
    Tokenizer._state_script_data_escaped_dash,
    Tokenizer._state_script_data_escaped_dash_dash,
    Tokenizer._state_script_data_escaped_less_than_sign,
    Tokenizer._state_script_data_escaped_end_tag_open,
    Tokenizer._state_script_data_escaped_end_tag_name,
    Tokenizer._state_script_data_double_escape_start,
    Tokenizer._state_script_data_double_escaped,
    Tokenizer._state_script_data_double_escaped_dash,
    Tokenizer._state_script_data_double_escaped_dash_dash,
    Tokenizer._state_script_data_double_escaped_less_than_sign,
    Tokenizer._state_script_data_double_escape_end,
]
