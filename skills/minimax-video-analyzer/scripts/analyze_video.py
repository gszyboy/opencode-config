#!/usr/bin/env python3
"""Analyze a local video with MiniMax-M3 using file upload + chat completions."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


DEFAULT_BASE_URL = "https://api.minimaxi.com/v1"
DEFAULT_MODEL = "MiniMax-M3"
DEFAULT_PROMPT = """你是一名严谨的软件产品与视频内容分析师。请优先把这段视频当作小程序、APP、Web 或软件操作录屏来分析；如果画面明显不是软件界面，再自动切换为通用视频分析。

【硬约束】
1. 只基于画面进行分析，不要假设音频、对白、旁白、音乐或音效。
2. 保持中肯客观，不做主观吐槽、夸赞或无证据的价值判断。
3. 每个判断尽量标注：[观察] 画面直接可见；[推断] 基于画面证据的合理推断；[不确定] 证据不足或画面不清。
4. 如果看不清、被遮挡、变化太快或证据不足，请直接说明，不要补全细节。

【输出结构】请用中文 Markdown 输出：
1. 视频类型与分析边界：说明这是软件操作录屏、产品演示、游戏界面、普通视频等，并说明只能基于画面判断。
2. 用户操作时间线：按 mm:ss 顺序还原点击、滑动、输入、页面跳转、状态反馈等关键操作。
3. 页面 / 组件 / 状态变化：列出可见页面、导航、按钮、列表、弹窗、Toast、Loading、选中态、禁用态、刷新等变化。
4. 交互体验分析：基于画面证据评价路径是否清晰、反馈是否及时、信息层级是否明确，指出卡顿、误触、歧义或遮挡。
5. 动效与转场复刻拆解：说明触发条件、动效对象、初始/结束状态、变化属性（位置、透明度、缩放、旋转、颜色、层级、模糊）、大致时长和节奏。
6. 视觉层级与 UI 结构：描述布局、组件关系、颜色、字号、间距、对齐、层级和可复刻组件清单。
7. 镜头 / 画面表现：如是录屏，说明是否固定画面；如有实拍或剪辑，再分析景别、构图、运镜、光影、动画、转场、特效和剪辑节奏。
8. 异常、可疑点与不确定信息：集中列出画面中不连贯、难判断、可能影响复刻或体验判断的细节。
9. 工程复刻建议：给出可能涉及的前端状态、组件、触发事件、动画参数方向和需要人工确认的信息；不要直接写代码，除非用户要求。
10. 客观总结：用 1-3 句话总结视频实际呈现的内容，不加入主观评论。"""
SUPPORTED_TYPES = {
    ".mp4": "video/mp4",
    ".avi": "video/x-msvideo",
    ".mov": "video/quicktime",
    ".mkv": "video/x-matroska",
}
MAX_UPLOAD_BYTES = 512 * 1024 * 1024


class MiniMaxError(RuntimeError):
    pass


def fail(message: str, code: int = 1) -> None:
    print(f"Error: {message}", file=sys.stderr)
    raise SystemExit(code)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyze a local video with MiniMax-M3 visual understanding."
    )
    parser.add_argument("video", help="Local video path: mp4, avi, mov, or mkv")
    parser.add_argument(
        "prompt",
        nargs="?",
        default=DEFAULT_PROMPT,
        help="Analysis prompt. Defaults to a Chinese visual-analysis prompt.",
    )
    parser.add_argument(
        "--base-url",
        default=os.getenv("MINIMAX_API_BASE", DEFAULT_BASE_URL),
        help=f"MiniMax API base URL. Default: {DEFAULT_BASE_URL}",
    )
    parser.add_argument(
        "--model",
        default=os.getenv("MINIMAX_VIDEO_MODEL", DEFAULT_MODEL),
        help=f"Model name. Default: {DEFAULT_MODEL}",
    )
    parser.add_argument(
        "--detail",
        choices=("low", "default", "high"),
        default="default",
        help="Video detail hint passed to video_url. Default: default",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=120,
        help="Timeout in seconds for each API request. Default: 120",
    )
    parser.add_argument(
        "--print-json",
        action="store_true",
        help="Print the raw chat completion JSON instead of extracted text.",
    )
    return parser.parse_args()


def validate_video(path_text: str) -> tuple[Path, str]:
    path = Path(path_text).expanduser().resolve()
    if not path.is_file():
        fail(f"video file does not exist: {path}")

    suffix = path.suffix.lower()
    if suffix not in SUPPORTED_TYPES:
        allowed = ", ".join(sorted(SUPPORTED_TYPES))
        fail(f"unsupported video format '{suffix}'. Allowed: {allowed}")

    size = path.stat().st_size
    if size > MAX_UPLOAD_BYTES:
        fail("video is larger than the MiniMax upload limit of 512 MB")

    return path, SUPPORTED_TYPES[suffix]


def curl_json(args: list[str], timeout: int) -> dict[str, Any]:
    if shutil.which("curl") is None:
        fail("curl is required but was not found in PATH")

    marker = "__MINIMAX_HTTP_STATUS__:"
    command = ["curl", "-sS", "-w", f"\n{marker}%{{http_code}}", *args]

    try:
        process = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise MiniMaxError(f"request timed out after {timeout}s") from exc

    if process.returncode != 0:
        detail = process.stderr.strip() or process.stdout.strip()
        raise MiniMaxError(f"curl failed with exit code {process.returncode}: {detail}")

    body, sep, status_text = process.stdout.rpartition(f"\n{marker}")
    if not sep:
        raise MiniMaxError("could not read HTTP status from curl output")

    try:
        status = int(status_text.strip())
    except ValueError as exc:
        raise MiniMaxError(f"invalid HTTP status: {status_text.strip()}") from exc

    try:
        data = json.loads(body)
    except json.JSONDecodeError as exc:
        snippet = body[:1000].replace("\n", " ")
        raise MiniMaxError(f"response is not valid JSON: {snippet}") from exc

    if status >= 400:
        snippet = json.dumps(data, ensure_ascii=False)[:1200]
        raise MiniMaxError(f"HTTP {status}: {snippet}")

    return data


def check_base_resp(data: dict[str, Any], action: str) -> None:
    base_resp = data.get("base_resp")
    if not isinstance(base_resp, dict):
        return

    status_code = base_resp.get("status_code")
    if status_code not in (0, "0", None):
        status_msg = base_resp.get("status_msg", "unknown error")
        raise MiniMaxError(f"{action} failed: {status_code} {status_msg}")


def upload_video(
    api_key: str, base_url: str, video_path: Path, mime_type: str, timeout: int
) -> str:
    upload_url = f"{base_url.rstrip('/')}/files/upload"
    print(f"Uploading video: {video_path}", file=sys.stderr)

    data = curl_json(
        [
            "-X",
            "POST",
            upload_url,
            "-H",
            f"Authorization: Bearer {api_key}",
            "-F",
            "purpose=video_understanding",
            "-F",
            f"file=@{video_path};type={mime_type}",
        ],
        timeout=timeout,
    )
    check_base_resp(data, "upload")

    file_info = data.get("file") if isinstance(data.get("file"), dict) else data
    file_id = file_info.get("file_id") or file_info.get("id")
    if not file_id:
        snippet = json.dumps(data, ensure_ascii=False)[:1200]
        raise MiniMaxError(f"upload response did not include file_id: {snippet}")

    print(f"Uploaded file_id: {file_id}", file=sys.stderr)
    return str(file_id)


def analyze_video(
    api_key: str,
    base_url: str,
    model: str,
    file_id: str,
    prompt: str,
    detail: str,
    timeout: int,
) -> dict[str, Any]:
    chat_url = f"{base_url.rstrip('/')}/chat/completions"
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "video_url",
                        "video_url": {
                            "url": f"mm_file://{file_id}",
                            "detail": detail,
                        },
                    },
                ],
            }
        ],
        "stream": False,
    }

    print("Analyzing video with MiniMax-M3...", file=sys.stderr)
    return curl_json(
        [
            "-X",
            "POST",
            chat_url,
            "-H",
            f"Authorization: Bearer {api_key}",
            "-H",
            "Content-Type: application/json",
            "--data",
            json.dumps(payload, ensure_ascii=False),
        ],
        timeout=timeout,
    )


def extract_text(data: dict[str, Any]) -> str:
    choices = data.get("choices")
    if not isinstance(choices, list) or not choices:
        snippet = json.dumps(data, ensure_ascii=False)[:1200]
        raise MiniMaxError(f"chat response did not include choices: {snippet}")

    message = choices[0].get("message") if isinstance(choices[0], dict) else None
    if not isinstance(message, dict):
        raise MiniMaxError("first choice did not include message")

    content = message.get("content")
    if isinstance(content, str):
        return strip_thinking(content)

    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict) and isinstance(item.get("text"), str):
                parts.append(item["text"])
        if parts:
            return strip_thinking("\n".join(parts))

    return json.dumps(content, ensure_ascii=False)


def strip_thinking(text: str) -> str:
    cleaned = re.sub(r"<think>.*?</think>\s*", "", text, flags=re.DOTALL)
    return cleaned.strip()


def main() -> None:
    args = parse_args()
    api_key = os.getenv("MINIMAX_API_KEY")
    if not api_key:
        fail("MINIMAX_API_KEY is not set. If it is in ~/.bashrc, run: source ~/.bashrc")

    video_path, mime_type = validate_video(args.video)

    try:
        file_id = upload_video(api_key, args.base_url, video_path, mime_type, args.timeout)
        response = analyze_video(
            api_key=api_key,
            base_url=args.base_url,
            model=args.model,
            file_id=file_id,
            prompt=args.prompt,
            detail=args.detail,
            timeout=args.timeout,
        )
        if args.print_json:
            print(json.dumps(response, ensure_ascii=False, indent=2))
            return
        print(extract_text(response))
    except MiniMaxError as exc:
        fail(str(exc))


if __name__ == "__main__":
    main()
