---
name: minimax-video-analyzer
description: >
  MiniMax video analysis skill for local mp4/mov/mkv/avi files, especially software operation recordings, 小程序/APP/Web 操作录屏, UX review, interaction analysis, 动效复刻, video analysis, 视频分析, MiniMax-M3, or 本地视频. This skill only analyzes existing video content and does not generate video.
license: MIT
metadata:
  version: "1.0"
  category: media-analysis
---

# MiniMax Video Analyzer

Use this skill to analyze an existing local video with MiniMax-M3 through the China Mainland MiniMax API. It is optimized for software operation recordings: small programs, apps, web pages, admin panels, product demos, interaction flows, UX review, and motion-effect replication.

This skill is intentionally narrow: upload a local video, ask MiniMax-M3 to analyze the visual content, and return the text result. Do not use it for video generation, audio transcription, image generation, TTS, or music generation.

## Capabilities

- Analyze local videos in `mp4`, `avi`, `mov`, or `mkv` format.
- Upload the video with `purpose=video_understanding`.
- Call `MiniMax-M3` through the OpenAI-compatible `/v1/chat/completions` endpoint.
- Reference uploaded videos with `mm_file://<file_id>`.
- Return the model's text analysis to stdout.
- Prefer a software-analysis report when the video is an operation recording: action timeline, UI state changes, interaction feedback, UX issues, and animation/motion breakdown.
- Fall back to general visual analysis when the video is not a software interface.

## Important Limits

- MiniMax-M3 video understanding does not support audio input. Treat the result as visual analysis only.
- Uploaded `video_understanding` files are retained by MiniMax for up to 7 days.
- The upload API supports videos up to 512 MB.
- Base64 inline video can work for small files, but this skill deliberately uses file upload by default because it is simpler and more stable.

## Environment

The script reads the API key from:

```bash
MINIMAX_API_KEY
```

For the user's China Mainland Token Plan, the default API base is:

```bash
https://api.minimaxi.com/v1
```

If the current shell cannot see the key but it exists in `~/.bashrc`, load it first:

```bash
source ~/.bashrc
```

## Usage

Run the bundled script from any working directory:

```bash
python ~/.config/opencode/skills/minimax-video-analyzer/scripts/analyze_video.py \
  ~/tmp/opencode/6-真假难辨.mp4 \
  "请基于画面客观分析这个软件操作录屏，重点说明用户操作流程、界面状态变化、交互体验和可复刻的动效细节。"
```

If no prompt is provided, the script uses a default Chinese prompt that prioritizes software operation analysis and falls back to general video analysis when the content is not a software interface.

## Default Analysis Focus

The default prompt asks MiniMax-M3 to stay objective and separate visual evidence into `[观察]`, `[推断]`, and `[不确定]`. For software videos, it focuses on:

- User operation timeline: clicks, swipes, inputs, navigation, and visible feedback.
- Page, component, and state changes: dialogs, toast messages, loading states, tabs, lists, buttons, selected/disabled states, and refresh behavior.
- UX review based on visible evidence: clarity, feedback timing, information hierarchy, hesitation, blocking, ambiguity, or possible mis-taps.
- Motion-effect replication: trigger, animated object, start/end state, changed properties, approximate duration, easing/pace, and engineering notes.
- UI structure and visual hierarchy: layout, components, color, text size, spacing, alignment, layering, and reusable component list.
- General visual fallback: camera, composition, movement, lighting, animation, transitions, effects, and editing rhythm when the video is not a software recording.

Useful options:

```bash
python ~/.config/opencode/skills/minimax-video-analyzer/scripts/analyze_video.py VIDEO_PATH [PROMPT] \
  --detail default \
  --timeout 120
```

## Workflow For Agents

1. Confirm the user is asking to analyze an existing local video.
2. Check that `MINIMAX_API_KEY` is available in the current environment.
3. If the user provides a custom question, preserve it. If not, rely on the default prompt for software operation, UX, and motion-effect analysis.
4. Run `scripts/analyze_video.py` with the video path and the user's analysis question.
5. Report the returned text. If the user asks about spoken dialogue or sound, clearly state that MiniMax-M3 video input does not include audio understanding in this workflow.

## Do Not Add

- Do not add ASR, audio extraction, or transcript merging unless the user explicitly asks for audio-aware analysis.
- Do not add caching or file deletion by default.
- Do not switch to base64 inline upload unless the user explicitly requests that path.
- Do not use the video generation skill for this task.
