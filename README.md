# OpenCode 配置

## 插件安装记录

### 2026-04-19

安装了 [opencode-dynamic-context-pruning](https://github.com/Opencode-DCP/opencode-dynamic-context-pruning) 插件，并进行了配置。

该插件用于动态上下文剪枝，优化大语言模型的上下文管理。

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