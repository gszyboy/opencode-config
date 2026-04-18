---
name: design-md
description: |
  DESIGN.md 设计风格参考技能。当用户请求使用某个知名网站的 设计风格时自动触发，如"用 Linear 的风格"、"做成 Stripe 那种 UI"、"按照 Vercel 的设计"等。
  技能会自动从 VoltAgent/awesome-design-md 仓库获取对应的 DESIGN.md 文档，读取其设计规范（颜色、字体、间距、组件样式），并在生成 UI 时严格遵循。
  触发场景：用户提到要用某个具体网站/产品的设计风格来构建界面时。
  ⚠️ 注意：awesome-design-md 仓库是活跃项目，持续新增更多品牌。本 skill 中的品牌列表可能不完整，使用前应检查仓库最新状态。
triggers:
  - "用.*的风格"
  - "做成.*那种"
  - "按照.*的设计"
  - "像.*一样的"
  - ".*风格"
  - ".*设计风格"
  - "设计参考"
---

# Design-MD Skill

当用户请求使用某个知名网站的 设计风格时，使用本技能获取对应 DESIGN.md 并严格遵循。

## ⚠️ 关于品牌列表

**awesome-design-md 仓库是持续更新的活跃项目**：
- 截至 2026年4月 已收录 68+ 个品牌设计
- 仓库仍在持续新增更多品牌（几乎每周都有更新）
- **本 skill 中的品牌列表可能不完整**

每次使用时，应先去仓库获取最新列表：
```
https://github.com/VoltAgent/awesome-design-md
```
或使用 librarian agent 查询最新可用的品牌。

## 工作流程

### Step 1: 确认品牌是否存在 + 获取 URL

**首先检查仓库最新状态**。推荐方式：

1. 直接尝试通用 URL 格式（品牌名通常对应该 URL 模式）：
   ```
   https://getdesign.md/<slug>/design-md
   ```

2. 如果不确定 slug，查询 GitHub 仓库的 README 获取完整列表：
   ```
   webfetch(url="https://raw.githubusercontent.com/VoltAgent/awesome-design-md/main/README.md", format="markdown")
   ```

3. 或使用 librarian agent：
   > "查询 VoltAgent/awesome-design-md 仓库最新有哪些品牌的 DESIGN.md 可用"

**常见 URL 映射**（仅供快速参考，以仓库实际为准）：

| 类别 | 代表品牌 | URL slug |
|------|----------|----------|
| AI 平台 | Claude, Minimax, Mistral, Ollama | `claude`, `minimax`, `mistral.ai`, `ollama` |
| 开发者工具 | Cursor, Vercel, Expo, Raycast | `cursor`, `vercel`, `expo`, `raycast` |
| 数据库 | Supabase, MongoDB, ClickHouse | `supabase`, `mongodb`, `clickhouse` |
| 设计工具 | Figma, Framer, Webflow | `figma`, `framer`, `webflow` |
| 金融科技 | Stripe, Coinbase, Revolut | `stripe`, `coinbase`, `revolut` |
| 汽车 | Tesla, BMW, Ferrari, Lamborghini | `tesla`, `bmw`, `ferrari`, `lamborghini` |

> 如果用户提到的网站不在已知列表中，**不要假设没有** — 直接去 getdesign.md 尝试通用格式，因为仓库在持续新增。

### Step 2: 获取 DESIGN.md 内容

**首选**：使用 `webfetch` 工具从 getdesign.md 获取内容：

```
webfetch(url="https://getdesign.md/<slug>/design-md", format="markdown")
```

**备选**：如果 getdesign.md 无法访问或内容为空，从 GitHub raw 获取：
```
webfetch(url="https://raw.githubusercontent.com/VoltAgent/awesome-design-md/main/design-md/<slug>/DESIGN.md", format="markdown")
```

> ⚠️ 注意：GitHub 仓库中部分品牌的 `design-md/<slug>/` 目录下可能只有 `README.md` 指针文件，实际内容托管在 getdesign.md 网站上。优先尝试 getdesign.md。

### Step 3: 解析设计规范

DESIGN.md 文件通常包含以下章节，严格按照其中规范执行：

1. **Visual Theme & Atmosphere** - 整体氛围和设计哲学
2. **Color Palette** - 语义化颜色名称 + hex 值，AI 生成时必须使用精确的 hex 颜色
3. **Typography** - 字体族、字号层级、字重
4. **Component Stylings** - 按钮、卡片、输入框等组件的具体样式
5. **Layout Principles** - 间距系统（通常是 4px/8px 倍数）、网格布局
6. **Depth & Elevation** - 阴影层级
7. **Do's and Don'ts** - 设计禁忌
8. **Responsive Behavior** - 响应式断点

### Step 4: 应用设计规范

读取 DESIGN.md 后，在生成任何 UI 代码时：

1. **严格使用精确的 hex 颜色值** - 不要随意替换或近似
2. **遵循指定的字体** - 如果没有自定义字体，使用系统字体栈
3. **遵循间距系统** - 使用 DESIGN.md 中定义的基础间距单位
4. **遵循组件样式** - 按钮圆角、阴影、边框等都严格按照文档
5. **遵循暗色/亮色主题** - 如果文档同时提供两种主题，询问用户偏好

## 输出格式

在应用设计规范时，在回复开头注明：

```
📐 设计参考: [品牌名]
- 主色调: [精确 hex 值]
- 字体: [字体栈]
- 基础间距: [Xpx]
- 组件风格: [描述]
```

## 注意事项

- 如果同时存在 `AGENTS.md`，将其与 DESIGN.md 结合使用
- AGENTS.md 定义"如何构建项目"，DESIGN.md 定义"项目应该长什么样"
- 如果用户没有指定品牌但说"现代感"、"简约风"等模糊描述，主动推荐合适的品牌
- DESIGN.md 是给 AI 看的设计规范，比 Figma 文件更适合 AI 理解和执行

## ⚠️ 仓库动态性声明

**awesome-design-md 是活跃维护的仓库**：
- 品牌数量持续增长（本 skill 撰写时约 68 个）
- 现有品牌的设计规范可能随时更新优化
- 新品牌每周都在增加

**最佳实践**：
1. 使用前先检查仓库最新状态：`https://github.com/VoltAgent/awesome-design-md`
2. 如果用户请求的品牌在 skill 中没有列出，**先去 getdesign.md 尝试**，不要直接说没有
3. 如果 getdesign.md 也找不到，再去 GitHub 仓库提 Issue 请求添加新品牌
