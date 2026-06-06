"""Image decoding, output path management, and shared response handling
for the openai-image skill.

The OpenAI Images API always returns base64-encoded images (no URL option).
This module turns those into real files on disk, applies the output
naming convention described in SKILL.md, and offers a single
`save_and_summarize` function that both generate.py and edit.py call to
avoid duplication.
"""

from __future__ import annotations

import base64
import datetime as _dt
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Iterable, Optional

SKILL_ROOT = Path(__file__).resolve().parent.parent.parent

# Default per-project output directory name. Resolved against the
# process's current working directory at call time (see `resolve_out_dir`).
DEFAULT_OUT_DIRNAME = "gpt_image_out"

def _default_out_dir() -> Path:
    """Path.cwd() / gpt_image_out — the per-project default."""
    return Path.cwd() / DEFAULT_OUT_DIRNAME


# Backward-compat shim: kept for callers that import DEFAULT_OUT_DIR.
# New code should call `resolve_out_dir()` so cwd changes are honored at
# every invocation; this static value is captured at import time.
DEFAULT_OUT_DIR = _default_out_dir()


def resolve_out_dir(explicit: Optional[str] = None) -> Path:
    """Return the directory to write generated images to.

    Priority (highest first):
      1. `explicit` (the value of --out-dir)
      2. `<cwd>/gpt_image_out/` (the per-project default)

    The directory is *not* created here — callers that need an existing
    directory should pass the result through `ensure_dir()` (which
    `save_and_summarize` already does).
    """
    if explicit:
        return Path(explicit).expanduser()
    return _default_out_dir()


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def _slugify(text: str, max_len: int = 40) -> str:
    """Turn a prompt into a filesystem-safe slug. Empty -> 'image'."""
    s = text.strip().lower()
    s = re.sub(r"[^\w\u4e00-\u9fff-]+", "-", s, flags=re.UNICODE)
    s = re.sub(r"-+", "-", s).strip("-")
    if not s:
        return "image"
    return s[:max_len].rstrip("-")


def build_out_path(
    out_dir: Path,
    prompt: str,
    explicit: Optional[str] = None,
    index: int = 0,
    total: int = 1,
    suffix: str = "",
) -> Path:
    """Return a unique output path. If `explicit` is given, use it verbatim
    (still appending suffix/index for batching). Otherwise generate
    `out/YYYY-MM-DD-HH-MM-SS-<slug>.<ext>`.
    """
    ensure_dir(out_dir)
    ext = suffix if suffix else "png"
    if explicit:
        p = Path(explicit)
        if p.is_dir():
            stamp = _dt.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            return p / f"{stamp}-{_slugify(prompt)}.{ext}"
        if total > 1:
            stem = p.stem
            return p.with_name(f"{stem}_{index}{p.suffix or '.' + ext}")
        return p
    stamp = _dt.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    name = f"{stamp}-{_slugify(prompt)}.{ext}"
    if total > 1:
        stem, dot_ext = name.rsplit(".", 1)
        name = f"{stem}_{index}.{dot_ext}"
    return out_dir / name


def decode_b64_to_file(b64: str, dest: Path) -> Path:
    """Decode a base64 string to binary and write to `dest`. Returns dest."""
    data = base64.b64decode(b64)
    dest.parent.mkdir(parents=True, exist_ok=True)
    with open(dest, "wb") as f:
        f.write(data)
    return dest


# ---------------------------------------------------------------------------
# Response shape extraction (defensive: many proxies don't return the same
# fields as the official OpenAI SDK response objects).
# ---------------------------------------------------------------------------


def extract_usage(usage_obj: Any) -> dict:
    """Return a dict with input/output/image/text tokens, tolerating the
    many ways proxies may or may not populate the `usage` field.

    Returns a dict with all four keys set to 0 when nothing is available.
    """
    if usage_obj is None:
        return {"input_tokens": 0, "output_tokens": 0,
                "input_tokens_details": {"image_tokens": 0, "text_tokens": 0}}

    # Direct attribute access (official OpenAI SDK)
    def _get(obj, name, default=0):
        if obj is None:
            return default
        if isinstance(obj, dict):
            return obj.get(name, default)
        return getattr(obj, name, default)

    in_t = _get(usage_obj, "input_tokens")
    out_t = _get(usage_obj, "output_tokens")
    details = _get(usage_obj, "input_tokens_details", default=None)
    img_t = _get(details, "image_tokens")
    text_t = _get(details, "text_tokens")
    return {
        "input_tokens": int(in_t or 0),
        "output_tokens": int(out_t or 0),
        "input_tokens_details": {
            "image_tokens": int(img_t or 0),
            "text_tokens": int(text_t or 0),
        },
    }


