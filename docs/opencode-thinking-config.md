# opencode / OMO 中的 MiniMax 思考模式配置指南

> 调研时间: 2026-06-07
> 适用版本: opencode ≥ v1.x、oh-my-openagent ≥ v4.x、MiniMax M2.x / M3

本文档整理了三个相关问题的调研结论:
1. opencode 内置 minimax provider 走的是哪个 API 协议
2. 如何禁用 MiniMax-M3 的思考(thinking)模式
3. oh-my-openagent 配置中 `reasoningEffort`、`variant`、`thinking` 三个参数的含义与关系

---

## 1. opencode 内置 minimax 走的是 **Anthropic 协议**

### 数据来源

opencode 的内置 provider 元数据从 `https://models.dev/api.json` 加载(由 SST 官方维护,与 opencode 同一团队)。

### 4 个 minimax 相关内置 provider

| Provider ID | npm | baseURL | 说明 |
|---|---|---|---|
| `minimax` | `@ai-sdk/anthropic` | `https://api.minimax.io/anthropic/v1` | 国际版 |
| `minimax-cn` | `@ai-sdk/anthropic` | `https://api.minimaxi.com/anthropic/v1` | 大陆版 |
| `minimax-cn-coding-plan` | `@ai-sdk/anthropic` | `https://api.minimaxi.com/anthropic/v1` | 大陆版编码套餐 |
| `minimax-coding-plan` | `@ai-sdk/anthropic` | `https://api.minimax.io/anthropic/v1` | 国际版编码套餐 |

**4 个全部走 Anthropic 协议**,`/anthropic/v1` 路径是 Anthropic Messages API 的标准前缀。

### 关键源码位置

- `packages/llm/src/providers/anthropic.ts` — opencode 内置的 anthropic provider 实现
- `packages/llm/src/providers/openai-compatible-profile.ts` — OpenAI 兼容 provider profiles(无 minimax)
- `packages/llm/src/providers/index.ts` — 内置 provider 列表(无 minimax,数据从 models.dev 动态注入)

### MiniMax 官方协议支持

MiniMax 同时支持 OpenAI 和 Anthropic 两种协议(详见 `platform.minimaxi.com/docs/api-reference/api-overview`):

| 协议 | 大陆版端点 | 国际版端点 | 官方推荐 |
|---|---|---|---|
| OpenAI Chat Completions | `https://api.minimaxi.com/v1` | `https://api.minimax.io/v1` | — |
| **Anthropic Messages** | `https://api.minimaxi.com/anthropic` | `https://api.minimax.io/anthropic` | ✅ **推荐** |
| MiniMax 原生 | `https://api.minimaxi.com/v1/text/chatcompletion_v2` | `https://api.minimax.io/v1/text/chatcompletion_v2` | — |

opencode 统一选了 Anthropic 协议(跟官方推荐一致)。

---

## 2. MiniMax 思考(thinking)控制 API

### 各模型支持矩阵

| 模型 | thinking 默认 | 可关闭? | API 参数 |
|---|---|---|---|
| **MiniMax-M3** | ✅ 开启 | ✅ 可关闭 | `thinking: {"type": "disabled"}` |
| MiniMax-M2.7 | ✅ 开启 | ❌ 不可关闭 | — |
| MiniMax-M2.7-highspeed | ✅ 开启 | ❌ 不可关闭 | — |
| MiniMax-M2.5 | ✅ 开启 | ❌ 不可关闭 | — |
| MiniMax-M2.5-highspeed | ✅ 开启 | ❌ 不可关闭 | — |
| MiniMax-M2.1 | ✅ 开启 | ❌ 不可关闭 | — |
| MiniMax-M2 | ✅ 开启 | ❌ 不可关闭 | — |

**结论**:只有 **M3** 支持关闭 thinking。M2.x 系列 thinking 永远开启,即使传 `disabled` 也会被忽略(MiniMax 官方限制)。

### MiniMax M3 thinking 参数格式

**Anthropic 协议调用**(opencode 当前走的方式):

```json
{
  "thinking": {
    "type": "disabled"  // 或 "enabled" / "adaptive"
  }
}
```

- 省略 `thinking` → 默认开启 thinking
- `{"type": "adaptive"}` → 等同于开启
- `{"type": "disabled"}` → 关闭 thinking,直接给最终答案

