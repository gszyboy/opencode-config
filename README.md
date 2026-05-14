# OpenCode 配置

## 插件安装记录

### 2026-04-19

安装了 [opencode-dynamic-context-pruning](https://github.com/Opencode-DCP/opencode-dynamic-context-pruning) 插件，并进行了配置。

该插件用于动态上下文剪枝，优化大语言模型的上下文管理。

### 2026-04-23

更新 `oh-my-openagent.json` 中的 kimi 模型：`k2p5` → `k2p6`，并备份为 `oh-my-openagent.json.正常版`。

### 2026-05-14

模型配置调整：
- `opencode.json` 删除 `claude-opus-4-6` 模型
- `oh-my-openagent.json` 多处节点模型更新：
  - `multimodal-looker` 主模型 `mimo-v2.5` → `mimo-v2-omni`，第一回退 `mimo-v2-omni` → `gpt-agent/mimo-v2-omni`
  - `atlas` 节点新增回退模型 `xiaomi-token-plan-cn/mimo-v2.5-pro`
  - `sisyphus` 主模型 `k2p6` → `mimo-v2.5`
  - `visual-engineering` 主模型 `MiniMax-M2.7` → `mimo-v2.5`
  - `unspecified-high` 主模型 `MiniMax-M2.7` → `mimo-v2.5`
- `AGENTS.md` Change Budget 新增：新项目或者在开发中的新项目不受此约束

### 2026-05-06

`opencode.json` gpt-agent 节点模型更新：
- `mimo-v2-pro` → `mimo-v2.5-pro`（context 128K → 1M，output 32K → 131.1K）
- 新增 `mimo-v2.5` 多模态模型（text + image + audio + video，context 1M，output 131.1K）
- 3 个 `oh-my-openagent.json` 配置文件（主版本/正常版/DeepSeek版）`mimo-v2-omni` → `mimo-v2.5`
- `oh-my-openagent.json.应急版` `mimo-v2-omni` → `mimo-v2.5`
- 4 个配置文件 `multimodal-looker` 和 `artistry` 节点：第1回退 `mimo-v2-omni`，第2回退 `gemini-3.1-pro`
- 4 个配置文件 `gpt-agent/mimo-v2.5` → `xiaomi-token-plan-cn/mimo-v2.5`
- 4 个配置文件 `gpt-agent/mimo-v2-omni` → `xiaomi-token-plan-cn/mimo-v2-omni`
- 4 个配置文件 `sisyphus` 节点 `ultrawork` 主模型 → `xiaomi-token-plan-cn/mimo-v2.5-pro`，variant → `high`

新增 Skills：
- `ai-ui-generator` - AI UI 生成器
- `doc-to-ppt-pdf` - Markdown 转 PPT/PDF 提案
- `fastadmin-dev` - FastAdmin PHP 框架开发助手
- `mineadmin` - MineAdmin 全栈管理后台（Swoole/Hyperf）
- `pure-admin-router` - Pure Admin Router
- `python-vue-admin` - FastAPI + Vue3 全栈管理后台
- `.gitignore` 添加 `__pycache__/` 和 `*.pyc`

### 2026-05-02（本次）

新增模型配置并升级现有配置：
- `opencode.json` 新增 `gpt-5.5` 和 `claude-opus-4-7` 模型定义
- `opencode.json` 更新 `gpt-5.5`: context 1,050,000 / output 128,000
- `opencode.json` 更新 `claude-opus-4-7`: context 1,000,000 / output 128,000（原 200K/32K）
- 4 个 `oh-my-openagent.json` 配置文件（主版本/正常版/应急版/DeepSeek版）所有 `gpt-5.4` 替换为 `gpt-5.5`
- 删除 AGENTS.md 中混入的 VoiceInput 项目特定规范

### 2026-05-02（后续）

- 4 个 `oh-my-openagent.json` 配置文件所有 `MiniMax-M2.5-highspeed` 替换为 `minimax-cn-coding-plan/MiniMax-M2.7`
- `oh-my-openagent.json` 和 `oh-my-openagent.json.正常版` 的 `atlas` 节点：主模型更换为 `minimax-cn-coding-plan/MiniMax-M2.7`
- `oh-my-openagent.json` 和 `oh-my-openagent.json.正常版` 的 `sisyphus-junior` 节点：主模型更换为 `kimi-for-coding/k2p6`，第一回退更换为 `minimax-cn-coding-plan/MiniMax-M2.7`

### 2026-04-27

新增 DeepSeek 版配置文件 `oh-my-openagent.json.DeepSeek版`：
- 复制 `oh-my-openagent.json.正常版` 为基础
- 将 10 个节点的主模型从 `minimax-cn-coding-plan/MiniMax-M2.7` 切换为 `deepseek_custom/deepseek-v4-pro`
- 涉及的节点：hephaestus、librarian、metis、atlas、sisyphus-junior、sisyphus、visual-engineering、unspecified-low、unspecified-high、writing
- 删除 sisyphus 节点中的 ultrawork 配置
- 在 `switch-agent.sh` 中新增 `deepseek` 选项以快速切换到此版本

## 项目结构

- `AGENTS.md` - Agent 配置
- `docs/` - 开发规范文档
- `skills/` - 技能配置
- `plugins/` - 插件目录
- `commands/` - 命令配置

## 配置

- `opencode.json` - 主配置
- `oh-my-openagent.json` - Agent 行为配置
- `dcp.jsonc` - 动态上下文剪枝配置

---

# 文档变更记录

本文档汇总所有规范文档的变更历史。

---

## general-rules.md

| 日期 | 更新内容 |
|------|----------|
| 2026-03-22 | 添加 Git 提交规范和分支命名规范 |

---

## frontend-rules.md

| 日期 | 更新内容 |
|------|----------|
| 2026-03-22 | 添加 Vue 3 详细规范和 UniApp 规范 |
| 2026-04-19 | 添加 Vue 组件大小规范（200行目标/300行警戒线） |

---

## backend-rules.md

| 日期 | 更新内容 |
|------|----------|
| 2026-03-22 | 添加完整 FastAPI 项目结构规范 |

---

## typescript-rules.md

| 日期 | 更新内容 |
|------|----------|
| 2026-03-22 | 创建 TypeScript 规范 |

---

## security-guide.md

| 日期 | 更新内容 |
|------|----------|
| 2026-03-22 | 添加安全增强规范和 Plugins |

---

## OPENCODE-USER-GUIDE.md

| 日期 | 更新内容 |
|------|----------|
| 2026-03-22 | 创建完整使用指南 |
| 2026-03-22 | 添加已有项目AI协作规范（/assess-project、/incremental-dev） |
| 2026-03-22 | 更新技能列表，完善 MCP 配置说明 |
| 2026-03-22 | 精简 Skills，删除重复的 dev-progress/incremental-doc/plan-decomposer |
| 2026-03-22 | 更新用户指南：修正 Skills 列表、移除 `@` 前缀、修复重复命令 |

---

## AGENTS.md

| 日期 | 更新内容 |
|------|----------|
| 2026-04-21 | 合并 Karpathy 4 原则（Think Before Coding、Simplicity First、Surgical Changes、Goal-Driven Execution）|

---

## 汇总统计

| 文档 | 创建日期 | 最近更新 |
|------|----------|----------|
| general-rules.md | 2026-03-22 | 2026-03-22 |
| frontend-rules.md | 2026-03-22 | 2026-04-19 |
| backend-rules.md | 2026-03-22 | 2026-03-22 |
| typescript-rules.md | 2026-03-22 | 2026-03-22 |
| security-guide.md | 2026-03-22 | 2026-03-22 |
| OPENCODE-USER-GUIDE.md | 2026-03-22 | 2026-03-22 |
| existing-project-rules.md | - | - |
| parallel-development-guide.md | - | - |

**说明**：`-` 表示该文档无变更记录或从未更新。