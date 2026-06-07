#!/usr/bin/env python3
"""edit.py — image-to-image / reference / mask edit CLI for the openai-image skill.

Usage:
  # Single-reference edit / restyle
  python3 scripts/edit.py -p "Make it a winter evening with heavy snowfall" \
      -i photo.png -f gpt_image_out/photo-winter.png
      -i woman.png -i dog.png --quality high -f gpt_image_out/combined.png
      -i photo.png -m sky_mask.png -f gpt_image_out/aurora.png

  python3 scripts/edit.py -p "..." -i photo.png --dry-run --verbose
  python3 scripts/edit.py -p "..." -i photo.png --json

Exit codes:
  0  success
  1  API / refusal error
  2  bad arguments or missing API key
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib.client import (  # noqa: E402
    call_with_retry,
    describe_endpoint,
    make_client,
    verbose_log_request,
)
from lib.image_io import (  # noqa: E402
    DEFAULT_OUT_DIRNAME,
    print_text_summary,
    resolve_out_dir,
    save_and_summarize,
    to_json_result,
)
from lib.params import (  # noqa: E402
    PROXY_FALLBACK_FIELDS,
    is_experimental,
    looks_like_unsupported_field_error,
    resolve_format,
    resolve_quality,
    resolve_size,
)

MAX_REFERENCE_IMAGES = 16
MAX_IMAGE_BYTES = 50 * 1024 * 1024
ALLOWED_IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp"}


def _emit_dry_run(args, kwargs, endpoint: str, out_dir: Path) -> None:
    """Print or JSON-dump the request that would be sent."""
    request = {
        "model": "gpt-image-2",
        "prompt": args.prompt,
        "size": args._size,
        "quality": args._quality,
        "n": args.n,
        "image": args.image,
    }
    if args.mask:
        request["mask"] = args.mask
    payload = {
        "ok": False,
        "dry_run": True,
        "endpoint": endpoint,
        "model": "gpt-image-2",
        "request": request,
        "output_dir": str(out_dir),
        "explicit_file": args.file,
    }
    if args.json_mode:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"endpoint: {endpoint}", file=sys.stderr)
        print(f"output_dir: {out_dir}", file=sys.stderr)
        if args.file:
            print(f"explicit_file: {args.file}", file=sys.stderr)
        print("--- request body (would send) ---", file=sys.stderr)
        for k, v in request.items():
            if k == "image":
                print(f"  image: <{len(args.image)} path(s)> -> {args.image}", file=sys.stderr)
            else:
                print(f"  {k}: {v!r}", file=sys.stderr)


def _open_image(path_str: str):
    p = Path(path_str).expanduser().resolve()
    if not p.exists():
        print(f"ERROR: image not found: {p}", file=sys.stderr)
        raise SystemExit(2)
    if p.suffix.lower() not in ALLOWED_IMAGE_EXTS:
        print(
            f"ERROR: {p}: unsupported extension {p.suffix}. "
            f"Allowed: {', '.join(sorted(ALLOWED_IMAGE_EXTS))}.",
            file=sys.stderr,
        )
        raise SystemExit(2)
    if p.stat().st_size > MAX_IMAGE_BYTES:
        print(
            f"ERROR: {p}: file is {p.stat().st_size:,} bytes, "
            f"max is {MAX_IMAGE_BYTES:,}.",
            file=sys.stderr,
        )
        raise SystemExit(2)
    return open(p, "rb")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="openai-image edit",
        description="Edit / restyle / inpaint images using gpt-image-2.",
    )
    p.add_argument("-p", "--prompt", required=True, help="edit instruction")
    p.add_argument(
        "-i", "--image", action="append", required=True,
        help=f"reference image path. Repeatable, up to {MAX_REFERENCE_IMAGES} images.",
    )
    p.add_argument(
        "-m", "--mask",
        help="optional mask PNG. Opaque = preserved, transparent = regenerated.",
    )
    p.add_argument(
        "-f", "--file",
        help="explicit output path (file or directory).",
    )
    p.add_argument(
        "--out-dir",
        default=None,
        help=(
            f"output directory when --file is not given. "
            f"Default: ./<{DEFAULT_OUT_DIRNAME}>/ (relative to the OpenCode "
            f"session's working directory)."
        ),
    )
    p.add_argument("-n", type=int, default=1, choices=[1],
                   help="number of images; forced to 1 (cost + UI use case). OpenAI gpt-image-2 supports n>1, but this skill restricts to 1.")
    p.add_argument("--size", default="auto", help="alias or WIDTHxHEIGHT (default: auto)")
    p.add_argument("--quality", default="high", help="low/medium/high/auto or alias (default: high)")
    p.add_argument("--format", dest="output_format", default="png", help="png/jpeg/webp (default: png)")

    out = p.add_argument_group("output & diagnostics")
    out.add_argument("--json", dest="json_mode", action="store_true",
                     help="emit a single JSON object to stdout (suitable for agents)")
    out.add_argument("--dry-run", dest="dry_run", action="store_true",
                     help="print the request body (with file paths) and exit")
    out.add_argument("-v", "--verbose", action="store_true",
                     help="print request body and retry progress to stderr")
    out.add_argument("--retries", type=int, default=3,
                     help="max retries on 429/5xx (default: 3)")
    out.add_argument("--quiet", action="store_true",
                     help="suppress the per-call 'saved:' / 'usage:' lines")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    if len(args.image) < 1:
        print("ERROR: at least one -i image is required", file=sys.stderr)
        return 2
    if len(args.image) > MAX_REFERENCE_IMAGES:
        print(
            f"ERROR: openai-image accepts at most {MAX_REFERENCE_IMAGES} reference images, "
            f"got {len(args.image)}.",
            file=sys.stderr,
        )
        return 2
    if not 1 <= args.n <= 10:
        print("ERROR: -n must be between 1 and 10", file=sys.stderr)
        return 2

    try:
        args._size = resolve_size(args.size)
        args._quality = resolve_quality(args.quality)
        args._format = resolve_format(args.output_format)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    if is_experimental(args._size):
        print(
            f"note: size {args._size} is in the experimental band; results may vary.",
            file=sys.stderr,
        )

    out_dir = resolve_out_dir(args.out_dir).resolve()
    endpoint = describe_endpoint()

    if args.dry_run:
        # Dry-run must not require the file to exist — agents may inspect
        # the payload before staging inputs.
        for p in args.image:
            ext = Path(p).suffix.lower()
            if ext not in ALLOWED_IMAGE_EXTS:
                print(
                    f"ERROR: {p}: unsupported extension {ext}. "
                    f"Allowed: {', '.join(sorted(ALLOWED_IMAGE_EXTS))}.",
                    file=sys.stderr,
                )
                return 2
        if args.mask:
            ext = Path(args.mask).suffix.lower()
            if ext != ".png":
                print(
                    f"ERROR: mask must be a PNG (got {ext}).",
                    file=sys.stderr,
                )
                return 2
        _emit_dry_run(args, kwargs=None, endpoint=endpoint, out_dir=out_dir)
        return 0

    image_handles = [_open_image(p) for p in args.image]
    mask_handle = _open_image(args.mask) if args.mask else None
    try:
        image_for_payload = image_handles if len(image_handles) > 1 else image_handles[0]
        kwargs = {
            "model": "gpt-image-2",
            "prompt": args.prompt,
            "image": image_for_payload,
            "size": args._size,
            "quality": args._quality,
            "n": args.n,
        }
        if mask_handle is not None:
            kwargs["mask"] = mask_handle

        if not args.json_mode:
            print(f"endpoint: {endpoint}", file=sys.stderr)
            print(
                f"model: gpt-image-2  size: {args._size}  quality: {args._quality}  "
                f"refs: {len(args.image)}  mask: {'yes' if mask_handle else 'no'}",
                file=sys.stderr,
            )
        if args.verbose:
            verbose_log_request("edit", {
                **{k: v for k, v in kwargs.items() if k not in ("image", "mask")},
                "image": [f"<{p}>" for p in args.image],
                "mask": args.mask,
            })

        client = make_client()
        response = None
        dropped: list[str] = []
        for attempt in range(len(PROXY_FALLBACK_FIELDS) + 1):
            try:
                response = call_with_retry(
                    client.images.edit, kwargs=kwargs,
                    max_retries=args.retries, verbose=args.verbose, label="edit",
                )
                break
            except Exception as e:  # noqa: BLE001
                bad = looks_like_unsupported_field_error(str(e))
                if bad and bad in kwargs and bad not in dropped:
                    print(
                        f"note: proxy rejected field {bad!r}; retrying without it.",
                        file=sys.stderr,
                    )
                    kwargs.pop(bad, None)
                    dropped.append(bad)
                    continue
                print(f"API error: {type(e).__name__}: {e}", file=sys.stderr)
                return 1
    finally:
        for h in image_handles:
            try:
                h.close()
            except Exception:
                pass
        if mask_handle is not None:
            try:
                mask_handle.close()
            except Exception:
                pass

    saved, usage = save_and_summarize(
        response,
        out_dir=out_dir,
        prompt=args.prompt,
        explicit_file=args.file,
        n=args.n,
        output_format=args._format,
        compression=None,   # edit endpoint doesn't accept output_compression
        json_mode=args.json_mode,
    )

    if args.json_mode:
        print(json.dumps(to_json_result(saved, usage, prompt=args.prompt,
                                        endpoint=endpoint, n=args.n),
                         ensure_ascii=False, indent=2))
    elif not args.quiet:
        print_text_summary(saved, usage)

    return 0


if __name__ == "__main__":
    sys.exit(main())