def extract_b64_items(response: Any) -> list[str]:
    """Return the list of base64 strings from an images.generate / images.edit
    response. Tolerates the many shapes proxies may return."""
    if response is None:
        return []
    data = getattr(response, "data", None)
    if data is None and isinstance(response, dict):
        data = response.get("data")
    if not data:
        return []
    out: list[str] = []
    for item in data:
        b64 = None
        if isinstance(item, dict):
            b64 = item.get("b64_json")
        else:
            b64 = getattr(item, "b64_json", None)
        if b64:
            out.append(b64)
    return out


def extract_url_items(response: Any) -> list[str]:
    """Return the list of image URLs from an images.generate / images.edit
    response. The official OpenAI gpt-image-2 endpoint never returns URLs
    (b64_json is mandatory), but some OpenAI-compatible proxies (e.g.
    gpt-agent.cc) return URLs instead. Callers should fall back to this
    only when extract_b64_items returns an empty list."""
    if response is None:
        return []
    data = getattr(response, "data", None)
    if data is None and isinstance(response, dict):
        data = response.get("data")
    if not data:
        return []
    out: list[str] = []
    for item in data:
        url = None
        if isinstance(item, dict):
            url = item.get("url")
        else:
            url = getattr(item, "url", None)
        if url:
            out.append(url)
    return out


def download_url_to_b64(url: str, *, timeout: float = 30.0) -> str:
    """Fetch a remote image and return it base64-encoded. Stdlib only."""
    import urllib.request
    req = urllib.request.Request(url, headers={"User-Agent": "openai-image-skill/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read()
    return base64.b64encode(raw).decode("ascii")


# ---------------------------------------------------------------------------
# Shared save / summarise flow
# ---------------------------------------------------------------------------


def save_and_summarize(
    response: Any,
    *,
    out_dir: Path,
    prompt: str,
    explicit_file: Optional[str],
    n: int,
    output_format: str,
    compression: Optional[int],
    json_mode: bool = False,
) -> tuple[list[Path], dict]:
    """Decode the b64 items, write them, optionally re-encode JPEG/WebP with
    compression, append to the usage log, and return (saved_paths, summary_dict).

    In `json_mode=True` the dict is suitable for `json.dumps` to stdout.
    """
    ensure_dir(out_dir)
    b64s = extract_b64_items(response)
    if not b64s:
        urls = extract_url_items(response)
        if urls:
            print(
                f"note: response contains {len(urls)} url(s) but no b64_json; "
                f"downloading (proxy-specific fallback).",
                file=sys.stderr,
            )
            for url in urls:
                try:
                    b64s.append(download_url_to_b64(url))
                except Exception as e:  # noqa: BLE001
                    print(f"warning: failed to download {url[:80]}: {e}", file=sys.stderr)

    saved: list[Path] = []
    for i, b64 in enumerate(b64s):
        dest = build_out_path(
            out_dir=out_dir,
            prompt=prompt,
            explicit=explicit_file,
            index=i,
            total=n,
            suffix=output_format,
        )
        decode_b64_to_file(b64, dest)
        saved.append(dest)

    # Re-encode for jpeg/webp compression if requested.
    if output_format in ("jpeg", "webp") and compression is not None and saved:
        try:
            from PIL import Image
        except ImportError:
            if not json_mode:
                print("note: Pillow not installed; skipping compression re-encode", file=sys.stderr)
        else:
            for p in saved:
                with Image.open(p) as im:
                    im.save(p, output_format.upper(), quality=compression)
            if not json_mode:
                print(f"re-encoded {len(saved)} file(s) as {output_format} q={compression}", file=sys.stderr)

    usage = extract_usage(getattr(response, "usage", None))
    return saved, usage


def print_text_summary(saved: Iterable[Path], usage: dict) -> None:
    for p in saved:
        size = p.stat().st_size if p.exists() else 0
        print(f"saved: {p}  ({size:,} bytes)")
    if usage and (usage.get("input_tokens", 0) or usage.get("output_tokens", 0)):
        in_t = usage["input_tokens"]
        out_t = usage["output_tokens"]
        img_t = usage["input_tokens_details"]["image_tokens"]
        text_t = usage["input_tokens_details"]["text_tokens"]
        print(
            f"usage: input={in_t} (image={img_t}, text={text_t}) "
            f"output={out_t} total={in_t + out_t}"
        )


def to_json_result(saved: Iterable[Path], usage: dict, *, prompt: str,
                   endpoint: str, n: int) -> dict:
    """Build the final dict emitted on `--json`."""
    items = []
    for p in saved:
        items.append({
            "path": str(p),
            "bytes": p.stat().st_size if p.exists() else 0,
        })
    return {
        "ok": True,
        "endpoint": endpoint,
        "model": "gpt-image-2",
        "prompt": prompt,
        "n_requested": n,
        "n_returned": len(items),
        "files": items,
        "usage": usage,
    }
