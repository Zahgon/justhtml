"""HTML sanitization policy API.

This module defines the public API for JustHTML sanitization.

The sanitizer operates on the parsed JustHTML DOM and is intentionally
policy-driven.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Collection, Mapping
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import TYPE_CHECKING, Any, Literal, cast
from urllib.parse import quote, urlsplit

from .tokens import ParseError

UrlFilter = Callable[[str, str, str], str | None]


class UnsafeHtmlError(ValueError):
    """Raised when unsafe HTML is encountered and unsafe_handling='raise'."""


UnsafeHandling = Literal["strip", "raise", "collect"]

DisallowedTagHandling = Literal["unwrap", "escape", "drop"]

UrlHandling = Literal["allow", "strip", "proxy"]


@dataclass(frozen=True, slots=True)
class UrlProxy:
    url: str
    param: str = "url"

    def __post_init__(self) -> None:
        proxy_url = str(self.url)
        if not proxy_url:
            raise ValueError("UrlProxy.url must be a non-empty string")
        object.__setattr__(self, "url", proxy_url)
        object.__setattr__(self, "param", str(self.param))


@dataclass(frozen=True, slots=True)
class UrlRule:
    """Rule for a single URL-valued attribute (e.g. a[href], img[src]).

    This is intentionally rendering-oriented.

    - Returning/keeping a URL can still cause network requests when the output
        is rendered (notably for <img src>). Applications like email viewers often
        want to block remote loads by default.
    """

    # Allow same-document fragments (#foo). Typically safe.
    allow_fragment: bool = True

    # If set, protocol-relative URLs (//example.com) are resolved to this scheme
    # (e.g. "https") before checking allowed_schemes.
    # If None, protocol-relative URLs are disallowed.
    resolve_protocol_relative: str | None = "https"

    # Allow absolute URLs with these schemes (lowercase), e.g. {"https"}.
    # If empty, all absolute URLs with a scheme are disallowed.
    allowed_schemes: Collection[str] = field(default_factory=set)

    # If provided, absolute URLs are allowed only if the parsed host is in this
    # allowlist.
    allowed_hosts: Collection[str] | None = None

    # Optional per-rule handling override.
    # If None, the URL is kept ("allow") after it passes validation.
    handling: UrlHandling | None = None

    # Optional per-rule override of UrlPolicy.default_allow_relative.
    # If None, UrlPolicy.default_allow_relative is used.
    allow_relative: bool | None = None

    # Optional proxy override for absolute/protocol-relative URLs.
    # Used when the effective URL handling is "proxy".
    proxy: UrlProxy | None = None

    def __post_init__(self) -> None:
        # Accept lists/tuples from user code, normalize for internal use.
        if not isinstance(self.allowed_schemes, set):
            object.__setattr__(self, "allowed_schemes", set(self.allowed_schemes))
        if self.allowed_hosts is not None and not isinstance(self.allowed_hosts, set):
            object.__setattr__(self, "allowed_hosts", set(self.allowed_hosts))

        if self.proxy is not None and not isinstance(self.proxy, UrlProxy):
            raise TypeError("UrlRule.proxy must be a UrlProxy or None")

        if self.handling is not None:
            mode = str(self.handling)
            if mode not in {"allow", "strip", "proxy"}:
                raise ValueError("Invalid UrlRule.handling. Expected one of: 'allow', 'strip', 'proxy'")
            object.__setattr__(self, "handling", mode)

        if self.allow_relative is not None:
            object.__setattr__(self, "allow_relative", bool(self.allow_relative))


@dataclass(frozen=True, slots=True)
class UrlPolicy:
    # Default handling for URL-like attributes after they pass UrlRule checks.
    # - "allow": keep the URL as-is
    # - "strip": drop the attribute
    # - "proxy": rewrite the URL through a proxy (UrlPolicy.proxy or UrlRule.proxy)
    default_handling: UrlHandling = "strip"

    # Default allowance for relative URLs (including /path, ./path, ../path, ?query)
    # for URL-like attributes that have a matching UrlRule.
    default_allow_relative: bool = True

    # Rule configuration for URL-valued attributes.
    allow_rules: Mapping[tuple[str, str], UrlRule] = field(default_factory=dict)

    # Optional hook that can drop or rewrite URLs.
    # url_filter(tag, attr, value) should return:
    # - a replacement string to keep (possibly rewritten), or
    # - None to drop the attribute.
    url_filter: UrlFilter | None = None

    # Default proxy config used when a rule is handled with "proxy" and
    # the rule does not specify its own UrlRule.proxy override.
    proxy: UrlProxy | None = None

    def __post_init__(self) -> None:
        mode = str(self.default_handling)
        if mode not in {"allow", "strip", "proxy"}:
            raise ValueError("Invalid default_handling. Expected one of: 'allow', 'strip', 'proxy'")
        object.__setattr__(self, "default_handling", mode)

        object.__setattr__(self, "default_allow_relative", bool(self.default_allow_relative))

        if not isinstance(self.allow_rules, dict):
            object.__setattr__(self, "allow_rules", dict(self.allow_rules))

        if self.proxy is not None and not isinstance(self.proxy, UrlProxy):
            raise TypeError("UrlPolicy.proxy must be a UrlProxy or None")

        # Validate proxy configuration for any rules that are in proxy mode.
        for rule in self.allow_rules.values():
            if not isinstance(rule, UrlRule):
                raise TypeError("UrlPolicy.allow_rules values must be UrlRule")
            if rule.handling == "proxy" and self.proxy is None and rule.proxy is None:
                raise ValueError("UrlRule.handling='proxy' requires a UrlPolicy.proxy or a per-rule UrlRule.proxy")


def _proxy_url_value(*, proxy: UrlProxy, value: str) -> str:
    pass


@dataclass(slots=True)
class UnsafeHandler:
    """Centralized handler for security findings.

    This is intentionally a small stateful object so multiple sanitization-
    related passes/transforms can share the same unsafe-handling behavior and
    (in collect mode) append into the same error list.
    """

    unsafe_handling: UnsafeHandling

    # Optional external sink (e.g. a JustHTML document's .errors list).
    # When set and unsafe_handling == "collect", security findings are written
    # into that list so multiple components can share a single sink.
    sink: list[ParseError] | None = None

    _errors: list[ParseError] | None = None

    def reset(self) -> None:
        pass

    def collected(self) -> list[ParseError]:
        pass

    def handle(self, msg: str, *, node: Any | None = None) -> None:
        pass


@dataclass(frozen=True, slots=True)
class SanitizationPolicy:
    """An allow-list driven policy for sanitizing a parsed DOM.

    This API is intentionally small. The implementation will interpret these
    fields strictly.

    - Tags not in `allowed_tags` are disallowed.
    - Attributes not in `allowed_attributes[tag]` (or `allowed_attributes["*"]`)
      are disallowed.
    - URL scheme checks apply to attributes listed in `url_attributes`.

    All tag and attribute names are expected to be ASCII-lowercase.
    """

    allowed_tags: frozenset[str]
    allowed_attributes: Mapping[str, Collection[str]]

    if TYPE_CHECKING:

        def __init__(
            self,
            allowed_tags: Collection[str],
            allowed_attributes: Mapping[str, Collection[str]],
            url_policy: UrlPolicy = ...,
            drop_comments: bool = True,
            drop_doctype: bool = True,
            drop_foreign_namespaces: bool = True,
            drop_content_tags: Collection[str] = ...,
            allowed_css_properties: Collection[str] = ...,
            force_link_rel: Collection[str] = ...,
            unsafe_handling: UnsafeHandling = "strip",
            disallowed_tag_handling: DisallowedTagHandling = "unwrap",
            strip_invisible_unicode: bool = True,
        ) -> None: ...

    # URL handling.
    url_policy: UrlPolicy = field(default_factory=UrlPolicy)

    drop_comments: bool = True
    drop_doctype: bool = True
    drop_foreign_namespaces: bool = True

    # Dangerous containers whose text payload should not be preserved.
    drop_content_tags: Collection[str] = field(default_factory=lambda: {"script", "style"})

    # Inline style allowlist.
    # Only applies when the `style` attribute is allowed for a tag.
    # If empty, inline styles are effectively disabled (style attributes are dropped).
    allowed_css_properties: Collection[str] = field(default_factory=set)

    # Link hardening.
    # If non-empty, ensure these tokens are present in <a rel="...">.
    # (The sanitizer will merge tokens; it will not remove existing ones.)
    force_link_rel: Collection[str] = field(default_factory=set)

    # Determines how unsafe input is handled.
    #
    # - "strip": Default. Remove/drop unsafe constructs and keep going.
    # - "raise": Raise UnsafeHtmlError on the first unsafe construct.
    #
    # This is intentionally a string mode (instead of a boolean) so we can add
    # more behaviors over time without changing the API shape.
    unsafe_handling: UnsafeHandling = "strip"

    # Determines how disallowed tags are handled.
    #
    # - "unwrap": Default. Drop the tag but keep/sanitize its children.
    # - "escape": Emit original tag tokens as text, keep/sanitize children.
    # - "drop": Drop the entire disallowed subtree.
    disallowed_tag_handling: DisallowedTagHandling = "unwrap"

    # Strip invisible Unicode commonly abused for obfuscation in text and
    # attribute values, such as variation selectors, zero-width/bidi controls,
    # and private-use characters.
    strip_invisible_unicode: bool = True

    _unsafe_handler: UnsafeHandler = field(
        default_factory=lambda: UnsafeHandler("strip"),
        init=False,
        repr=False,
        compare=False,
    )

    # Internal caches to avoid per-node allocations in hot paths.
    _allowed_attrs_global: frozenset[str] = field(
        default_factory=frozenset,
        init=False,
        repr=False,
        compare=False,
    )
    _allowed_attrs_by_tag: dict[str, frozenset[str]] = field(
        default_factory=dict,
        init=False,
        repr=False,
        compare=False,
    )

    # Cache for the compiled `Sanitize(policy=...)` transform pipeline.
    # This lets safe serialization reuse the same compiled transforms.
    _compiled_sanitize_transforms: list[Any] | None = field(
        default=None,
        init=False,
        repr=False,
        compare=False,
    )
    _compiled_sanitize_signature: Any = field(
        default=None,
        init=False,
        repr=False,
        compare=False,
    )

    def __post_init__(self) -> None:
        # Validate and normalize allowlists once so the sanitizer can do fast
        # membership checks.
        #
        # NOTE: Strings are iterables in Python. Passing e.g. "div" or
        # "attribute" by mistake would otherwise silently become a set of
        # characters ("d", "i", "v"), producing surprising behavior.
        if isinstance(self.allowed_tags, str):
            raise TypeError(
                "SanitizationPolicy.allowed_tags must be a collection of tag names (e.g. ['div']), not a string"
            )

        if isinstance(self.allowed_attributes, str) or not isinstance(self.allowed_attributes, Mapping):
            raise TypeError(
                "SanitizationPolicy.allowed_attributes must be a mapping like {'*': ['id'], 'a': ['href']}"
            )

        for tag, attrs in self.allowed_attributes.items():
            if isinstance(attrs, str):
                raise TypeError(
                    "SanitizationPolicy.allowed_attributes values must be collections of attribute names "
                    f"(e.g. {{'{tag}': ['class', 'id']}}), not a string"
                )

        normalized_tags = frozenset(str(t).strip().lower() for t in self.allowed_tags if str(t).strip())
        object.__setattr__(self, "allowed_tags", normalized_tags)

        normalized_attrs: dict[str, set[str]] = {}
        for tag, attrs in self.allowed_attributes.items():
            tag_name = str(tag).strip().lower()
            if not tag_name:
                raise ValueError("SanitizationPolicy.allowed_attributes contains an empty tag key")

            attr_set = attrs if isinstance(attrs, set) else set(attrs)
            normalized_attr_set = {str(a).strip().lower() for a in attr_set if str(a).strip()}

            if tag_name in normalized_attrs:
                normalized_attrs[tag_name].update(normalized_attr_set)
            else:
                normalized_attrs[tag_name] = normalized_attr_set

        object.__setattr__(self, "allowed_attributes", normalized_attrs)

        if not isinstance(self.drop_content_tags, set):
            object.__setattr__(self, "drop_content_tags", set(self.drop_content_tags))
        normalized_drop_content_tags = {str(t).strip().lower() for t in self.drop_content_tags if str(t).strip()}
        object.__setattr__(self, "drop_content_tags", normalized_drop_content_tags)

        if not isinstance(self.allowed_css_properties, set):
            object.__setattr__(self, "allowed_css_properties", set(self.allowed_css_properties))

        if not isinstance(self.force_link_rel, set):
            object.__setattr__(self, "force_link_rel", set(self.force_link_rel))

        unsafe_handling = str(self.unsafe_handling)
        if unsafe_handling not in {"strip", "raise", "collect"}:
            raise ValueError("Invalid unsafe_handling. Expected one of: 'strip', 'raise', 'collect'")
        object.__setattr__(self, "unsafe_handling", unsafe_handling)

        disallowed_tag_handling = str(self.disallowed_tag_handling)
        if disallowed_tag_handling not in {"unwrap", "escape", "drop"}:
            raise ValueError("Invalid disallowed_tag_handling. Expected one of: 'unwrap', 'escape', 'drop'")
        object.__setattr__(self, "disallowed_tag_handling", disallowed_tag_handling)
        object.__setattr__(self, "strip_invisible_unicode", bool(self.strip_invisible_unicode))

        # Centralize unsafe-handling logic so multiple passes can share it.
        handler = UnsafeHandler(cast("UnsafeHandling", unsafe_handling))
        handler.reset()
        object.__setattr__(self, "_unsafe_handler", handler)

        # Normalize rel tokens once so downstream sanitization can stay allocation-light.
        # (Downstream code expects lowercase tokens and ignores empty/whitespace.)
        if self.force_link_rel:
            normalized_force_link_rel = {t.strip().lower() for t in self.force_link_rel if str(t).strip()}
            object.__setattr__(self, "force_link_rel", normalized_force_link_rel)

        style_allowed = any("style" in attrs for attrs in self.allowed_attributes.values())
        if style_allowed and not self.allowed_css_properties:
            raise ValueError(
                "SanitizationPolicy allows the 'style' attribute but allowed_css_properties is empty. "
                "Either remove 'style' from allowed_attributes or set allowed_css_properties (for example CSS_PRESET_TEXT)."
            )

        allowed_attributes = self.allowed_attributes
        allowed_global = frozenset(allowed_attributes.get("*", ()))
        by_tag: dict[str, frozenset[str]] = {}
        for tag, attrs in allowed_attributes.items():
            if tag == "*":
                continue
            by_tag[tag] = frozenset(allowed_global.union(attrs))
        object.__setattr__(self, "_allowed_attrs_global", allowed_global)
        object.__setattr__(self, "_allowed_attrs_by_tag", by_tag)

    def reset_collected_security_errors(self) -> None:
        pass

    def collected_security_errors(self) -> list[ParseError]:
        pass

    def collects_security_errors_into(self, sink: list[ParseError]) -> bool:
        """Return True if security findings are being collected into `sink`.

        This is intentionally a small helper to avoid other modules depending
        on the private UnsafeHandler implementation details.
        """
        pass

    def handle_unsafe(self, msg: str, *, node: Any | None = None) -> None:
        pass


_URL_NORMALIZE_STRIP_TABLE = {i: None for i in range(0x21)}
_URL_NORMALIZE_STRIP_TABLE[0x7F] = None
_URL_NORMALIZE_STRIP_REGEX: re.Pattern[str] = re.compile(r"[\x00-\x20\x7f]")

# Invisible Unicode commonly abused for obfuscation includes zero-width and
# bidi controls, variation selectors, and private-use characters.
_INVISIBLE_UNICODE_STRIP_REGEX: re.Pattern[str] = re.compile(
    r"[\u061C\u200B-\u200F\u202A-\u202E\u2060-\u2069\uFE00-\uFE0F\uFEFF\uE000-\uF8FF"
    r"\U000E0100-\U000E01EF\U000F0000-\U000FFFFD\U00100000-\U0010FFFD]"
)

_ATTR_DROP_PATTERNS: tuple[str, ...] = ("on*", "srcdoc", "*:*")
_ATTR_DROP_REGEX: re.Pattern[str] = re.compile(
    "^(?:" + "|".join(re.escape(p).replace(r"\*", ".*").replace(r"\?", ".") for p in _ATTR_DROP_PATTERNS) + ")$"
)


def _compiled_sanitize_transforms_for_policy(policy: SanitizationPolicy) -> list[Any]:
    pass


def _seal_url_policy(url_policy: UrlPolicy) -> None:
    pass


def _seal_default_policy(policy: SanitizationPolicy) -> None:
    pass


DEFAULT_POLICY: SanitizationPolicy = SanitizationPolicy(
    allowed_tags=[
        # Text / structure
        "p",
        "br",
        # Structure
        "div",
        "span",
        "blockquote",
        "pre",
        "code",
        # Headings
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        # Lists
        "ul",
        "ol",
        "li",
        # Tables
        "table",
        "caption",
        "thead",
        "tbody",
        "tfoot",
        "tr",
        "th",
        "td",
        # Text formatting
        "b",
        "strong",
        "i",
        "em",
        "u",
        "s",
        "sub",
        "sup",
        "small",
        "mark",
        # Quotes/code
        # Line breaks
        "hr",
        # Links and images
        "a",
        "img",
    ],
    allowed_attributes={
        "*": ["class", "id", "title", "lang", "dir"],
        "a": ["href", "title"],
        "img": ["src", "alt", "title", "width", "height", "loading", "decoding"],
        "th": ["colspan", "rowspan"],
        "td": ["colspan", "rowspan"],
    },
    url_policy=UrlPolicy(
        default_handling="strip",
        allow_rules={
            ("a", "href"): UrlRule(
                allowed_schemes=["http", "https", "mailto", "tel"],
                resolve_protocol_relative="https",
            ),
            ("img", "src"): UrlRule(
                allowed_schemes=[],
                resolve_protocol_relative=None,
            ),
        },
    ),
    allowed_css_properties=set(),
)


# A conservative preset for allowing a small amount of inline styling.
# This is intentionally focused on text-level styling and avoids layout/
# positioning properties that are commonly abused for UI redress.
CSS_PRESET_TEXT: frozenset[str] = frozenset(
    {
        "background-color",
        "color",
        "font-size",
        "font-style",
        "font-weight",
        "letter-spacing",
        "line-height",
        "text-align",
        "text-decoration",
        "text-transform",
        "white-space",
        "word-break",
        "word-spacing",
        "word-wrap",
    }
)


DEFAULT_DOCUMENT_POLICY: SanitizationPolicy = SanitizationPolicy(
    allowed_tags=sorted(set(DEFAULT_POLICY.allowed_tags) | {"html", "head", "body", "title"}),
    allowed_attributes=DEFAULT_POLICY.allowed_attributes,
    url_policy=DEFAULT_POLICY.url_policy,
    drop_comments=DEFAULT_POLICY.drop_comments,
    drop_doctype=False,
    drop_foreign_namespaces=DEFAULT_POLICY.drop_foreign_namespaces,
    drop_content_tags=DEFAULT_POLICY.drop_content_tags,
    allowed_css_properties=DEFAULT_POLICY.allowed_css_properties,
    force_link_rel=DEFAULT_POLICY.force_link_rel,
    strip_invisible_unicode=DEFAULT_POLICY.strip_invisible_unicode,
)

_seal_default_policy(DEFAULT_POLICY)
_seal_default_policy(DEFAULT_DOCUMENT_POLICY)


_RAWTEXT_SERIALIZATION_ELEMENTS: frozenset[str] = frozenset({"script", "style"})


def _neutralize_rawtext_end_tag_sequences(text: str, tag_name: str) -> tuple[str, bool]:
    pass


def _record_rawtext_security_issue(
    *,
    policy: SanitizationPolicy,
    errors: list[ParseError] | None,
    code: str,
    message: str,
    node: Any,
) -> None:
    pass


def _sanitize_rawtext_element_contents(
    node: Any,
    *,
    policy: SanitizationPolicy,
    errors: list[ParseError] | None,
) -> None:
    pass


def _is_valid_css_property_name(name: str) -> bool:
    # Conservative: allow only ASCII letters/digits/hyphen.
    # This keeps parsing deterministic and avoids surprises with escapes.
    pass


def _css_value_contains_disallowed_functions(value: str, *, allow_url: bool) -> bool:
    # Extremely conservative check: reject any declaration value that contains a
    # CSS function/construct that can load external resources.
    #
    # We intentionally do not try to parse full CSS (escapes, strings, etc.).
    # Instead, we scan while ignoring ASCII whitespace/control chars and CSS
    # comments, and we look for dangerous tokens in the normalized stream.
    #
    # If allow_url=True, url(...) is not considered disallowed (it is handled
    # separately by `_sanitize_css_url_functions`).
    pass


def _css_value_may_load_external_resource(value: str) -> bool:
    pass


def _css_value_has_disallowed_resource_functions(value: str) -> bool:
    """Return True if `value` contains disallowed CSS constructs (excluding url())."""
    pass


def _lookup_css_url_rule(*, url_policy: UrlPolicy, tag: str, prop: str) -> UrlRule | None:
    pass


def _sanitize_url_function_value(
    *,
    rule: UrlRule,
    value: str,
    tag: str,
    attr: str,
    handling: UrlHandling,
    allow_relative: bool,
    proxy: UrlProxy | None,
    url_filter: UrlFilter | None,
    apply_filter: bool,
) -> str | None:
    # Keep this parser intentionally conservative. We only support plain url(...)
    # without escapes and without nested parentheses inside the URL token.
    pass


def _sanitize_css_url_functions(*, url_policy: UrlPolicy, tag: str, prop: str, value: str) -> str | None:
    pass


def _sanitize_inline_style(
    *,
    allowed_css_properties: Collection[str],
    value: str,
    tag: str,
    url_policy: UrlPolicy | None = None,
) -> str | None:
    pass


def _normalize_url_for_checking(value: str) -> str:
    # Strip whitespace/control chars commonly used for scheme obfuscation.
    # Note: do not strip backslashes; they are not whitespace/control chars,
    # and removing them can turn invalid schemes into valid ones.
    #
    # Fast path: most URLs contain no control/space chars, so avoid allocating.
    pass


def _strip_invisible_unicode(value: str) -> str:
    pass


def _is_valid_scheme(scheme: str) -> bool:
    pass


def _get_scheme(value: str) -> str | None:
    """Return the URL scheme (lowercased) if present and valid, else None."""
    pass


def _has_invalid_scheme_like_prefix(value: str) -> bool:
    pass


def _effective_proxy(*, url_policy: UrlPolicy, rule: UrlRule) -> UrlProxy | None:
    pass


def _effective_url_handling(*, url_policy: UrlPolicy, rule: UrlRule) -> UrlHandling:
    # URL-like attributes are allowlisted via UrlPolicy.allow_rules. When they are
    # allowlisted and the URL passes validation, the default action is to keep the URL.
    pass


def _effective_allow_relative(*, url_policy: UrlPolicy, rule: UrlRule) -> bool:
    pass


def _sanitize_url_value_with_rule(
    *,
    rule: UrlRule,
    value: str,
    tag: str,
    attr: str,
    handling: UrlHandling,
    allow_relative: bool,
    proxy: UrlProxy | None,
    url_filter: UrlFilter | None,
    apply_filter: bool,
) -> str | None:
    pass


def _sanitize_srcset_value(
    *,
    url_policy: UrlPolicy,
    rule: UrlRule,
    tag: str,
    attr: str,
    value: str,
) -> str | None:
    # Apply the URL filter once to the whole attribute value.
    pass


def _sanitize_space_separated_url_list(
    *,
    url_policy: UrlPolicy,
    rule: UrlRule,
    tag: str,
    attr: str,
    value: str,
) -> str | None:
    pass


_URL_LIKE_ATTRS: frozenset[str] = frozenset(
    {
        # Common URL-valued attributes.
        "href",
        "src",
        "srcset",
        "imagesrcset",
        "poster",
        "action",
        "formaction",
        "data",
        "cite",
        "background",
        # Can trigger requests/pings.
        "ping",
        "attributionsrc",
    }
)

_URL_FUNCTION_LIKE_ATTRS: frozenset[str] = frozenset(
    {
        "clip-path",
        "cursor",
        "fill",
        "marker-end",
        "marker-mid",
        "marker-start",
        "mask",
        "stroke",
    }
)


def _url_rule_signature(rule: UrlRule) -> tuple[Any, ...]:
    pass


def _url_policy_signature(url_policy: UrlPolicy) -> tuple[Any, ...]:
    pass


def _sanitization_policy_signature(policy: SanitizationPolicy) -> tuple[Any, ...]:
    pass


def _sanitize(node: Any, *, policy: SanitizationPolicy | None = None) -> Any:
    """Return a sanitized clone of `node`.

    This returns a sanitized clone without mutating the original tree.
    For performance, it builds the sanitized clone in a single pass.
    """
    pass


def sanitize_dom(
    node: Any,
    *,
    policy: SanitizationPolicy | None = None,
    errors: list[ParseError] | None = None,
) -> Any:
    """Sanitize a DOM tree in place.

    For document roots (`#document` or `#document-fragment`), this mutates the
    tree in place and returns the same root. For other nodes, the node is
    sanitized as if it were the only child of a document fragment; the returned
    node may need to be reattached by the caller.
    """
    pass
