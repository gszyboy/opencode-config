#!/usr/bin/env python3
"""generate.py — text-to-image CLI for the openai-image skill.

Usage:
  python3 scripts/generate.py -p "A photorealistic cafe at golden hour" -f gpt_image_out/cafe.png
  python3 scripts/generate.py -p "..." --size portrait --quality high -n 4
  python3 scripts/generate.py -p "..." --dry-run --verbose
  python3 scripts/generate.py -p "..." --json

Exit codes:
  0  success
  1  API / refusal error (full response body echoed to stderr)
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
    resolve_background,
    resolve_format,
    resolve_moderation,
    resolve_quality,
    resolve_size,
)


def _build_kwargs(args: argparse.Namespace) -> dict:
    """Build the request kwargs for client.images.generate.

    `moderation` is always sent (claudeapi.win upstream supports it; verified
    with `moderation=low` returning 200). `background` is never sent —
    claudeapi.win upstream rejects the field for ANY value (both
    `transparent` and `opaque` return 422; verified). The OpenAI gpt-image-2
    API does support `background` natively, but this skill's default proxy
    does not forward it.
    """
    kwargs: dict = {
        "model": "gpt-image-2",
        "prompt": args.prompt,
        "size": args._size,
        "quality": args._quality,
        "n": args.n,
        "moderation": args._moderation,
    }
    return kwargs


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="openai-image generate",
        description="Generate images from a text prompt using gpt-image-2.",
    )
    p.add_argument("-p", "--prompt", required=True, help="text description")
    p.add_argument(
        "-f", "--file",
        help="explicit output path (file or directory). If a directory, "
             "a timestamped filename is created inside it.",
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
    p.add_argument("--size", default="1024x1024", help="alias or WIDTHxHEIGHT (default: 1024x1024)")
    p.add_argument("--quality", default="high", help="low/medium/high/auto or alias (default: high)")
    p.add_argument("--format", dest="output_format", default="png", help="png/jpeg/webp (default: png)")
    p.add_argument("--compression", type=int, default=None, help="0-100, only for jpeg/webp")
    p.add_argument("--background", default="auto", help="transparent/opaque/auto (default: auto)")
    p.add_argument("--moderation", default="auto", help="low/auto (default: auto)")

    # Output / diagnostics
    out = p.add_argument_group("output & diagnostics")
    out.add_argument("--json", dest="json_mode", action="store_true",
                     help="emit a single JSON object to stdout (suitable for piping into agents)")
    out.add_argument("--dry-run", dest="dry_run", action="store_true",
                     help="print the request body and exit without calling the API")
    out.add_argument("-v", "--verbose", action="store_true",
                     help="print request body and retry progress to stderr")
    out.add_argument("--stream", dest="stream", action="store_true",
                     help="enable streaming partial images (experimental)")
    out.add_argument("--partial-images", type=int, default=2,
                     help="number of partial images for --stream, 0-3 (default: 2)")
    out.add_argument("--retries", type=int, default=3,
                     help="max retries on 429/5xx (default: 3)")
    out.add_argument("--quiet", action="store_true",
                     help="suppress the per-call 'saved:' / 'usage:' lines")
    return p.parse_args(argv)


def _resolve_args(args: argparse.Namespace) -> None:
    """Resolve string aliases into canonical values. Mutates `args`."""
    try:
        args._size = resolve_size(args.size)
        args._quality = resolve_quality(args.quality)
        args._background = resolve_background(args.background)
        args._moderation = resolve_moderation(args.moderation)
        args._format = resolve_format(args.output_format)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        raise SystemExit(2)


def _validate_args(args: argparse.Namespace) -> None:
    if not 1 <= args.n <= 10:
        print("ERROR: -n must be between 1 and 10", file=sys.stderr)
        raise SystemExit(2)
    if args.compression is not None and not 0 <= args.compression <= 100:
        print("ERROR: --compression must be between 0 and 100", file=sys.stderr)
        raise SystemExit(2)
    if is_experimental(args._size):
        print(
            f"note: size {args._size} is in the experimental band (>2560 on the long edge); "
            f"results may vary.",
            file=sys.stderr,
        )


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    _resolve_args(args)
    _validate_args(args)

    kwargs = _build_kwargs(args)
    out_dir = resolve_out_dir(args.out_dir).resolve()
    endpoint = describe_endpoint()

    if args.dry_run:
        if args.json_mode:
            print(json.dumps({
                "ok": False,
                "dry_run": True,
                "endpoint": endpoint,
                "model": "gpt-image-2",
                "request": {k: v for k, v in kwargs.items()},
                "output_dir": str(out_dir),
                "explicit_file": args.file,
            }, ensure_ascii=False, indent=2))
        else:
            print(f"endpoint: {endpoint}", file=sys.stderr)
            print(f"output_dir: {out_dir}", file=sys.stderr)
            if args.file:
                print(f"explicit_file: {args.file}", file=sys.stderr)
            print("--- request body (would send) ---", file=sys.stderr)
            for k, v in kwargs.items():
                print(f"  {k}: {v!r}", file=sys.stderr)
        return 0

    if not args.json_mode:
        print(f"endpoint: {endpoint}", file=sys.stderr)
        print(
            f"model: gpt-image-2  size: {args._size}  quality: {args._quality}  n: {args.n}",
            file=sys.stderr,
        )
    if args.verbose:
        verbose_log_request("generate", kwargs)

    client = make_client()
    # Stream mode: ask the SDK to stream partial events.
    if args.stream:
        kwargs_stream = dict(kwargs)
        kwargs_stream["stream"] = True
        kwargs_stream["partial_images"] = max(0, min(3, args.partial_images))

        def _stream():
            return client.images.generate(**kwargs_stream)

        try:
            stream = call_with_retry(
                _stream, kwargs={}, max_retries=args.retries,
                verbose=args.verbose, label="generate(stream)",
            )
        except Exception as e:
            print(f"API error: {type(e).__name__}: {e}", file=sys.stderr)
            return 1

        # Collect the final image(s) from the stream.
        saved: list[Path] = []
        usage: dict = {"input_tokens": 0, "output_tokens": 0,
                       "input_tokens_details": {"image_tokens": 0, "text_tokens": 0}}
        for event in stream:
            etype = getattr(event, "type", None)
            if etype in ("image_edit.partial_image", "image_gen.partial_image",
                         "image_edit.completed", "image_gen.completed"):
                b64 = getattr(event, "b64_json", None) or getattr(event, "partial_image_b64", None)
                if not b64:
                    continue
                from lib.image_io import build_out_path, decode_b64_to_file
                dest = build_out_path(
                    out_dir=out_dir, prompt=args.prompt,
                    explicit=args.file, index=len(saved), total=args.n,
                    suffix=args._format,
                )
                decode_b64_to_file(b64, dest)
                saved.append(dest)
            elif etype and "usage" in etype:
                # Some proxies put usage in the event payload.
                usage = extract_usage(getattr(event, "usage", None))
        if not args.quiet:
            print_text_summary(saved, usage)
        if args.json_mode:
            print(json.dumps(to_json_result(saved, usage, prompt=args.prompt,
                                            endpoint=endpoint, n=args.n),
                             ensure_ascii=False, indent=2))
        return 0

    # Non-stream path. Try a transparent fallback if the proxy rejects a
    # field it doesn't know about (background / moderation / output_compression).
    response = None
    dropped: list[str] = []
    for attempt in range(len(PROXY_FALLBACK_FIELDS) + 1):
        try:
            response = call_with_retry(
                client.images.generate, kwargs=kwargs,
                max_retries=args.retries, verbose=args.verbose, label="generate",
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

    saved, usage = save_and_summarize(
        response,
        out_dir=out_dir,
        prompt=args.prompt,
        explicit_file=args.file,
        n=args.n,
        output_format=args._format,
        compression=args.compression,
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
