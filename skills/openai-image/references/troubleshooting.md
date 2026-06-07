# 故障排查

> 实际出图过程中遇到的常见问题及处理建议。加载规则:LLM 看到 exit 1 / 5xx /
> `ok: false` 时主动 `view` 本文件。

## 1. 代理后端不可用(521 / 长时间 timeout / 空响应)

**识别**:同一域名 HTML 主页能访问,但 `/v1/images/generations` 持续 5xx。
**本质**:Cloudflare ↔ one-api ↔ 上游链路某段断了,任何 client 都会同样失败。
**Agent 对策**:看到持续 5xx → 告知用户代理暂时不可用,请换代理或稍后重试。
**不要反复重试或改 prompt**——都是浪费时间。
**skill 内部行为**:408/409/429/5xx 自动重试 3 次(jitter 退避),所以 stderr 出现 N 次
`[generate] attempt N failed` 后才是真 fail。

## 2. 冷启动慢

`gpt-image-2` 端点首次调用 15~60 秒(model lazy-load)属正常,不是错误。
调用方建议 `subprocess.run(timeout=300)`,本 skill 内部不主动设短 timeout。

## 3. b64 缺失 / url fallback

少数代理(如 gpt-agent.cc)违反 OpenAI 规范,只返 `url` 不返 `b64_json`。
本 skill **自动检测并下载 url 写盘**(见 `lib/image_io.py:extract_url_items` +
`download_url_to_b64`)。代理未计费时 `usage` 字段全 0 也属正常。

## 4. 字段被代理拒(自动降级)

`background` / `moderation` / `output_compression` / `output_format` 这 4 个字段
某些代理不接受。skill 自动去掉重试一次,在 stderr 输出
`note: proxy rejected field 'xxx'; retrying without it.`。

> **注意**:`size` **不在自动降级列表**(因为解析后是具体尺寸或字符串 `"auto"`,
> 代理拒绝时无法判断该去掉还是该替换成 1024x1024)。如果遇到 `size` 被拒,
> 改用 `--size 1024x1024` 字面量重试。

## 5. `--json` 输出 `ok: false` 但 exit 0

API 调用成功,但响应里既没 b64 也没 url(代理兼容性问题)。
Agent 应:不重试,提示用户**该代理不支持 gpt-image-2**,换代理。

## 6. `User-Agent` / `x-stainless-*` 被代理拒

`lib/client.py` 默认设置了反指纹 headers(伪装成非 OpenAI SDK 客户端,绕过某些代理
对 `OpenAI/Python*` UA 的封锁)。如被拒,可手动编辑 `lib/client.py:92-101` 调整。
**A/B 测试后再改**,没有通用最优解。

## 7. 鉴权错误(401 / 403)

- **401 Unauthorized**:API key 未设置或无效 → 检查 `GPT_AGENT_KEY` 是否导出
- **403 Forbidden**:API key 有效但权限不够 / 余额不足 → 看 stderr 响应体,通常含具体原因
- **403 + proxy 误判 fingerprint**:见上一节,某些代理有反 bot 检测

## 8. 参数超限错误(400 / 422)

| 触发 | 修法 |
|---|---|
| `prompt` 超过 32 000 字符 | 截短 |
| `size` 不合规(不是 16 倍数 / 长宽比越界 / 总像素超 829 万) | 用合法别名或字面量,详见 `cli-reference.md` §4 |
| `n` 超过 10 | 减少到 1-10 |
| `--compression` 超过 100 | 0-100 范围 |
| `gpt-image-2` 不支持的参数(目前确认:`input_fidelity`、未来可能扩展) | 移除该参数 |
