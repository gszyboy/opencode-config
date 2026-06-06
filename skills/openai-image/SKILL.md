---
name: openai-image
license: MIT
description: |
  图像生成 / 改图 / 重绘 / 合成 skill,基于 OpenAI gpt-image-2,通过任意
  OpenAI 兼容代理调用。当用户想"gpt生图、用 AI 出图、改背景、换风格、融合几张图、
  局部重绘、做产品图 / 海报 / UI mockup / 角色立绘 / inpainting",以及提到
  gpt-image-2 / GPT Image 2 任意变体时,优先用本 skill。
  同样适用英文 query (generate / restyle / inpaint via gpt-image-2)。
triggers:
  - "(?i)gpt[- ]image[- ]?2"
  - "(?i)(生成|画|做).*图"
  - "(?i)(generate|make|draw|create).*image"
  - "(?i)(参考|根据|基于).*图.*(改|换|调|编辑)"
  - "(?i)inpaint|局部重绘|重绘|redraw"
---

# openai-image Skill

调用 `scripts/generate.py` 出图,`scripts/edit.py` 改图 / 局部重绘。
任意 OpenAI 兼容代理都支持,优先 `CLAUDEAPI_API_URL` + `CLAUDEAPI_API_KEY`,
回落 `OPENAI_*`。**仅走 Images API**(`/v1/images/generations` + `/v1/images/edits`),
不接 Responses API。

## 5 个工作流

```bash
# 1. 文生图
python3 scripts/generate.py -p "A photorealistic cafe at golden hour" -f gpt_image_out/cafe.png

# 2. 单参考图编辑 / 换背景 / 换风格
python3 scripts/edit.py -p "Change only the background to a snowy mountain. Keep the subject, camera angle, lighting direction exactly the same." -i in.png -f gpt_image_out/winter.png

# 3. 多参考图融合 (1~16 张)
python3 scripts/edit.py -p "Place the dog from image 2 next to the woman in image 1. Match lighting and composition. Do not change anything else." -i woman.png -i dog.png -f gpt_image_out/combined.png

# 4. Mask 局部重绘 (PNG alpha: 不透明=保留, 透明=重画)
python3 scripts/edit.py -p "replace sky with aurora" -i photo.png -m sky_mask.png -f gpt_image_out/aurora.png

# 5. Agent 自动化 (--json 输出结构化结果, --dry-run 调试 payload)
python3 scripts/generate.py -p "..." -f gpt_image_out/x.png --json
python3 scripts/generate.py -p "..." --dry-run --json
```

> `--dry-run` 不会调 API,但会在终端打印(或 `--json` 输出一份)将发往
> 代理的完整 payload。**它会校验输入文件存在 + 扩展名合法**(这是为了
> 早早 fail,而不是把错误传到代理),所以 `-i` `-m` 路径必须真实可读。

## 输出路径

agent 调用时,产物默认落到 `cwd` 下的 `gpt_image_out/` 子目录
(目录不存在会自动 `mkdir`,失败时 exit code 1)。换 OpenCode 项目时图自然
归到对应项目,不会污染 skill 本体。

| 优先级 | 来源 | 用法 |
|---|---|---|
| 1 | `-f <path>` | 这次调用显式指定文件(如 `-f gpt_image_out/cafe.png`)或目录(如 `-f gpt_image_out/`,目录内自动起时间戳文件名) |
| 2 | `--out-dir <dir>` | 这次调用显式指定目录,文件仍按时间戳命名 |
| 3 | `<cwd>/gpt_image_out/` | 默认 |

文件命名:`YYYY-MM-DD-HH-MM-SS-<slug>.<ext>`,`--format jpeg|webp --compression N` 时 Pillow 重编码。

## 关键约束

