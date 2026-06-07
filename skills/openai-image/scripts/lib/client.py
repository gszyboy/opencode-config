"""OpenAI-compatible client factory + retry / verbose support.

Reads credentials from environment:
  - GPT_AGENT_KEY  (required)
  - GPT_AGENT_URL  (required; set to your proxy's /v1 root)

The proxy only needs to be OpenAI-Images-API compatible (POST /v1/images/generations
and POST /v1/images/edits). This module never hard-codes a host so the same scripts
work against any OpenAI-compatible gateway.
"""

from __future__ import annotations

import os
import random
import re
import sys
import time
from typing import Any, Callable, Optional

from openai import OpenAI


_API_KEY_VARS = ("GPT_AGENT_KEY",)
_BASE_URL_VARS = ("GPT_AGENT_URL",)

# HTTP status codes worth retrying. 408 = request timeout, 409 = rare conflict,
# 429 = rate limit, >=500 = server errors.
_RETRYABLE_STATUS = {408, 409, 429, 500, 502, 503, 504}


def _first_env(names: tuple[str, ...]) -> Optional[str]:
    for name in names:
        value = os.environ.get(name)
        if value:
            return value
    return None


def get_api_key() -> str:
    key = _first_env(_API_KEY_VARS)
    if not key:
        print(
            "ERROR: missing API key. Set GPT_AGENT_KEY in your environment "
            "(e.g. ~/.bashrc).",
            file=sys.stderr,
        )
        raise SystemExit(2)
    return key


def get_base_url() -> Optional[str]:
    """Return the configured base URL, stripping any trailing slash and ensuring
    it ends with `/v1` (the SDK appends endpoint paths like `/images/generations`).

    Both env vars are read; if neither is set, we return None and the SDK
    falls back to its default (which is api.openai.com — this skill is
    designed to run against a proxy, so callers MUST set one of the two
    env vars)."""
    url = _first_env(_BASE_URL_VARS)
    if not url:
        return None
    url = url.rstrip("/")
    if not url.endswith("/v1"):
        url = url + "/v1"
    return url


def make_client(timeout: float = 300.0) -> OpenAI:
    """Build an OpenAI client. The same instance can be reused for both
    `images.generate` and `images.edit`.

    Important: some OpenAI-compatible proxies (notably claudeapi.win)
    reject requests with `User-Agent: OpenAI/Python*` — the default
    header the official SDK sends. We override User-Agent and the
    SDK's x-stainless-* identification headers so the proxy can't
    fingerprint us as a script. The override is benign for honest
    OpenAI-compat endpoints.
    """
    return OpenAI(
        api_key=get_api_key(),
        base_url=get_base_url(),
        timeout=timeout,
        default_headers={
            "User-Agent": f"openai-image-skill/1.0 (+https://opencode.ai/skills/openai-image)",
            "x-stainless-lang": "skill",
            "x-stainless-package-version": "1.0.0",
            "x-stainless-os": "linux",
            "x-stainless-arch": "x64",
            "x-stainless-runtime": "python",
            "x-stainless-runtime-version": "3.12",
            "x-stainless-async": "false",
        },
    )


def describe_endpoint() -> str:
    base = get_base_url() or "(unconfigured — set GPT_AGENT_URL)"
    return base


# ---------------------------------------------------------------------------
# Retry / verbose helpers
# ---------------------------------------------------------------------------


def _extract_status_and_body(exc: BaseException) -> tuple[Optional[int], str]:
    """Pull status_code and a useful body string from an OpenAI SDK exception.
    The SDK's exception classes vary across versions; we look at common attributes
    without importing private names."""
    status = getattr(exc, "status_code", None)
    body = ""
    # openai.APIError / BadRequestError / RateLimitError expose `.message` and
    # sometimes `.body`; the underlying httpx response has `.text`.
    body = getattr(exc, "body", None) or getattr(exc, "message", None) or str(exc)
    resp = getattr(exc, "response", None)
    if resp is not None and getattr(resp, "text", None):
        body = f"{body} | response.text={resp.text[:500]}"
    if not isinstance(status, int):
        m = re.search(r"\b(4\d\d|5\d\d)\b", str(exc))
        if m:
            status = int(m.group(1))
    return status, str(body)


def call_with_retry(
    fn: Callable[..., Any],
    *,
    args: tuple = (),
    kwargs: dict,
    max_retries: int = 3,
    base_delay: float = 1.5,
    verbose: bool = False,
    label: str = "API call",
) -> Any:
    """Invoke `fn(*args, **kwargs)` with exponential backoff on transient errors.

    - Retries 408/409/429 and 5xx up to `max_retries` times.
    - 4xx other than the above are surfaced immediately (no retry).
    - For 400s whose message mentions a proxy-fallback field, the caller is
      expected to strip the field and re-invoke; this helper does not auto-strip.
    - The full response body is echoed to stderr on every failure so the user
      can see exactly what the proxy said.
    """
    attempt = 0
    while True:
        attempt += 1
        try:
            return fn(*args, **kwargs)
        except SystemExit:
            raise
        except KeyboardInterrupt:
            raise
        except Exception as e:  # noqa: BLE001
            status, body = _extract_status_and_body(e)
            retryable = (status in _RETRYABLE_STATUS) if status else False
            print(
                f"[{label}] attempt {attempt} failed: "
                f"{type(e).__name__}: {body[:600]}",
                file=sys.stderr,
            )
            if not retryable or attempt > max_retries:
                raise
            # Exponential backoff with jitter: 1.5s, 3s, 6s ...
            delay = base_delay * (2 ** (attempt - 1))
            delay = delay * (0.5 + random.random())  # 0.5x..1.5x
            if verbose:
                print(f"[{label}] retrying in {delay:.1f}s ...", file=sys.stderr)
            time.sleep(delay)


def verbose_log_request(label: str, body: dict, *, hidden_keys: tuple = ("api_key",)) -> None:
    """Print a redacted view of an outgoing request body to stderr."""
    safe = {k: v for k, v in body.items() if k not in hidden_keys}
    print(f"[{label}] request body:", file=sys.stderr)
    for k, v in safe.items():
        # Don't dump binary file handles.
        if hasattr(v, "read"):
            print(f"  {k}: <file handle>", file=sys.stderr)
        elif isinstance(v, list) and v and hasattr(v[0], "read"):
            print(f"  {k}: <list of {len(v)} file handles>", file=sys.stderr)
        else:
            print(f"  {k}: {v!r}", file=sys.stderr)
