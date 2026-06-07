# CLI 参数 / 退出码 / JSON Schema 参考

> 给 LLM agent 用的完整技术参考。`SKILL.md` 已给出 5 个工作流示例,
> 本文档详尽到每一参数、每一退出码、每一 JSON 字段。
> 加载规则:LLM 需要精确信息(如某个 CLI flag、JSON 字段含义)时主动 `view` 本文件。

## 1. `generate.py` 参数

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|---|---|---|
| `-p, --prompt` | string | ✅ | — | 文本描述,最长 32 000 字符 |
| `-f, --file` | path | ❌ | (走 `--out-dir` 或默认) | 显式输出路径;可以是文件或目录(目录内自动起时间戳文件名) |
| `--out-dir` | path | ❌ | `./gpt_image_out/`(`cwd` 下) | 输出目录;`-f` 优先级更高 |
| `-n` | int | ❌ | 1 | **强制 1**(`choices=[1]`,用户传其他值会被 argparse 拒绝)。OpenAI gpt-image-2 官方支持 n>1,本 skill 因**省钱 + UI 场景单张够用**限制为 1 |
| `--size` | string\|WxH | ❌ | `1024x1024` | 尺寸别名或字面量 WxH |
| `--quality` | string | ❌ | `high` | `low`/`medium`/`high`/`auto` 或别名(`draft`/`preview`/`normal`/`standard`/`final`/`print`) |
| `--format` / `--output_format` | string | ❌ | `png` | `png`/`jpeg`/`webp`(也接受 `jpg`) |
| `--compression` | int 0-100 | ❌ | (不重编码) | 仅 jpeg/webp 生效;`--format jpeg --compression 80` 用 Pillow 重编码 |
| `--background` | string | ❌ | `auto` | `transparent` / `opaque` / `auto`(OpenAI Images API 标准字段) |
| `--moderation` | string | ❌ | `auto` | `low` / `auto`(OpenAI Images API 标准字段) |
| `--json` | flag | ❌ | false | 单行 JSON 输出到 stdout(适合 agent 解析) |
| `--dry-run` | flag | ❌ | false | 打印完整 request body 并退出,不调 API |
| `-v, --verbose` | flag | ❌ | false | 打印 request body + 每次重试详情到 stderr |
| `--stream` | flag | ❌ | false | 启用流式 partial images(**实验性**) |
| `--partial-images` | int 0-3 | ❌ | 2 | `--stream` 模式下的部分图数量 |
| `--retries` | int | ❌ | 3 | 408/409/429/5xx 最大重试次数 |
| `--quiet` | flag | ❌ | false | 抑制 stdout 的 `saved:` / `usage:` 行 |

## 2. `edit.py` 参数

| 参数 | 类型 | 必填 | 默认 | 说明 |
|---|---|---|---|---|
| `-p, --prompt` | string | ✅ | — | 编辑指令,最长 32 000 字符 |
| `-i, --image` | path(可重复) | ✅ | — | 参考图,**至少 1 张,最多 16 张**。例:`-i a.png -i b.png -i c.png` |
| `-m, --mask` | path(.png) | ❌ | — | alpha mask,不透明=保留,透明=重画。**必须是 .png** |
| `-f, --file` | path | ❌ | (走 `--out-dir` 或默认) | 显式输出路径 |
| `--out-dir` | path | ❌ | `./gpt_image_out/` | 输出目录 |
| `-n` | int | ❌ | 1 | **强制 1**(`choices=[1]`)。OpenAI gpt-image-2 官方支持 n>1,本 skill 因**省钱 + UI 场景单张够用**限制为 1 |
| `--size` | string\|WxH | ❌ | `auto` | 尺寸(默认 `auto` 让模型自选) |
| `--quality` | string | ❌ | `high` | 同 generate |
| `--format` | string | ❌ | `png` | 输出格式 |
| `--json` | flag | ❌ | false | JSON 输出 |
| `--dry-run` | flag | ❌ | false | 打印 payload(包含文件路径) |
| `-v, --verbose` | flag | ❌ | false | 详细日志 |
| `--retries` | int | ❌ | 3 | 重试次数 |
| `--quiet` | flag | ❌ | false | 抑制 saved/usage 行 |

**注意**:`edit.py` **不接** `--background` 和 `--moderation`,因为 OpenAI
Images Edits API 本身不支持这两个字段(它们是 generations-only)。

## 3. 共享 / 隐含参数

| 行为 | 由什么控制 |
|---|---|
| API key 读取 | `GPT_AGENT_KEY`(见 SKILL.md "环境配置") |
| Base URL 读取 | `GPT_AGENT_URL` |
| 网络超时 | 内部默认 300 秒 |
| 旧版 `OPENAI_API_KEY` | **不读取**(本 skill 显式传 `api_key=`) |

