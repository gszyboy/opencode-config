"""Size / quality / format alias resolution and validation for the OpenAI Images API.

The model accepts arbitrary WIDTHxHEIGHT strings but enforces:
  - both edges divisible by 16
  - aspect ratio between 1:3 and 3:1
  - longest edge <= 3840
  - total pixels between 655_360 and 8_294_400
Above 2560x1440 is "experimental" per the OpenAI API reference.
"""

from __future__ import annotations

import re
from typing import Optional

# Semantic aliases -> canonical pixel string the API expects.
SIZE_ALIASES: dict[str, str] = {
    "square": "1024x1024",
    "1k": "1024x1024",
    "1k-wide": "1536x1024",
    "1k-tall": "1024x1536",
    "2k": "2048x2048",
    "2k-wide": "2048x1152",
    "2k-tall": "1152x2048",
    "4k": "3840x2160",          # experimental
    "4k-tall": "2160x3840",     # experimental
    "portrait": "1024x1536",
    "landscape": "1536x1024",
    "wide": "1536x1024",
    "tall": "1024x1536",
    "auto": "auto",
}

QUALITY_ALIASES: dict[str, str] = {
    "draft": "low",
    "preview": "low",
    "normal": "medium",
    "standard": "medium",
    "final": "high",
    "print": "high",
}

VALID_QUALITY = {"low", "medium", "high", "auto"}
VALID_FORMAT = {"png", "jpeg", "webp"}
VALID_BACKGROUND = {"transparent", "opaque", "auto"}
VALID_MODERATION = {"low", "auto"}

# Fields that the official gpt-image-2 endpoint accepts but many OpenAI-compatible
# proxies reject (either they don't implement them or return 400). When a request
# fails with a 400 mentioning one of these field names, the caller can re-try
# without them.
PROXY_FALLBACK_FIELDS = (
    "background",
    "moderation",
    "output_compression",
    "output_format",
)

_PIXEL_RE = re.compile(r"^(\d+)x(\d+)$")
_MIN_PIXELS = 655_360
_MAX_PIXELS = 8_294_400
_MAX_EDGE = 3840
_EXPERIMENTAL_EDGE = 2560


def resolve_size(value: str) -> str:
    """Resolve an alias or a literal WxH into the canonical size string."""
    if value is None:
        return "auto"
    key = value.strip().lower()
    if key in SIZE_ALIASES:
        return SIZE_ALIASES[key]
    if key == "auto":
        return "auto"
    m = _PIXEL_RE.match(key)
    if not m:
        raise ValueError(
            f"invalid size: {value!r}. Use an alias "
            f"({', '.join(sorted(SIZE_ALIASES))}) or literal WIDTHxHEIGHT."
        )
    w, h = int(m.group(1)), int(m.group(2))
    if w % 16 != 0 or h % 16 != 0:
        raise ValueError(f"size {w}x{h}: both edges must be multiples of 16")
    long_edge = max(w, h)
    short_edge = min(w, h)
    if long_edge > _MAX_EDGE:
        raise ValueError(f"size {w}x{h}: longest edge must be <= {_MAX_EDGE}")
    if short_edge == 0 or (long_edge / short_edge) > 3.0:
        raise ValueError(f"size {w}x{h}: aspect ratio must be between 1:3 and 3:1")
    total = w * h
    if total < _MIN_PIXELS or total > _MAX_PIXELS:
        raise ValueError(
            f"size {w}x{h}: total pixels must be between {_MIN_PIXELS} and {_MAX_PIXELS}"
        )
    return f"{w}x{h}"


def is_experimental(size: str) -> bool:
    """Sizes with any edge > 2560 are experimental per OpenAI docs."""
    m = _PIXEL_RE.match(size)
    if not m:
        return False
    return max(int(m.group(1)), int(m.group(2))) > _EXPERIMENTAL_EDGE


def resolve_quality(value: Optional[str]) -> str:
    if value is None or value == "":
        return "high"
    key = value.strip().lower()
    if key in VALID_QUALITY:
        return key
    if key in QUALITY_ALIASES:
        return QUALITY_ALIASES[key]
    raise ValueError(
        f"invalid quality: {value!r}. Allowed: {', '.join(sorted(VALID_QUALITY))} "
        f"or aliases ({', '.join(sorted(QUALITY_ALIASES))})."
    )


def resolve_format(value: Optional[str]) -> str:
    if value is None or value == "":
        return "png"
    key = value.strip().lower()
    if key in VALID_FORMAT:
        return key
    if key == "jpg":
        return "jpeg"
    raise ValueError(f"invalid format: {value!r}. Allowed: {', '.join(sorted(VALID_FORMAT))}.")


def resolve_background(value: Optional[str]) -> str:
    if value is None or value == "":
        return "auto"
    key = value.strip().lower()
    if key in VALID_BACKGROUND:
        return key
    raise ValueError(f"invalid background: {value!r}. Allowed: {', '.join(sorted(VALID_BACKGROUND))}.")


def resolve_moderation(value: Optional[str]) -> str:
    if value is None or value == "":
        return "auto"
    key = value.strip().lower()
    if key in VALID_MODERATION:
        return key
    raise ValueError(f"invalid moderation: {value!r}. Allowed: {', '.join(sorted(VALID_MODERATION))}.")


def looks_like_unsupported_field_error(message: str) -> Optional[str]:
    """Inspect a 400-style error string and return the first PROXY_FALLBACK_FIELDS
    name mentioned, or None. Used to drive a transparent retry without that field."""
    if not message:
        return None
    lower = message.lower()
    for f in PROXY_FALLBACK_FIELDS:
        if f in lower:
            return f
    return None