来源:`platform.minimaxi.com/docs/api-reference/text-anthropic-api`

---

## 3. opencode 配置文件结构

### 配置文件位置

| 位置 | 路径 | 作用范围 |
|---|---|---|
| **全局** | `~/.config/opencode/opencode.json` 或 `opencode.jsonc` | 当前用户所有项目 |
| **项目级** | `<项目根>/opencode.json` 或 `opencode.jsonc` | 只在该项目生效 |

项目级 > 全局。建议用 `.jsonc` 后缀(支持注释)。

### opencode config.json schema 关键约束

来自 `https://opencode.ai/config.json` schema:

- `provider.models.X.options` → `type: "object"`(**完全开放**,允许任意字段,包括 `thinking`)
- `provider.models.X.variants.Y` → **只允许一个字段** `disabled: boolean`(这就是为什么 Issue #31180 用户在 `variants` 下放 `thinking` 不工作)

**因此 `thinking` 参数必须放在 `options` 下,不能放在 `variants` 下。**

### 禁用 M3 thinking 的标准配置

**最小化**写法,放在全局 `opencode.jsonc`:

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "minimax-cn": {                         // 或 minimax-cn-coding-plan / minimax
      "models": {
        "MiniMax-M3": {
          "options": {
            "thinking": {
              "type": "disabled"             // 关闭 thinking
            }
          }
        }
      }
    }
  }
}
```

**agent 级覆盖**(只在某个 agent 下关):

```jsonc
{
  "agent": {
    "build": {
      "model": "minimax-cn/MiniMax-M3",
      "options": {
        "thinking": { "type": "disabled" }
      }
    }
  }
}
```

agent 级 `options` 覆盖全局(官方文档原话:"The agent config overrides any global options here")。

### ⚠️ 已知问题:Issue #31180

[Issue #31180](https://github.com/anomalyco/opencode/issues/31180)(2026-06-07 提交):用户实测在 opencode + minimax 组合下,通过 `variants` 路径设置 `thinking` **不生效**。但通过 `options` 路径(本文档推荐的方式)目前未发现失败案例。

如果按本文档配置后 M3 仍然输出 thinking 块,说明 opencode 当前对 minimax 的 thinking 透传还没修好。可选 workaround:
1. 临时把 M3 替换为其他不依赖 thinking 的模型
2. 关注 Issue #31180 进展

---

## 4. oh-my-openagent 配置中的三个推理参数

OMO 的 agent 配置中**同时存在两种风格的推理控制**:`reasoningEffort`(OpenAI 风格)、`thinking`(Anthropic 风格),加一个预设开关 `variant`。

### 4.1 `reasoningEffort` — OpenAI / GPT-5 风格

```jsonc
"reasoningEffort": "medium"
```

可选值(来自 OMO 官方 schema):

| 值 | 含义 |
|---|---|
| `"none"` | 不推理(强制无思考) |
| `"minimal"` | 最小推理 |
| `"low"` | 低强度 |
| `"medium"` | 中等 |
| `"high"` | 高强度 |
| `"xhigh"` | 超高(部分模型支持) |
| `"max"` | 最大 |

**作用对象**:GPT-5 系列及其他支持 `reasoning_effort` 的 OpenAI 系模型。
**生效路径**:OMO 把这个值映射到 OpenAI 的 `reasoning_effort` 参数。

### 4.2 `variant` — opencode 预设变体

```jsonc
"variant": "high"
```

**含义**:选择该 model 的某个预设变体(就是 opencode variants)。opencode 内置变体:

| Provider | 可用 variant |
|---|---|
| Anthropic | `high`(默认)、`max` |
| OpenAI | `none`、`minimal`、`low`、`medium`、`high`、`xhigh` |
| Google | `low`、`high` |

**好处**:不用手动写 `thinking.budgetTokens` 或 `reasoningEffort`,一键切到预设。
**底层**:variant 展开后就是 `thinking: { type: "enabled", budgetTokens: X }` 或 `reasoningEffort: "X"` 的组合。

### 4.3 `thinking` — Anthropic Extended Thinking 风格

```jsonc
"thinking": {
  "type": "enabled",
  "budgetTokens": 32000
}
```

| 字段 | 必填 | 取值 | 作用 |
|---|---|---|---|
| `type` | ✅ 必填 | `"enabled"` / `"disabled"` | 开关扩展思考 |
| `budgetTokens` | 否 | 数字(默认根据模型) | thinking 块允许的最大 token |

**作用对象**:Anthropic 协议系列(Claude、MiniMax-M3 等所有走 `@ai-sdk/anthropic` 的模型)。
**底层**:映射到 Anthropic Extended Thinking 的 `thinking: { type, budget_tokens }` 参数。

### 三者关系总结

| 你想做的事 | 用哪个 |
|---|---|
| 切 GPT-5 的推理强度 | `reasoningEffort` |
| 切 Claude / MiniMax-M3 的 extended thinking | `thinking` |
| 用 opencode 预定义的组合(`max` 思考、`xhigh` 推理等) | `variant` |

**`variant` 是快捷方式**,等同于预先打包好的 `reasoningEffort`/`thinking` 组合。
三个字段**通常只用一个**(同时存在会冲突,实际生效的以哪个为准未明确)。

---

## 5. 三个参数在 OMO 配置中的层级

OMO agent config 中,三个参数可以放在**四个层级**(均经 schema 验证):

```jsonc
{
  "$schema": "https://raw.githubusercontent.com/code-yeongyu/oh-my-openagent/dev/assets/oh-my-opencode.schema.json",
  "agents": {
    "sisyphus": {                                    // ① agent 级 — 整个 agent 生效
      "model": "github-copilot/gpt-5.5",
      "variant": "max",                               // ← 这里
      "reasoningEffort": "high",                      // ← 或者这里
      "thinking": { "type": "enabled", "budgetTokens": 32000 },  // ← 或者这里

      "fallback_models": [                            // ② fallback 级 — 仅 fallback 切换时生效
        {
          "model": "anthropic/claude-opus-4-7",
          "variant": "max"                            // ← 这里
        },
        {
          "model": "minimax-cn/MiniMax-M3",
          "thinking": { "type": "disabled" }          // ← 或这里关掉 thinking
        }
      ],

      "ultrawork": {                                  // ③ ultrawork 模式专用(OMO 核心 feature)
        "model": "anthropic/claude-opus-4-7",
        "variant": "max"                              // ← 这里
      },

      "compaction": {                                 // ④ 上下文压缩时专用
        "model": "anthropic/claude-haiku-4-5",
        "variant": "max"                              // ← 这里
      }
    }
  }
}
```

**优先级**:`ultrawork` / `compaction` > `fallback_models` 中匹配的项 > 顶层 agent 配置。

### OMO 配置文件位置

| 位置 | 路径 |
|---|---|
| 全局 | `~/.config/opencode/oh-my-openagent.json` 或 `oh-my-openagent.jsonc` |
| 项目级 | `<项目根>/.opencode/oh-my-openagent.jsonc` |

**注意**:旧版本文件名是 `oh-my-opencode.json[c]`,新版本是 `oh-my-openagent.json[c]`,两者都识别。

---

## 6. 实操:本机 5 处 MiniMax-M3 配置修改

当前 `~/.config/opencode/oh-my-openagent.jsonc` 中,**5 处**用到了 MiniMax-M3:

| # | 路径 | 现有 thinking 相关配置 | 改法 |
|---|---|---|---|
| 1 | `agents.atlas` (L71-78) | `variant: "high"` | 改为 `thinking: { "type": "disabled" }` |
| 2 | `agents.sisyphus-junior` (L79-86) | `variant: "high"` | 同上 |
| 3 | `categories.visual-engineering` (L96-103) | `variant: "high"` | 同上 |
| 4 | `categories.deep` (L112-118) | **无** | 新增 `thinking: { "type": "disabled" }` |
| 5 | `categories.unspecified-high` (L140-147) | `variant: "high"` | 同上 |

### 完整 diff

**位置 1:`agents.atlas`**
```diff
 "atlas": {
   "model": "minimax-cn-coding-plan/MiniMax-M3",
   "fallback_models": [
     "minimax-cn-coding-plan/MiniMax-M2.7",
     "opencode-go/glm-5.1"
   ],
-  "variant": "high"
+  "thinking": { "type": "disabled" }
 }