## 4. 尺寸别名(`--size` 可用值)

| 别名 | 解析为 | 备注 |
|---|---|---|
| `square` / `1k` | `1024x1024` | |
| `portrait` / `1k-tall` / `tall` | `1024x1536` | |
| `landscape` / `1k-wide` / `wide` | `1536x1024` | |
| `2k` | `2048x2048` | |
| `2k-wide` | `2048x1152` | |
| `2k-tall` | `1152x2048` | |
| `4k` | `3840x2160` | **实验性** |
| `4k-tall` | `2160x3840` | **实验性** |
| `auto` | `auto` | **仅 `edit.py` 默认值** |
| 字面量 `WxH` | 原样 | 必须两边都是 16 的倍数,长边 ≤ 3840,长宽比 1:3~3:1,总像素 65.5 万~829 万 |

## 5. 字段降级表

**`lib/params.py:PROXY_FALLBACK_FIELDS`** —— 代理拒这些字段时,skill 自动去掉重试一次:

```python
PROXY_FALLBACK_FIELDS = (
    "background",
    "moderation",
    "output_compression",
    "output_format",
)
```

**不在降级列表的字段**:
- `size` —— 解析后是具体尺寸或 `"auto"` 字符串,代理拒绝时**无法**自动降级。遇到 `size` 报错,改用字面量 `--size 1024x1024` 重试
- `quality`、`model`、`prompt` —— 核心字段,不会降级

## 6. 退出码与触发条件

| 退出码 | 含义 | 典型触发 |
|---|---|---|
| `0` | 成功 | API 调用成功 + 至少一张图写盘 |
| `1` | API / 业务错误 | 401/403/404/422/5xx(完整 body echo 到 stderr);`--json` 时 `ok: false` |
| `2` | 参数 / 预处理错误 | 缺 API key、文件不存在、扩展名不合法、`--n` 越界、`--compression` 越界、size 不合法 |

**Agent 处理建议**:
- exit 0 但 `--json` 输出 `ok: false` → API 调通但响应没图(代理兼容性问题),不重试,提示用户换代理
- exit 1 → 看 stderr 的 proxy 响应体,定位是鉴权/限流/字段不支持
- exit 2 → 用户输入错,不重试,直接修正参数

## 7. JSON output schema (`--json`)

stdout 一行 JSON,适合 agent 解析:

```json
{
  "ok": true,
  "endpoint": "https://www.claudeapi.win/v1",
  "model": "gpt-image-2",
  "prompt": "...",
  "n_requested": 1,
  "n_returned": 1,
  "files": [{"path": "/abs/path/to/file.png", "bytes": 1234567}],
  "usage": {
    "input_tokens": 1234,
    "output_tokens": 0,
    "input_tokens_details": {"image_tokens": 0, "text_tokens": 1234}
  }
}
```

| 字段 | 含义 |
|---|---|
| `ok` | `true` = 至少一张图成功写盘;`false` = API 调通但响应无图(代理兼容性问题) |
| `endpoint` | 实际使用的 base URL(从 env 读到的) |
| `model` | 固定 `gpt-image-2` |
| `n_requested` | 用户请求的图数 |
| `n_returned` | 实际写盘的图数;`n_requested > n_returned` 表示代理少返了 |
| `files` | 写盘的图列表,含绝对路径 + 字节数 |
| `usage` | token 计费;代理未计费时全 0 |

## 8. 常用参数组合示例

```bash
# 高质量 + JPEG 压缩(电商主图)
python3 scripts/generate.py -p "..." -f out.jpg --quality high --format jpeg --compression 85

# 透明背景(图标)
python3 scripts/generate.py -p "..." -f icon.png --background transparent --format png

# 一次出 4 张挑一张
python3 scripts/generate.py -p "..." -f gpt_image_out/ --n 4

# 单图换背景,verbose 看请求体
python3 scripts/edit.py -p "..." -i in.png -f out.png -v

# Mask 修补 + dry-run 验证 payload
python3 scripts/edit.py -p "..." -i photo.png -m mask.png -f out.png --dry-run
```

## 9. 开发与测试

```bash
# 单元测试(不调 API)
cd ~/.config/opencode/skills/openai-image
python3 -m unittest tests.test_params -v
python3 -m unittest tests.test_resolve_out_dir -v

# Dry-run 验证 payload(不调 API)
python3 scripts/generate.py -p "test" --dry-run --json
python3 scripts/edit.py -p "test" -i in.png --dry-run --json
```
