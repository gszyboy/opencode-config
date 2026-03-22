# 子代理并行开发指南

## 概述

本文档介绍如何使用 OpenCode 的子代理功能，实现**前端、后端、文档**的并行开发。通过解耦任务、并行执行，显著提升开发效率。

### 核心思想

```
传统串行：前端(2h) → 后端(2h) → 文档(1h) = 5小时
并行执行：前端(2h) ← 并行 → 后端(2h) ← 并行 → 文档(1h) = 2小时
```

### 架构图

```
┌─────────────────────────────────────────────────────────────┐
│                     主会话（Task Master）                     │
│  • 分解任务                                                 │
│  • 创建 API 规范（解耦关键）                                 │
│  • 并行启动子代理                                           │
│  • 汇总结果、处理冲突                                        │
└─────────────────────────────────────────────────────────────┘
        │                   │                   │
        ▼                   ▼                   ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│ frontend-agent│  │ backend-agent │  │   docs-agent  │
│   subagent    │  │   subagent    │  │   subagent    │
│   type:build  │  │   type:build  │  │  type:general │
├───────────────┤  ├───────────────┤  ├───────────────┤
│ src/api/      │  │ backend/      │  │ docs/api.md   │
│ src/types/    │  │ routers/      │  │ openapi.yaml  │
│ src/mock/     │  │ models/       │  │               │
└───────────────┘  └───────────────┘  └───────────────┘
```

---

## 前置准备

### 1. 明确项目需求

在开始并行开发前，需要准备好：

| 文件 | 必需 | 说明 |
|------|------|------|
| SPEC.md | ✅ | 项目需求文档，包含功能列表、业务流程 |
| api-spec.md | ✅ | API 接口规范，**解耦的核心文件** |

### 2. 创建 API 规范（解耦关键）

API 规范是前后端和文档的**唯一真实来源**，所有子代理都基于此规范工作。

```yaml
# api-spec.md
openapi: 3.0.0
info:
  title: 项目API规范
  version: 1.0.0

paths:
  /users:
    get:
      summary: 获取用户列表
      tags: [用户管理]
      parameters:
        - name: page
          in: query
          schema:
            type: integer
            default: 1
        - name: page_size
          in: query
          schema:
            type: integer
            default: 20
      responses:
        '200':
          description: 成功
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UserListResponse'

  /users/{id}:
    get:
      summary: 获取用户详情
      tags: [用户管理]
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: integer
      responses:
        '200':
          description: 成功
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '404':
          $ref: '#/components/responses/NotFound'

  /users:
    post:
      summary: 创建用户
      tags: [用户管理]
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateUserRequest'
      responses:
        '201':
          description: 创建成功
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'

components:
  schemas:
    User:
      type: object
      properties:
        id:
          type: integer
          description: 用户ID
        name:
          type: string
          description: 用户名
        email:
          type: string
          format: email
        created_at:
          type: string
          format: date-time

    UserListResponse:
      type: object
      properties:
        total:
          type: integer
        page:
          type: integer
        users:
          type: array
          items:
            $ref: '#/components/schemas/User'

    CreateUserRequest:
      type: object
      required: [name, email]
      properties:
        name:
          type: string
        email:
          type: string
          format: email

  responses:
    NotFound:
      description: 资源不存在
      content:
        application/json:
          schema:
            type: object
            properties:
              code:
                type: integer
              message:
                type: string
```

### 3. API 规范检查清单

创建 API 规范后，确认以下内容：

- [ ] 每个接口有唯一的 HTTP 方法 + 路径组合
- [ ] 所有请求参数有名称、类型、位置（path/query/body）
- [ ] 所有响应有状态码和响应体 schema
- [ ] 复用 schema 使用 `$ref` 引用
- [ ] 字段有中文描述

---

## 子代理配置

### 1. 代理类型选择

| 代理 | subagent_type | 适用任务 |
|------|---------------|----------|
| explore | 探索/搜索 | 分析代码库、搜索模式 |
| build | 构建/开发 | 编写代码、实现功能 |
| general | 通用 | 文档、总结、分析 |