```

**位置 2:`agents.sisyphus-junior`**
```diff
 "sisyphus-junior": {
   "model": "minimax-cn-coding-plan/MiniMax-M3",
   "fallback_models": [
     "opencode-go/qwen3.6-plus",
     "opencode-go/glm-5.1"
   ],
-  "variant": "high"
+  "thinking": { "type": "disabled" }
 }
```

**位置 3:`categories.visual-engineering`**
```diff
 "visual-engineering": {
   "model": "minimax-cn-coding-plan/MiniMax-M3",
   "fallback_models": [
     "xiaomi-token-plan-cn/mimo-v2.5-pro"
   ],
-  "variant": "high"
+  "thinking": { "type": "disabled" }
 }
```

**位置 4:`categories.deep`**
```diff
 "deep": {
   "model": "minimax-cn-coding-plan/MiniMax-M3",
   "fallback_models": [
     "deepseek/deepseek-v4-pro",
     "opencode-go/glm-5.1"
-  ]
+  ],
+  "thinking": { "type": "disabled" }
 }
```

**位置 5:`categories.unspecified-high`**
```diff
 "unspecified-high": {
   "model": "minimax-cn-coding-plan/MiniMax-M3",
   "fallback_models": [
     "xiaomi-token-plan-cn/mimo-v2.5-pro",
     "deepseek/deepseek-v4-pro"
   ],
-  "variant": "high"
+  "thinking": { "type": "disabled" }
 }
