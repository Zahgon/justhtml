"""Text linkification scanner.

This module finds URL/email-like substrings in plain text.

It is intentionally HTML-agnostic: in JustHTML it is applied to DOM text nodes,
not to raw HTML strings.

The behavior is driven by vendored compliance fixtures from the upstream
`linkify-it` project (MIT licensed). See `tests/linkify-it/README.md`.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Final


@dataclass(frozen=True, slots=True)
class LinkMatch:
    start: int
    end: int
    text: str
    href: str
    kind: str  # "url" | "email"


DEFAULT_TLDS: Final[frozenset[str]] = frozenset(
    {
        # Keep this aligned with linkify-it's default list.
        # See: https://github.com/markdown-it/linkify-it/blob/master/index.mjs
        "biz",
        "com",
        "edu",
        "gov",
        "net",
        "org",
        "pro",
        "web",
        "xxx",
        "aero",
        "asia",
        "coop",
        "info",
        "museum",
        "name",
        "shop",
        "рф",
    }
)


# A pragmatic Unicode-aware domain label pattern.
#
# Use `\w` for Unicode letters/digits (and underscore), and reject underscores
# during validation. This is intentionally stricter than allowing all non-ASCII
# codepoints, and matches the fixture behavior around delimiter punctuation.
_LABEL_RE: Final[str] = (
    r"[0-9A-Za-z\w\u2600-\u27bf]"
    r"(?:[0-9A-Za-z\w\u2600-\u27bf-]{0,61}[0-9A-Za-z\w\u2600-\u27bf])?"
)

# A fast-ish candidate matcher. We do real validation after we find a candidate.
_CANDIDATE_PATTERN: Final[str] = "".join(
    [
        r"(?i)([^0-9A-Za-z_])",  # left boundary (avoid matching after underscore)
        r"(",  # candidate group
        r"(?:https?|ftp)://[^\s<>\uFF5C]+",  # absolute URL
        r"|mailto:[^\s<>\uFF5C]+",  # mailto
        r"|//[^\s<>\uFF5C]+",  # protocol-relative
        r"|(?:www\.)[^\s<>\uFF5C]+",  # www.
        rf"|[0-9A-Za-z.!#$%&'*+/=?^_`{{|}}~\-\"]+@(?:{_LABEL_RE}\.)+{_LABEL_RE}",  # email
        r"|(?:\d{1,3}\.){3}\d{1,3}(?:/[^\s<>\uFF5C]*)?",  # IPv4
        rf"|(?:{_LABEL_RE}\.)+{_LABEL_RE}(?:/[^\s<>\uFF5C]*)?",  # fuzzy domain/path
        r")",
    ]
)

_CANDIDATE_RE: Final[re.Pattern[str]] = re.compile(_CANDIDATE_PATTERN, re.UNICODE)

_TRAILING_PUNCT: Final[str] = ".,;:!?"

# RE pattern for 2-character TLDs, copied from linkify-it (MIT licensed).
_CC_TLD_RE: Final[re.Pattern[str]] = re.compile(
    r"^(?:a[cdefgilmnoqrstuwxz]|b[abdefghijmnorstvwyz]|c[acdfghiklmnoruvwxyz]|d[ejkmoz]|e[cegrstu]|f[ijkmor]|g[abdefghilmnpqrstuwy]|h[kmnrtu]|i[delmnoqrst]|j[emop]|k[eghimnprwyz]|l[abcikrstuvy]|m[acdeghklmnopqrstuvwxyz]|n[acefgilopruz]|om|p[aefghklmnrstwy]|qa|r[eosuw]|s[abcdeghijklmnortuvxyz]|t[cdfghjklmnortvwz]|u[agksyz]|v[aceginu]|w[fs]|y[et]|z[amw])$",
    re.IGNORECASE,
)


def _is_valid_tld(tld: str, *, extra_tlds: frozenset[str]) -> bool:
    pass


def _split_domain_for_tld(host: str) -> tuple[str, str] | None:
    # Return (domain_without_tld, tld).
    pass


@dataclass(frozen=True, slots=True)
class LinkifyConfig:
    fuzzy_ip: bool = False
    extra_tlds: frozenset[str] = frozenset()

    @staticmethod
    def with_extra_tlds(extra_tlds: list[str] | tuple[str, ...] | set[str] | frozenset[str]) -> LinkifyConfig:
        pass


def _is_valid_ipv4(host: str) -> bool:
    pass


def _punycode_host(host: str) -> str:
    # Safety default: normalize Unicode domains to punycode for href.
    pass


def _split_host_and_rest(raw: str) -> tuple[str, str]:
    # raw is after an optional scheme prefix (or for fuzzy domains, the whole).
    # Extract host[:port] and the rest (path/query/fragment).
    pass


def _strip_wrapping(raw: str) -> tuple[str, int, int]:
    # Trim common wrappers like <...> or quotes, but report how many chars were removed
    # from start/end so we can compute accurate offsets.
    pass


def _trim_trailing(candidate: str) -> str:
    # Remove trailing punctuation and unbalanced closing brackets.
    pass


def _href_for(text: str) -> tuple[str, str]:
    pass


def _punycode_href(href: str) -> str:
    # Convert the host portion to punycode (IDNA), keeping the rest intact.
    pass


def find_links(text: str) -> list[LinkMatch]:
    pass


def find_links_with_config(text: str, config: LinkifyConfig) -> list[LinkMatch]:
    pass