**本场景使用**：frontend-agent (build) + backend-agent (build) + docs-agent (general)

### 2. 代理职责划分

#### frontend-agent

```
职责：基于 API 规范开发前端代码

输入：
  - SPEC.md：项目需求
  - api-spec.md：API 接口规范
  - docs/frontend-rules.md：前端规范（可选）

输出：
  - src/types/api.ts：TypeScript 类型定义
  - src/api/*.ts：API 调用函数
  - src/mock/*.ts：Mock 数据
  - src/api/index.ts：API 统一导出

约束：
  - 使用 Vue 3 + TypeScript + Axios
  - 类型定义必须与 api-spec.yaml 中的 schema 一致
  - 接口路径必须与 api-spec.yaml 中的 paths 一致
```

#### backend-agent

```
职责：基于 API 规范开发后端代码

输入：
  - SPEC.md：项目需求
  - api-spec.md：API 接口规范
  - docs/backend-rules.md：后端规范（可选）

输出：
  - backend/routers/*.py：API 路由
  - backend/models/*.py：数据模型
  - backend/schemas/*.py：Pydantic 模型

约束：
  - 使用 FastAPI + SQLAlchemy
  - 路由路径必须与 api-spec.yaml 中的 paths 一致
  - 响应格式必须与 api-spec.yaml 中的 responses 一致
```

#### docs-agent

```
职责：基于 API 规范生成文档

输入：
  - api-spec.yaml：API 接口规范
  - docs/template.md：文档模板（可选）

输出：
  - docs/api.md：API 文档（Markdown）
  - docs/openapi.yaml：OpenAPI 规范文件
  - docs/examples.md：请求/响应示例

约束：
  - 文档内容必须与 api-spec.yaml 一致
  - 每个接口包含：说明、请求参数、响应示例、错误码
```

---

## 执行流程

### Step 1: 主会话准备工作

```python
# 主会话执行
# 1. 阅读并确认 SPEC.md
read("SPEC.md")

# 2. 创建或更新 api-spec.yaml
write("api-spec.yaml", api_spec_content)

# 3. 确认 API 规范完整性
# （对照检查清单验证）
```

### Step 2: 并行启动子代理

```python
# 主会话使用 Task 工具并行启动 3 个子代理

# === 子代理 1：前端开发 ===
task_frontend = Task(
    description="前端开发",
    prompt="""
    # 项目信息
    项目目录：/path/to/your/project
    
    # 参考文档
    - SPEC.md：项目需求（已阅读）
    - api-spec.yaml：API 接口规范（已阅读）
    - frontend-rules.md：前端规范（参考）
    
    # 你的任务
    1. 阅读 api-spec.yaml 中的所有接口定义
    2. 生成 TypeScript 类型定义到 src/types/api.ts
    3. 生成 API 调用函数到 src/api/*.ts
    4. 创建 Mock 数据到 src/mock/*.ts
    
    # 具体要求
    - 技术栈：Vue 3 + TypeScript + Axios
    - 接口路径：必须与 api-spec.yaml 完全一致
    - 响应类型：必须与 api-spec.yaml 中的 schema 一致
    - Mock 数据：包含正常响应和错误响应示例
    
    # 输出格式
    每个文件开头标注：
    // 来源：api-spec.yaml#/paths/xxx
    """,
    subagent_type="build"
)

# === 子代理 2：后端开发 ===
task_backend = Task(
    description="后端开发",
    prompt="""
    # 项目信息
    项目目录：/path/to/your/project
    
    # 参考文档
    - SPEC.md：项目需求（已阅读）
    - api-spec.yaml：API 接口规范（已阅读）
    - backend-rules.md：后端规范（参考）
    
    # 你的任务
    1. 阅读 api-spec.yaml 中的所有接口定义
    2. 实现 FastAPI 路由到 backend/routers/*.py
    3. 创建 Pydantic 模型到 backend/schemas/*.py
    4. 创建数据库模型到 backend/models/*.py
    
    # 具体要求
    - 技术栈：FastAPI + SQLAlchemy + Pydantic
    - 路由路径：必须与 api-spec.yaml 完全一致
    - 响应格式：必须与 api-spec.yaml 中的 responses 一致
    - 每个路由标注对应的规范路径
    
    # 输出格式
    每个文件开头标注：
    # 来源：api-spec.yaml#/paths/xxx
    """,
    subagent_type="build"
)

# === 子代理 3：文档编写 ===
task_docs = Task(
    description="API文档编写",
    prompt="""
    # 项目信息
    项目目录：/path/to/your/project
    
    # 参考文档
    - api-spec.yaml：API 接口规范（已阅读）
    
    # 你的任务
    1. 将 api-spec.yaml 转换为完整的 API 文档
    2. 生成 docs/api.md（Markdown 格式）
    3. 复制 api-spec.yaml 到 docs/openapi.yaml
    
    # 文档内容要求
    每个接口包含：
    - 接口说明（summary + description）
    - 请求方法、路径、参数
    - 请求示例（JSON）
    - 响应示例（JSON）
    - 错误码说明
    
    # 输出格式
    - docs/api.md：人类可读文档
    - docs/openapi.yaml：OpenAPI 规范（直接复制）
    """,
    subagent_type="general"
)

# 一次性发送 3 个任务，OpenCode 自动并行执行
[task_frontend, task_backend, task_docs]
```

