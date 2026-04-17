"""Centralized error message definitions and helpers for JustHTML errors.

This module provides human-readable error messages for parse error codes
emitted by the tokenizer and tree builder during HTML parsing, plus selected
security findings emitted by the sanitizer.
"""

from __future__ import annotations


def generate_error_message(code: str, tag_name: str | None = None) -> str:
    """Generate human-readable error message from error code.

    Args:
        code: The error code string (kebab-case format)
        tag_name: Optional tag name to include in the message for context

    Returns:
        Human-readable error message string
    """
    pass
