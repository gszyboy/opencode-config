---
name: openai-image
license: MIT
description: |
  图像生成 / 改图 / 合成 skill,基于 OpenAI gpt-image-2,任意 OpenAI
  兼容代理。当用户想"gpt生图、AI 出图、改背景、换风格、融合几张图、
  做产品图/海报/UI mockup/角色立绘"或提到 gpt-image-2 时使用。
  同样适用英文 generate / restyle。
---

# openai-image

通过 Bash 调 `scripts/generate.py` 出图、`scripts/edit.py` 改图。
走 OpenAI Images API(POST /v1/images/generations + /v1/images/edits),
代理域名带 "claude" 仍可能是 OpenAI 兼容端点(**与 Anthropic 无关**)。

## 4 个工作流

```bash
# 1. 文生图
python3 scripts/generate.py -p "A photorealistic cafe at golden hour" -f gpt_image_out/cafe.png

# 2. 单参考图编辑 / 换背景 / 换风格
python3 scripts/edit.py -p "Change only the background to snow. Keep the subject, camera angle, lighting exactly the same." -i in.png -f gpt_image_out/winter.png

# 3. 多参考图融合 (1~16 张)
python3 scripts/edit.py -p "Place the dog from image 2 next to the woman in image 1." -i woman.png -i dog.png -f gpt_image_out/combined.png

# 4. Agent 模式: --json 输出, --dry-run 验证 payload
python3 scripts/generate.py -p "..." -f gpt_image_out/x.png --json
python3 scripts/generate.py -p "..." --dry-run --json
```

> `--dry-run` 不调 API,会校验输入文件存在 + 扩展名合法。

## 输出路径

`-f <path>` 显式指定输出(可以是文件或目录);**不传 `-f` 时**,产物落到 `<cwd>/gpt_image_out/`(`cwd` = OpenCode session 当前工作目录;`DEFAULT_OUT_DIRNAME` 见 `scripts/lib/image_io.py`)。目录不存在自动 `mkdir`。

```bash
# 显式指定文件
-f gpt_image_out/cafe.png

# 显式指定目录(目录内自动起时间戳文件名)
-f gpt_image_out/

# 改默认目录(优先于 --out-dir 但一般用 --out-dir)
--out-dir /path/to/my/output
```

文件命名:`YYYY-MM-DD-HH-MM-SS-<slug>.<ext>`,`--format jpeg|webp --compression N` 时 Pillow 重编码。

## 关键约束

| 项 | 约束 |
|---|---|
| model | `gpt-image-2`(OpenAI 官方 2026-04-21 发布,见 `https://platform.openai.com/docs/models/gpt-image-2`) |
| size | 两边 16 倍数,长边 ≤ 3840,长宽比 1:3~3:1,总像素 65.5 万~829 万;>2560 实验性。**注意:OpenAI API 不严格校验 16 倍数**——传非 16 倍数(如 `1080x1920`)API 接受但**静默降级**到最近的合规尺寸(如 1024x1536),用户拿到的不是请求的尺寸。skill 客户端 `params.py:resolve_size` 主动拦截,exit 2,早 fail-fast |
| quality | `low` / `medium` / `high` / `auto` |
| format | png(默认)/ jpeg / webp |
| reference | 1~16 张 png/jpg/webp,单张 ≤ 50MB |
| mask | **必须 .png**,alpha: 不透明=保留,透明=重画 |
| prompt | 最长 32 000 字符 |
| retry | 408/409/429/5xx 退避 3 次(`--retries` 可调) |
| 字段降级 | 代理拒 `background` / `moderation` / `output_compression` / `output_format` 时自动去掉重试 |
| n | **强制 1**(业务决策:省钱 + UI 单张够用) |

> `--background`(`transparent`/`opaque`/`auto`)和 `--moderation`(`low`/`auto`)
> 是 OpenAI Images API 标准参数;`--background` 仅 `generate.py` 支持,
> `edit.py` 不接(Images Edits API 本身不支持)。

## UI 出图尺寸速查

以下尺寸都满足关键约束的 16 倍数规则。来源:`https://platform.openai.com/docs/guides/image-generation`。

### PC 桌面软件

| 场景 | `--size` |
|---|---|
| 应用图标 | `1024x1024` (`square`) |
| 窗口截图(16:10) | `1536x1024` (`landscape`) |
| 全屏截图(16:9) | `2048x1152` (`2k-wide`) |
| 4K Hero | `3072x1728` |

### 移动 App

| 场景 | `--size` |
|---|---|
| iPhone 启动屏(15 Pro) | `1152x2560` |
| iPhone SE | `768x1280` |
| Android 启动屏 | `1088x1920` |
| iPad Pro 11 | `1664x2384` |
| App Store 截图 | `1280x2560` |

### Web

| 场景 | `--size` |
|---|---|
| Hero 全宽(2:1) | `2048x1024` |
| 博客封面(3:2) | `1536x1024` (`landscape`) |
| OG Image(社交分享,~2:1) | `1216x640` |
| 长截图整页(1:3 临界) | `1024x3072` |

### 微信小程序

| 场景 | `--size` |
|---|---|
| 启动屏(9:16) | `1088x1920` |
| 分享卡片(4:3) | `512x384` |
| 商城 banner(5:2) | `800x320` |
| 商品主图(1:1) | `1024x1024` (`square`) |

## 环境配置

```bash
pip install 'openai>=1.68' 'Pillow>=10'
```

两个 env 必须都设(API key + Base URL):

| 用途 | env 变量 |
|---|---|
| API key | `GPT_AGENT_KEY` |
| Base URL | `GPT_AGENT_URL` |

Base URL 末尾 `/v1` 会自动补齐。实际访问的 endpoint:
- `generate.py` → `{BASE_URL}/images/generations`
- `edit.py` → `{BASE_URL}/images/edits`

> `OPENAI_API_KEY` / `OPENAI_BASE_URL` **不读取**——本 skill 只用 `GPT_AGENT_*`。

## 引用(按需加载)

| 场景 | 加载 |
|---|---|
| 完整 CLI 参数 / 退出码 / JSON schema / 测试 | `references/cli-reference.md` |
| 故障排查 | `references/troubleshooting.md` |