| 项 | 约束 |
|---|---|
| model | `gpt-image-2`(`input_fidelity` 2.0 不支持) |
| size | 两边 16 倍数,长边 ≤ 3840,长宽比 1:3~3:1,总像素 65.5 万~829 万;>2560 实验性 |
| quality | `low` 草稿 / `medium` 探索 / `high` 最终(密集文字必 high) |
| n | 1~10 |
| format | png(默认,文字锐利)/ jpeg / webp |
| reference | 1~16 张 png/jpg/webp,单张 ≤ 50MB |
| mask | 必须是 **.png** 文件,alpha 通道:不透明=保留,透明=重画 |
| prompt | 最长 32 000 字符 |
| retry | 408/409/429/5xx 退避 3 次(`--retries` 可调) |
| 字段降级 | 代理拒 `background` / `moderation` / `output_compression` / `output_format` 时自动去掉重试一次(*代码层支持,真实 4xx 场景未现场验证*) |

## Prompt 工艺

1. **结构化**:`[主体] [风格] [光线] [镜头] [材质] [环境] [氛围] [约束]`
2. **声明用途**:`"for a product poster" / "as a UI mockup"` 让模型自选精度
3. **文字加引号**:`"SUMMER DROP"` 严禁改写
4. **决定比例后写进 prompt**:`portrait 3:4 composition`
5. **一个 hero + supporting cast** 比堆元素好
6. **编辑时显式保留项**:`Keep the product shape, label layout, cap color, camera angle exactly the same`
7. **避坑**:不要 `8k masterpiece` 关键词堆砌,要自然语言

## 环境配置

- 依赖:`openai>=1.68` + `Pillow>=10`(`pip install openai Pillow`)
- API key: `CLAUDEAPI_API_KEY` → `GPT_AGENT_KEY`
- Base URL: `CLAUDEAPI_API_URL` → `GPT_AGENT_URL`
- **本 skill 只通过代理出图,不走 api.openai.com。两个 env 至少设一组。**

## 引用加载 (Progressive Loading)

| 场景 | 加载 |
|---|---|
| 商业产品图 prompt gallery(白底/场景/极简) | `references/use-cases/product-photography.md` |
| 改图 / 换背景 / 换风格 / 多图融合 | `references/use-cases/reference-edit.md` |
| 局部重绘 / mask 局部替换 / 修补 | `references/use-cases/inpainting-mask.md` |
| 默认 | 不用加载 |

## 退出码

- `0` 成功
- `1` API 错误(完整 body echo 到 stderr)
- `2` 参数错误 / 缺 API key / 文件不存在

## 失败模式与排查

**代理后端不可用**(521 / 长时间 timeout / 空响应)。
识别方法:同一个域名的 HTML 主页能访问,但 `/v1/images/generations` 或
`/v1/chat/completions` 持续 5xx。**这不是 prompt / skill 客户端问题**——
是 Cloudflare ↔ one-api ↔ 上游 OpenAI 链路某一段断了,任何 client
(curl / SDK / 浏览器)都会同样失败。
agent 应对:看到持续 5xx → **告知用户代理暂时不可用,请换代理或稍后重试**,
不要反复重试或改 prompt —— 都是浪费时间。

> 注:skill 内部已自动重试 3 次(5xx/408/409/429),jitter 退避,所以
> stderr 出现 N 次 `[generate] attempt N failed` 后才是真 fail。

**冷启动慢**。gpt-image-2 端点首次调用 15~60 秒(model lazy-load)属
正常,不是错误。建议调用方 `subprocess.run(timeout=300)`,本 skill 内部
不主动设短 timeout。

**b64 缺失 / url fallback**。少数代理(例如 gpt-agent.cc)违反 OpenAI
规范,只返 `url` 不返 `b64_json`。本 skill 自动检测并下载 url 写盘;
agent 看到 `usage` 字段全 0 也是正常的(代理未计费)。

## JSON output schema (`--json`)

```json
{
  "ok": true,
  "endpoint": "https://your-proxy.example.com/v1",
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

字段缺失(代理未返回 `usage`)时对应值为 0,不报错。