```

### ⚠️ fallback 链中的 M2.7 无法关闭 thinking

5 处的 `fallback_models` 中频繁出现 `MiniMax-M2.7`,但 M2.7 的 thinking **无法关闭**(MiniMax 官方硬性限制),只能换模型。如果希望主模型 fallback 后也不思考,M2.7 不是一个好的备选,需要找其他不依赖 thinking 的模型替换。

---

## 7. 验证方法

### 7.1 配置 schema 校验

```bash
bunx oh-my-openagent doctor
```

通过即 schema 合法。

### 7.2 确认 opencode 配置已加载

```bash
opencode debug config
```

搜索 `minimax-cn` 段,看 `MiniMax-M3.options.thinking.type` 是否为 `"disabled"`。

### 7.3 实际效果验证

在 TUI 中跑 atlas / sisyphus-junior / 任一 category 任务,看响应里**有没有 `thinking:` 开头的思维链块**——没有就说明关掉了。

---

## 8. 常见陷阱

| 陷阱 | 说明 |
|---|---|
| `thinking` 写在 `variants` 下 | ❌ opencode schema 不允许(`variants.*` 只接受 `disabled` 字段),实测不生效(Issue #31180) |
| `thinking` 写在 `options` 下 | ✅ opencode schema 允许,推荐 |
| M2.x 配 `thinking: disabled` | ❌ MiniMax 官方会忽略,thinking 仍然开启 |
| `reasoningEffort` 给 Anthropic 模型 | ❌ 该字段是 OpenAI 风格,Anthropic 不识别 |
| `thinking` 给 OpenAI 模型 | ❌ OpenAI 不识别 `thinking` 对象,该用 `reasoningEffort` |
| `variant` 和 `thinking` 同时写 | ⚠️ 行为未明确定义,只写一个 |

---

## 9. 参考资料

### opencode

- 官方文档 `/docs/models` — https://opencode.ai/docs/models/#configure-models
- 官方文档 `/docs/config` — https://opencode.ai/docs/config/
- Config schema — https://opencode.ai/config.json
- 仓库 — https://github.com/anomalyco/opencode
- Issue #31180 — https://github.com/anomalyco/opencode/issues/31180

### MiniMax 官方文档

- API 总览(大陆) — https://platform.minimaxi.com/docs/api-reference/api-overview
- Anthropic SDK 文档(大陆) — https://platform.minimaxi.com/docs/api-reference/text-anthropic-api
- API 总览(国际) — https://platform.minimax.io/docs/api-reference/api-overview
- Anthropic SDK 文档(国际) — https://platform.minimax.io/docs/api-reference/text-anthropic-api

### oh-my-openagent

- 仓库 — https://github.com/code-yeongyu/oh-my-openagent
- README — https://raw.githubusercontent.com/code-yeongyu/oh-my-openagent/dev/README.md
- Config schema — https://raw.githubusercontent.com/code-yeongyu/oh-my-openagent/dev/assets/oh-my-opencode.schema.json
- 模型元数据(由 SST 维护,opencode 通用) — https://models.dev/api.json