### Step 3: 等待并汇总结果

子代理执行完成后，主会话接收结果：

```python
# 结果汇总
results = {
    "frontend": {
        "files": ["src/types/api.ts", "src/api/user.ts", ...],
        "summary": "生成了 5 个文件，包含 10 个接口定义"
    },
    "backend": {
        "files": ["backend/routers/user.py", "backend/schemas/user.py", ...],
        "summary": "实现了 5 个路由，包含完整的 CRUD"
    },
    "docs": {
        "files": ["docs/api.md", "docs/openapi.yaml"],
        "summary": "生成了完整的 API 文档"
    }
}

# 主会话执行汇总任务：
# 1. 一致性检查
# 2. 冲突处理
# 3. 最终合并
```

---

## 一致性检查

### 检查清单

| 检查项 | 前端 | 后端 | 检查方法 |
|--------|------|------|----------|
| 接口路径 | /users/{id} | /users/{id} | 完全一致 |
| HTTP 方法 | GET | GET | 完全一致 |
| 路径参数 | id: integer | id: int | 类型一致 |
| 查询参数 | page, page_size | page, page_size | 名称一致 |
| 响应 schema | User | User | 字段一致 |

### 冲突处理策略

| 冲突类型 | 处理方式 | 优先级 |
|----------|----------|--------|
| 接口路径不一致 | 以 api-spec.yaml 为准 | P0 |
| 字段类型冲突 | 协商统一类型 | P1 |
| 命名规范差异 | 遵循项目规范 | P2 |
| 功能实现遗漏 | 分配给对应代理补全 | P3 |

### 主会话汇总操作

```python
# 主会话执行
# 1. 读取前后端生成的代码
# 2. 对比接口定义是否一致
# 3. 如有冲突，以 api-spec.yaml 为准修正
# 4. 合并到项目目录
# 5. 提交代码

git add .
git commit -m "feat: 实现用户管理模块（前后端并行开发）"
```

---

## 完整示例

### 示例项目：用户管理系统

#### 1. 创建项目结构

```
/project
├── SPEC.md                    # 项目需求
├── api-spec.yaml              # API 规范（核心）
├── frontend/                  # 前端子目录
│   └── src/
│       ├── types/
│       ├── api/
│       └── mock/
└── backend/                   # 后端子目录
    └── app/
        ├── routers/
        ├── models/
        └── schemas/
```

#### 2. 主会话执行命令

```
用户：我想用并行开发方式实现用户管理模块

主会话：
1. 确认项目目录和需求
2. 创建 api-spec.yaml
3. 并行启动 3 个子代理
4. 汇总结果

# 实际执行：
/parallel-dev --module=user --spec=api-spec.yaml
```

#### 3. 子代理输出示例

