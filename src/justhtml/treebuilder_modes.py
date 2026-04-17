# ruff: noqa: S101, RUF012
# mypy: disable-error-code="attr-defined, has-type, var-annotated, assignment"

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

from .constants import (
    FORMAT_MARKER,
    FORMATTING_ELEMENTS,
    HEADING_ELEMENTS,
)
from .node import Comment, Node, Template
from .tokens import AnyToken, CharacterTokens, CommentToken, DoctypeToken, EOFToken, Tag, TokenSinkResult
from .treebuilder_utils import (
    InsertionMode,
    doctype_error_and_quirks,
    is_all_whitespace,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    ModeResultTuple = tuple[str, InsertionMode, AnyToken] | tuple[str, InsertionMode, AnyToken, bool]
    "Result is (instruction, mode, token) or (instruction, mode, token, force_html)"

_CLEAR_STACK_UNTIL_TABLE_TEMPLATE_HTML = frozenset(("table", "template", "html"))
_CLEAR_STACK_UNTIL_TBODY_TFOOT_THEAD_TEMPLATE_HTML = frozenset(("tbody", "tfoot", "thead", "template", "html"))
_CLEAR_STACK_UNTIL_TR_TEMPLATE_HTML = frozenset(("tr", "template", "html"))


class TreeBuilderModesMixin:
    def _handle_doctype(self, token: DoctypeToken) -> Literal[0]:
        pass

    def _mode_initial(self, token: Any) -> ModeResultTuple | None:
        pass

    def _mode_before_html(self, token: AnyToken) -> ModeResultTuple | None:
        pass

    def _mode_before_head(self, token: AnyToken) -> ModeResultTuple | None:
        pass

    def _mode_in_head(self, token: AnyToken) -> ModeResultTuple | None:
        pass

    def _mode_in_head_noscript(self, token: AnyToken) -> ModeResultTuple | None:
        """Handle tokens in 'in head noscript' insertion mode (scripting disabled)."""
        pass

    def _mode_after_head(self, token: AnyToken) -> ModeResultTuple | None:
        pass

    def _mode_text(self, token: AnyToken) -> ModeResultTuple | None:
        pass

    def _mode_in_body(self, token: Any) -> ModeResultTuple | None:
        pass

    def _handle_characters_in_body(self, token: CharacterTokens) -> None:
        pass

    def _handle_comment_in_body(self, token: CommentToken) -> None:
        pass

    def _handle_tag_in_body(self, token: Tag) -> ModeResultTuple | None:
        pass

    def _handle_eof_in_body(self, token: EOFToken) -> ModeResultTuple | None:
        # If we're in a template, handle EOF in template mode first
        pass

    # ---------------------
    # Body mode start tag handlers
    # ---------------------

    def _handle_body_start_html(self, token: Tag) -> None:
        pass

    def _handle_body_start_body(self, token: Tag) -> None:
        pass

    def _handle_body_start_head(self, token: Tag) -> None:
        pass

    def _handle_body_start_in_head(self, token: Tag) -> ModeResultTuple | None:
        pass

    def _handle_body_start_block_with_p(self, token: Tag) -> None:
        pass

    def _handle_body_start_heading(self, token: Tag) -> None:
        pass

    def _handle_body_start_pre_listing(self, token: Tag) -> None:
        pass

    def _handle_body_start_form(self, token: Tag) -> None:
        pass

    def _handle_body_start_button(self, token: Tag) -> None:
        pass

    def _handle_body_start_paragraph(self, token: Tag) -> None:
        pass

    def _handle_body_start_math(self, token: Tag) -> None:
        pass

    def _handle_body_start_svg(self, token: Tag) -> None:
        pass

    def _handle_body_start_li(self, token: Tag) -> None:
        pass

    def _handle_body_start_dd_dt(self, token: Tag) -> None:
        pass

    def _adoption_agency(self, subject: Any) -> None:
        # 1. If the current node is the subject, and it is not in the active formatting elements list...
        pass

    def _handle_body_start_a(self, token: Tag) -> None:
        pass

    def _handle_body_start_formatting(self, token: Tag) -> None:
        pass

    def _handle_body_start_applet_like(self, token: Tag) -> None:
        pass

    def _handle_body_start_br(self, token: Tag) -> None:
        pass

    def _handle_body_start_frameset(self, token: Tag) -> None:
        pass

    # ---------------------
    # Body mode end tag handlers
    # ---------------------

    def _handle_body_end_body(self, token: Tag) -> None:
        pass

    def _handle_body_end_html(self, token: Tag) -> ModeResultTuple | None:
        pass

    def _handle_body_end_p(self, token: Tag) -> None:
        pass

    def _handle_body_end_li(self, token: Tag) -> None:
        pass

    def _handle_body_end_dd_dt(self, token: Tag) -> None:
        pass

    def _handle_body_end_form(self, token: Tag) -> None:
        pass

    def _handle_body_end_applet_like(self, token: Tag) -> None:
        pass

    def _handle_body_end_heading(self, token: Tag) -> None:
        pass

    def _handle_body_end_block(self, token: Tag) -> None:
        pass

    def _handle_body_end_template(self, token: Tag) -> None:
        pass

    def _handle_body_start_structure_ignored(self, token: Tag) -> None:
        pass

    def _handle_body_start_col_or_frame(self, token: Tag) -> None:
        pass

    def _handle_body_start_image(self, token: Tag) -> None:
        pass

    def _handle_body_start_void_with_formatting(self, token: Tag) -> None:
        pass

    def _handle_body_start_simple_void(self, token: Tag) -> None:
        pass

    def _handle_body_start_input(self, token: Tag) -> None:
        pass

    def _handle_body_start_table(self, token: Tag) -> None:
        pass

    def _handle_body_start_plaintext_xmp(self, token: Tag) -> None:
        pass

    def _handle_body_start_noscript(self, token: Tag) -> None:
        pass

    def _handle_body_start_textarea(self, token: Tag) -> None:
        pass

    def _handle_body_start_select(self, token: Tag) -> None:
        pass

    def _handle_body_start_option(self, token: Tag) -> None:
        pass

    def _handle_body_start_optgroup(self, token: Tag) -> None:
        pass

    def _handle_body_start_rp_rt(self, token: Tag) -> None:
        pass

    def _handle_body_start_rb_rtc(self, token: Tag) -> None:
        pass

    def _handle_body_start_table_parse_error(self, token: Tag) -> None:
        pass

    def _handle_body_start_default(self, token: Tag) -> ModeResultTuple | None:
        pass

    def _mode_in_table(self, token: AnyToken) -> ModeResultTuple | None:
        pass

    def _mode_in_table_text(self, token: AnyToken) -> ModeResultTuple | None:
        pass

    def _mode_in_caption(self, token: AnyToken) -> ModeResultTuple | None:
        pass

    def _close_caption_element(self) -> bool:
        pass

    def _mode_in_column_group(self, token: AnyToken) -> ModeResultTuple | None:
        pass
        # Per spec: EOF when current is html - implicit None return

    def _mode_in_table_body(self, token: AnyToken) -> ModeResultTuple | None:
        pass

    def _mode_in_row(self, token: AnyToken) -> ModeResultTuple | None:
        pass

    def _end_tr_element(self) -> None:
        pass

    def _mode_in_cell(self, token: AnyToken) -> ModeResultTuple | None:
        pass

    def _mode_in_select(self, token: AnyToken) -> ModeResultTuple | None:
        pass

    def _mode_in_template(self, token: AnyToken) -> ModeResultTuple | None:
        # § The "in template" insertion mode
        # https://html.spec.whatwg.org/multipage/parsing.html#parsing-main-intemplate
        pass

    def _mode_after_body(self, token: AnyToken) -> ModeResultTuple | None:
        pass

    def _mode_after_after_body(self, token: AnyToken) -> ModeResultTuple | None:
        pass

    def _mode_in_frameset(self, token: AnyToken) -> ModeResultTuple | None:
        # Per HTML5 spec §13.2.6.4.16: In frameset insertion mode
        pass

    def _mode_after_frameset(self, token: AnyToken) -> ModeResultTuple | None:
        # Per HTML5 spec §13.2.6.4.17: After frameset insertion mode
        pass

    def _mode_after_after_frameset(self, token: AnyToken) -> ModeResultTuple | None:
        # Per HTML5 spec §13.2.6.4.18: After after frameset insertion mode
        pass

    # Helpers ----------------------------------------------------------------

    _MODE_HANDLERS: list[Callable[[TreeBuilderModesMixin, AnyToken], ModeResultTuple | None]] = [
        _mode_initial,
        _mode_before_html,
        _mode_before_head,
        _mode_in_head,
        _mode_in_head_noscript,
        _mode_after_head,
        _mode_text,
        _mode_in_body,
        _mode_after_body,
        _mode_after_after_body,
        _mode_in_table,
        _mode_in_table_text,
        _mode_in_caption,
        _mode_in_column_group,
        _mode_in_table_body,
        _mode_in_row,
        _mode_in_cell,
        _mode_in_frameset,
        _mode_after_frameset,
        _mode_after_after_frameset,
        _mode_in_select,
        _mode_in_template,
    ]

    _BODY_TOKEN_HANDLERS: dict[type[AnyToken], Callable[[TreeBuilderModesMixin, Any], ModeResultTuple | None]] = {
        CharacterTokens: _handle_characters_in_body,
        CommentToken: _handle_comment_in_body,
        Tag: _handle_tag_in_body,
        EOFToken: _handle_eof_in_body,
    }

    _BODY_START_HANDLERS: dict[str, Callable[[TreeBuilderModesMixin, Tag], ModeResultTuple | None]] = {
        "a": _handle_body_start_a,
        "address": _handle_body_start_block_with_p,
        "applet": _handle_body_start_applet_like,
        "area": _handle_body_start_void_with_formatting,
        "article": _handle_body_start_block_with_p,
        "aside": _handle_body_start_block_with_p,
        "b": _handle_body_start_formatting,
        "base": _handle_body_start_in_head,
        "basefont": _handle_body_start_in_head,
        "bgsound": _handle_body_start_in_head,
        "big": _handle_body_start_formatting,
        "blockquote": _handle_body_start_block_with_p,
        "body": _handle_body_start_body,
        "br": _handle_body_start_br,
        "button": _handle_body_start_button,
        "caption": _handle_body_start_table_parse_error,
        "center": _handle_body_start_block_with_p,
        "code": _handle_body_start_formatting,
        "col": _handle_body_start_col_or_frame,
        "colgroup": _handle_body_start_structure_ignored,
        "dd": _handle_body_start_dd_dt,
        "details": _handle_body_start_block_with_p,
        "dialog": _handle_body_start_block_with_p,
        "dir": _handle_body_start_block_with_p,
        "div": _handle_body_start_block_with_p,
        "dl": _handle_body_start_block_with_p,
        "dt": _handle_body_start_dd_dt,
        "em": _handle_body_start_formatting,
        "embed": _handle_body_start_void_with_formatting,
        "fieldset": _handle_body_start_block_with_p,
        "figcaption": _handle_body_start_block_with_p,
        "figure": _handle_body_start_block_with_p,
        "font": _handle_body_start_formatting,
        "footer": _handle_body_start_block_with_p,
        "form": _handle_body_start_form,
        "frame": _handle_body_start_col_or_frame,
        "frameset": _handle_body_start_frameset,
        "h1": _handle_body_start_heading,
        "h2": _handle_body_start_heading,
        "h3": _handle_body_start_heading,
        "h4": _handle_body_start_heading,
        "h5": _handle_body_start_heading,
        "h6": _handle_body_start_heading,
        "head": _handle_body_start_head,
        "header": _handle_body_start_block_with_p,
        "hgroup": _handle_body_start_block_with_p,
        "html": _handle_body_start_html,
        "i": _handle_body_start_formatting,
        "image": _handle_body_start_image,
        "img": _handle_body_start_void_with_formatting,
        "input": _handle_body_start_input,
        "keygen": _handle_body_start_void_with_formatting,
        "li": _handle_body_start_li,
        "link": _handle_body_start_in_head,
        "listing": _handle_body_start_pre_listing,
        "main": _handle_body_start_block_with_p,
        "marquee": _handle_body_start_applet_like,
        "math": _handle_body_start_math,
        "menu": _handle_body_start_block_with_p,
        "meta": _handle_body_start_in_head,
        "nav": _handle_body_start_block_with_p,
        "nobr": _handle_body_start_formatting,
        "noscript": _handle_body_start_noscript,
        "noframes": _handle_body_start_in_head,
        "object": _handle_body_start_applet_like,
        "ol": _handle_body_start_block_with_p,
        "optgroup": _handle_body_start_optgroup,
        "option": _handle_body_start_option,
        "p": _handle_body_start_paragraph,
        "param": _handle_body_start_simple_void,
        "plaintext": _handle_body_start_plaintext_xmp,
        "pre": _handle_body_start_pre_listing,
        "rb": _handle_body_start_rb_rtc,
        "rp": _handle_body_start_rp_rt,
        "rt": _handle_body_start_rp_rt,
        "rtc": _handle_body_start_rb_rtc,
        "s": _handle_body_start_formatting,
        "script": _handle_body_start_in_head,
        "search": _handle_body_start_block_with_p,
        "section": _handle_body_start_block_with_p,
        "select": _handle_body_start_select,
        "small": _handle_body_start_formatting,
        "source": _handle_body_start_simple_void,
        "strike": _handle_body_start_formatting,
        "strong": _handle_body_start_formatting,
        "style": _handle_body_start_in_head,
        "summary": _handle_body_start_block_with_p,
        "svg": _handle_body_start_svg,
        "table": _handle_body_start_table,
        "tbody": _handle_body_start_structure_ignored,
        "td": _handle_body_start_structure_ignored,
        "template": _handle_body_start_in_head,
        "textarea": _handle_body_start_textarea,
        "tfoot": _handle_body_start_structure_ignored,
        "th": _handle_body_start_structure_ignored,
        "thead": _handle_body_start_structure_ignored,
        "title": _handle_body_start_in_head,
        "tr": _handle_body_start_structure_ignored,
        "track": _handle_body_start_simple_void,
        "tt": _handle_body_start_formatting,
        "u": _handle_body_start_formatting,
        "ul": _handle_body_start_block_with_p,
        "wbr": _handle_body_start_void_with_formatting,
        "xmp": _handle_body_start_plaintext_xmp,
    }
    _BODY_END_HANDLERS: dict[str, Callable[[TreeBuilderModesMixin, Tag], ModeResultTuple | None]] = {
        "address": _handle_body_end_block,
        "applet": _handle_body_end_applet_like,
        "article": _handle_body_end_block,
        "aside": _handle_body_end_block,
        "blockquote": _handle_body_end_block,
        "body": _handle_body_end_body,
        "button": _handle_body_end_block,
        "center": _handle_body_end_block,
        "dd": _handle_body_end_dd_dt,
        "details": _handle_body_end_block,
        "dialog": _handle_body_end_block,
        "dir": _handle_body_end_block,
        "div": _handle_body_end_block,
        "dl": _handle_body_end_block,
        "dt": _handle_body_end_dd_dt,
        "fieldset": _handle_body_end_block,
        "figcaption": _handle_body_end_block,
        "figure": _handle_body_end_block,
        "footer": _handle_body_end_block,
        "form": _handle_body_end_form,
        "h1": _handle_body_end_heading,
        "h2": _handle_body_end_heading,
        "h3": _handle_body_end_heading,
        "h4": _handle_body_end_heading,
        "h5": _handle_body_end_heading,
        "h6": _handle_body_end_heading,
        "header": _handle_body_end_block,
        "hgroup": _handle_body_end_block,
        "html": _handle_body_end_html,
        "li": _handle_body_end_li,
        "listing": _handle_body_end_block,
        "main": _handle_body_end_block,
        "marquee": _handle_body_end_applet_like,
        "menu": _handle_body_end_block,
        "nav": _handle_body_end_block,
        "object": _handle_body_end_applet_like,
        "ol": _handle_body_end_block,
        "p": _handle_body_end_p,
        "pre": _handle_body_end_block,
        "search": _handle_body_end_block,
        "section": _handle_body_end_block,
        "summary": _handle_body_end_block,
        "table": _handle_body_end_block,
        "template": _handle_body_end_template,
        "ul": _handle_body_end_block,
    }
