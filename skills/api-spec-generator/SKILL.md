---
name: api-spec-generator
description: 生成 OpenAPI 3.0 规范的 api-spec.yaml 文件。当用户需要创建 API 规范、设计前后端接口、定义数据模型时必须使用。触发场景包括：用户说"帮我生成 API 规范"、"创建 api-spec"、"设计接口"、"前后端分离开发"等。无论用户是否明确提到 api-spec.yaml 或 OpenAPI，都应在涉及 API 设计的场景中主动建议使用此技能。
---

# API Spec Generator

生成符合 OpenAPI 3.0 规范的 api-spec.yaml 文件，用于解耦前后端开发。

## 核心价值

```
api-spec.yaml = 前后端开发的"合同"
                    ↓
    前端和后端基于同一份规范独立开发
                    ↓
         最终对接时不再扯皮
```

## 工作流程

```
┌────────────────────────────────────────────────────┐
│  1. 收集需求                                        │
│     - 项目类型（用户管理/订单/博客/电商/...）          │
│     - 需要哪些接口（CRUD）                          │
│     - 数据模型有哪些字段                            │
└────────────────────────────────────────────────────┘
                         ↓
┌────────────────────────────────────────────────────┐
│  2. 生成规范                                        │
│     - 自动推断合理的 RESTful 路径                    │
│     - 生成完整的 schema 定义                        │
│     - 包含请求/响应示例                             │
└────────────────────────────────────────────────────┘
                         ↓
┌────────────────────────────────────────────────────┐
│  3. 校验完整性                                      │
│     - 路径是否符合规范                             │
│     - HTTP 方法是否正确                             │
│     - schema 是否完整                               │
└────────────────────────────────────────────────────┘
                         ↓
┌────────────────────────────────────────────────────┐
│  4. 输出文件                                        │
│     - api-spec.yaml                                │
│     - 保存到项目根目录                              │
└────────────────────────────────────────────────────┘
```

## 触发时机

| 用户说... | 是否触发 |
|-----------|----------|
| 帮我生成 API 规范 | ✅ |
| 创建 api-spec | ✅ |
| 设计接口 | ✅ |
| 前后端分离 | ✅ |
| 用户管理有哪些接口 | ✅ |
| 这个项目需要哪些 API | ✅ |

## 信息收集（按需）

### 最小信息（必需）

```
用户只需要告诉我：
- 项目/功能名称
- 数据模型（字段列表）
- 需要哪些操作（增删改查）

示例：
"帮我生成用户管理的 API 规范
 - 用户有：id, name, email
 - 需要：增删改查"
```

### 完整信息（可选）

如果你能获取到更多细节：

| 信息 | 用途 | 来源 |
|------|------|------|
| 项目类型 | 推断合理的接口设计 | 对话或现有代码 |
| 业务规则 | 添加验证规则 | 需求文档 |
| 认证方式 | 添加安全配置 | 项目规范 |
| 关系数据 | 添加关联 schema | 数据模型 |

## 输出格式

### 文件位置

```
项目根目录/
└── api-spec.yaml    # OpenAPI 3.0 规范文件
```

### 文件结构

```yaml
openapi: 3.0.0
info:
  title: [项目名称]
  description: [项目描述]
  version: 1.0.0

servers:
  - url: http://localhost:8000/api/v1
    description: 开发环境

paths:
  /[资源名]:
    get:
      summary: 获取列表
      tags: [[标签]]
      parameters:
        - name: page
          in: query
          schema:
            type: integer
      responses:
        '200':
          description: 成功
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/[Schema名]'

    post:
      summary: 创建
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/[RequestSchema]'
      responses:
        '201':
          description: 创建成功

  /[资源名]/{id}:
    get:
      summary: 获取详情
      parameters:
        - name: id
          in: path
          required: true
      responses:
        '200':
          description: 成功
        '404':
          $ref: '#/components/responses/NotFound'

    put:
      summary: 更新
      responses:
        '200':
          description: 成功
        '404':
          $ref: '#/components/responses/NotFound'

    delete:
      summary: 删除
      responses:
        '204':
          description: 删除成功
        '404':
          $ref: '#/components/responses/NotFound'

components:
  schemas:
    [Schema名]:
      type: object
      properties:
        id:
          type: integer
        ...
      required:
        - id

  responses:
    NotFound:
      description: 资源不存在
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ErrorResponse'

  schemas:
    ErrorResponse:
      type: object
      properties:
        code:
          type: integer
        message:
          type: string
```

## 命名规范

### 路径命名（kebab-case）

