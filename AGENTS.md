# 全局开发规范

## 语言
- 保持对话为中文

## 核心原则
1. 简单优先，不提前抽象
2. 每个改动必须有明确目的
3. 先让它跑起来，再优化
4. AI 加速开发，但不替代决策

## Change Budget（强制，所有项目通用）
- 修改文件数：≤ 3
- 修改行数：≤ 80（不含格式化）
- 不引入新依赖（除非明确要求）
- 不修改任务范围之外的文件

## 禁止事项
- ❌ 不创建 service/repository 层（除非有 3+ 重复代码）
- ❌ 不添加"为未来扩展"的代码
- ❌ 不重构未涉及的文件
- ❌ 不创建抽象基类或接口（除非有必要）
- ❌ 单次任务不追求完美
- ❌ 不过度工程（YAGNI 原则）

## 安全规范
- ❌ 禁止在代码中硬编码密钥、密码、token
- ❌ 禁止提交 .env 文件到 Git
- 使用环境变量或 {env:VAR_NAME} 语法

### 目录安全
**危险目录禁止操作**：以下目录不适合执行代码操作，发现后必须立即警告用户并拒绝创建/修改任何文件：
- `~` 用户根目录
- `/` 根目录
- `/home`、`/home/<user>` 个人目录
- `/tmp` 临时目录
- `/etc`、`/var`、`/usr`、`/boot`、`/sys`、`/proc`、`/dev` 系统目录

发现用户在危险目录时，必须：
1. 立即通过 TUI toast 或回复提醒用户
2. 拒绝创建、修改任何代码文件
3. 建议用户切换到正规项目目录

## Git 规范
- Commit 信息简洁明了
- 每次 commit 只做一件事
- 提交前检查敏感信息

## AI 开发节奏
1. 明确任务范围
2. 设置 Change Budget
3. 复杂任务先 Plan Mode 分析
4. 小步快跑，不追求一次到位
5. 完成后简单验证

## 模块化规范（按需加载）

需要具体规范时引用对应文件：

- 通用开发规范：@~/.config/opencode/docs/general-rules.md
- 后端规范：@~/.config/opencode/docs/backend-rules.md
- 前端规范：@~/.config/opencode/docs/frontend-rules.md
- TypeScript 规范：@~/.config/opencode/docs/typescript-rules.md
- 测试规范：@~/.config/opencode/test/testing-guide.md

## 已有项目规范

处理已有项目时引用：

- 已有项目规范：@~/.config/opencode/docs/existing-project-rules.md
- 项目评估命令：/assess-project
- 增量开发命令：/incremental-dev

### 已有项目核心规则

**50行平衡模式**：
- 改动 ≤ 50行
- 文件 ≤ 3个
- 不引入新依赖

**改动红线（绝对不改，除非明确授权）**：
1. 数据库结构/ORM模型
2. 认证鉴权逻辑
3. 支付财务代码
4. 核心业务算法

**介入级别**：
- L1 只读：刚接手、不确定风险
- L2 诊断：定位问题、分析原因
- L3 小改：改一个函数/一行配置（≤10行）
- L4 增量：修复bug、加小功能（≤50行）
- L5 重构：较大改动（分阶段授权）
