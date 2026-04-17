from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Generator

from .encoding import decode_html
from .tokenizer import Tokenizer
from .tokens import CommentToken, DoctypeToken, Tag

# Type alias for stream events
StreamEvent = tuple[str, Any]


class _DummyNode:
    namespace: str = "html"


class StreamSink:
    """A sink that buffers tokens for the stream API."""

    tokens: list[StreamEvent]
    open_elements: list[_DummyNode]

    def __init__(self) -> None:
        self.tokens = []
        self.open_elements = []  # Required by tokenizer for rawtext checks

    def process_token(self, token: Tag | CommentToken | DoctypeToken | Any) -> int:
        # Tokenizer reuses token objects, so we must copy data
        pass

    def process_characters(self, data: str) -> None:
        """Handle character data from tokenizer."""
        pass


def stream(
    html: str | bytes | bytearray | memoryview,
    *,
    encoding: str | None = None,
) -> Generator[StreamEvent, None, None]:
    """
    Stream HTML events from the given HTML string.
    Yields tuples of (event_type, data).
    """
    pass