| 场景 | 路径 | 说明 |
|------|------|------|
| 资源复数 | /users | 列表、创建 |
| 资源单数 | /users/{id} | 详情、更新、删除 |
| 动作 | /users/{id}/activate | 特殊动作 |

### HTTP 方法

| 方法 | 用途 | 示例 |
|------|------|------|
| GET | 查询 | GET /users |
| POST | 创建 | POST /users |
| PUT | 全量更新 | PUT /users/{id} |
| PATCH | 部分更新 | PATCH /users/{id} |
| DELETE | 删除 | DELETE /users/{id} |

### Schema 命名（PascalCase）

| 用途 | 命名 | 示例 |
|------|------|------|
| 数据模型 | [资源名] | User, Todo, Order |
| 创建请求 | Create[资源名]Request | CreateUserRequest |
| 更新请求 | Update[资源名]Request | UpdateUserRequest |
| 列表响应 | [资源名]ListResponse | UserListResponse |
| 错误响应 | ErrorResponse | 全局通用 |

## 常见数据模型模板

### 用户管理

```yaml
User:
  type: object
  properties:
    id: { type: integer }
    username: { type: string }
    email: { type: string, format: email }
    password: { type: string }
    created_at: { type: string, format: date-time }
    updated_at: { type: string, format: date-time }
```

### 待办事项

```yaml
Todo:
  type: object
  properties:
    id: { type: integer }
    title: { type: string }
    description: { type: string, nullable: true }
    completed: { type: boolean, default: false }
    priority: { type: integer, enum: [1,2,3] }
    created_at: { type: string, format: date-time }
```

### 分页响应

```yaml
ListResponse:
  type: object
  properties:
    total: { type: integer }
    page: { type: integer }
    page_size: { type: integer }
    items: { type: array, items: { $ref: '#/components/schemas/实体名' } }
```

## 校验清单

生成规范后，检查以下内容：

- [ ] 每个接口有 summary（中文）
- [ ] 所有参数有 name、type、description
- [ ] 必填参数标记 required
- [ ] 路径参数标记 in: path + required: true
- [ ] 响应包含状态码（200、201、204、400、404）
- [ ] 错误响应使用 $ref 复用
- [ ] schema 字段类型正确（string/integer/boolean/array）
- [ ] 日期格式使用 date-time
- [ ] 邮箱格式使用 format: email

## 交互示例

### 示例 1：简洁需求

```
用户：帮我生成用户管理的 API 规范

AI：
正在生成 api-spec.yaml...
✅ 完成！创建了以下接口：
- GET /users - 获取用户列表
- POST /users - 创建用户
- GET /users/{id} - 获取用户详情
- PUT /users/{id} - 更新用户
- DELETE /users/{id} - 删除用户

文件已保存到：api-spec.yaml
```

### 示例 2：详细需求

```
用户：帮我生成博客系统的 API 规范
- 文章有：id, title, content, author, created_at, updated_at
- 评论有：id, article_id, content, author, created_at
- 需要：文章的增删改查、评论的增删查

AI：
正在生成 api-spec.yaml...
✅ 完成！

包含 schema：
- Article、CreateArticleRequest、UpdateArticleRequest、ArticleListResponse
- Comment、CreateCommentRequest、CommentListResponse

包含路径：
- /articles（GET、POST）
- /articles/{id}（GET、PUT、DELETE）
- /articles/{id}/comments（GET、POST）
- /comments/{id}（DELETE）

文件已保存到：api-spec.yaml
```

## 输出文件

最终输出一个 `api-spec.yaml` 文件，包含：

1. **完整的 OpenAPI 3.0 结构**
2. **所有接口定义**（paths）
3. **所有数据模型**（components/schemas）
4. **通用响应定义**（components/responses）
5. **中文注释**（summary、description）

## 后续建议

生成规范后，主动建议用户：

```
规范已生成！接下来可以：

1. 【并行开发】并行开发前后端
   → 告诉我"并行开发"，我会启动多个子代理

2. 【单独开发】先开发后端
   → 基于规范实现 FastAPI 路由

3. 【单独开发】先开发前端
   → 基于规范生成 TypeScript 类型 + Mock 数据
```

## 参考文件

- `references/openapi-template.yaml` - OpenAPI 3.0 完整模板
- `references/examples.md` - 常见场景示例

## 注意事项

1. **不要过度设计**：只生成用户需要的接口
2. **保持简洁**：不需要 authentication、security 等高级特性（除非用户要求）
3. **中文优先**：summary、description 使用中文
4. **立即可用**：生成的规范可以直接被 FastAPI、Swagger 等工具使用
