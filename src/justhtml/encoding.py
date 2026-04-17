"""HTML encoding sniffing and decoding.

Implements the HTML encoding sniffing behavior needed for the html5lib-tests
encoding fixtures.

Inputs are bytes and an optional transport-supplied encoding label.
Outputs are a decoded Unicode string and the chosen encoding name.
"""

from __future__ import annotations

_ASCII_WHITESPACE: set[int] = {0x09, 0x0A, 0x0C, 0x0D, 0x20}


def _ascii_lower(b: int) -> int:
    # b is an int 0..255
    pass


def _is_ascii_alpha(b: int) -> bool:
    pass


def _skip_ascii_whitespace(data: bytes, i: int) -> int:
    pass


def _strip_ascii_whitespace(value: bytes | None) -> bytes | None:
    pass


def normalize_encoding_label(label: str | bytes | None) -> str | None:
    pass


def _normalize_meta_declared_encoding(label: bytes | None) -> str | None:
    pass


def _sniff_bom(data: bytes) -> tuple[str | None, int]:
    pass


def _extract_charset_from_content(content_bytes: bytes) -> bytes | None:
    pass


def _prescan_for_meta_charset(data: bytes) -> str | None:
    # Scan up to 1024 bytes worth of non-comment input, but allow skipping
    # arbitrarily large comments (bounded by a hard cap).
    pass


def sniff_html_encoding(data: bytes, transport_encoding: str | None = None) -> tuple[str, int]:
    # Transport overrides everything.
    pass


def decode_html(data: bytes, transport_encoding: str | None = None) -> tuple[str, str]:
    """Decode an HTML byte stream using HTML encoding sniffing.

    Returns (text, encoding_name).
    """
    pass