**frontend-agent 输出**：
```
✅ 完成！生成文件：
├── src/types/api.ts          # User, UserListResponse 类型
├── src/api/user.ts          # getUsers(), getUser(id), createUser()
└── src/mock/user.ts         # Mock 数据

📊 统计：
- 接口数：5 个
- 类型定义：3 个
- Mock 数据：10 条
```

**backend-agent 输出**：
```
✅ 完成！生成文件：
├── app/routers/user.py       # 5 个路由
├── app/schemas/user.py       # Pydantic 模型
└── app/models/user.py        # SQLAlchemy 模型

📊 统计：
- 路由数：5 个
- 模型数：3 个
- 符合规范：✓
```

**docs-agent 输出**：
```
✅ 完成！生成文件：
├── docs/api.md               # 完整 API 文档
└── docs/openapi.yaml         # OpenAPI 规范

📊 统计：
- 接口文档：5 个
- 示例代码：10 个
```

---

## 最佳实践

### 1. API 规范先行

```
❌ 不要：
  - 先写代码，后补文档
  - 前后端口头约定接口
  - 接口变更不同步

✅ 要：
  - 先创建 api-spec.yaml
  - 所有变更通过规范文件同步
  - 定期检查规范与实现的一致性
```

### 2. 任务解耦

```
❌ 不要：
  - 前端依赖后端正在开发的接口
  - 文档依赖尚未确定的响应格式

✅ 要：
  - 接口规范确定后，前后端独立开发
  - Mock 数据模拟未实现的接口
  - 文档基于规范，而非实际代码
```

### 3. 频繁同步

```
建议：
- 每完成一个接口，前后端同步一次
- 发现不一致，立即以规范为准调整
- 避免大量代码写完后才发现冲突
```

### 4. 命名规范统一

```
前后端约定：
- API 路径：kebab-case（如 /user-profiles）
- 字段命名：camelCase（如 userName）
- 枚举值：UPPER_SNAKE_CASE（如 STATUS_ACTIVE）

在 api-spec.yaml 中明确标注：
paths:
  /user-profiles:
    get:
      parameters:
        - name: status
          description: 状态，枚举值：STATUS_PENDING | STATUS_ACTIVE | STATUS_INACTIVE
```

---

## 注意事项

### 1. 子代理限制

| 限制 | 说明 |
|------|------|
| 独立上下文 | 子代理之间不能直接通信 |
| 依赖处理 | 需要主会话中转 |
| 任务粒度 | 单个子代理任务不宜过大 |
| 冲突可能 | 独立工作可能产生微小差异 |

### 2. 适用场景

| 场景 | 推荐度 | 说明 |
|------|--------|------|
| 新项目启动 | ⭐⭐⭐⭐⭐ | 完美适用，并行效率最高 |
| 模块开发 | ⭐⭐⭐⭐ | 接口明确时可并行 |
| Bug 修复 | ⭐⭐ | 通常需要串行定位 |
| 重构 | ⭐⭐ | 依赖关系复杂 |

### 3. 常见问题

**Q：前后端接口不一致怎么办？**
A：以 api-spec.yaml 为准，让不一致的一方修改

**Q：子代理执行失败怎么办？**
A：主会话收到失败通知，重新分析问题，可能需要串行处理

**Q：可以启动更多子代理吗？**
A：可以，但建议不超过 5 个，避免主会话汇总困难

---

## 附录：命令模板

### 快速启动并行开发

```bash
# 在项目目录下执行
cd /path/to/project

# 启动并行开发流程
/parallel-dev
```

### 自定义子代理数量

```python
# 2个子代理：前端 + 后端
[task_frontend, task_backend]

# 4个子代理：前端 + 后端 + 文档 + 测试
[task_frontend, task_backend, task_docs, task_test]
```

### 增量并行开发

```python
# 仅开发特定模块的 API
task_frontend = Task(
    prompt="仅实现 /users 模块的前端代码",
    ...
)
task_backend = Task(
    prompt="仅实现 /users 模块的后端路由",
    ...
)
[task_frontend, task_backend]
```

---

*文档版本：1.0*
*更新日期：2026-03-22*
*参考：OpenCode Task 工具文档*
