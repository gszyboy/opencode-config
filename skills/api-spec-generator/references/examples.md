# API Spec 生成示例

本文件展示常见的 API Spec 生成场景。

## 示例 1：用户管理

### 输入

```
帮我生成用户管理的 API 规范
- 用户有：id, username, email, password, created_at, updated_at
- 需要：增删改查
```

### 输出结构

```yaml
paths:
  /users:
    get:      # 获取用户列表
    post:     # 创建用户
  
  /users/{id}:
    get:      # 获取用户详情
    put:      # 更新用户
    delete:   # 删除用户

components:
  schemas:
    User:
      properties:
        id, username, email, created_at, updated_at
    
    CreateUserRequest:
      properties:
        username, email, password
    
    UpdateUserRequest:
      properties:
        username, email
```

---

## 示例 2：博客系统

### 输入

```
帮我生成博客系统的 API 规范
- 文章：id, title, content, author, status, created_at, updated_at
- 需要：文章的增删改查
```

### 输出结构

```yaml
paths:
  /articles:
    get:      # 获取文章列表（支持分页、状态筛选）
    post:     # 创建文章
  
  /articles/{id}:
    get:      # 获取文章详情
    put:      # 更新文章
    delete:   # 删除文章

components:
  schemas:
    Article:
      # 包含所有字段
    
    CreateArticleRequest:
      # 创建时需要的字段
    
    ArticleListResponse:
      # 分页响应
```

---

## 示例 3：订单管理

### 输入

```
帮我生成订单系统的 API 规范
- 订单：id, user_id, total_amount, status, created_at
- 订单项：id, order_id, product_id, quantity, price
- 需要：订单的增删改查、订单项的增删查
```

### 输出结构

```yaml
paths:
  /orders:
    get:      # 获取订单列表
    post:     # 创建订单
  
  /orders/{id}:
    get, put, delete
  
  /orders/{id}/items:
    get:      # 获取订单的所有条目
    post:     # 添加订单条目
  
  /orders/{id}/items/{item_id}:
    delete:   # 删除订单条目

components:
  schemas:
    Order:
    OrderItem:
    CreateOrderRequest:
```

---

## 示例 4：待办事项（带筛选）

### 输入

```
帮我生成待办事项的 API 规范
- 待办：id, title, description, completed, priority, created_at
- completed：boolean，默认 false
- priority：integer，1-3，默认 1
- 需要：增删改查
- 需要支持按完成状态筛选
```

### 输出结构

```yaml
paths:
  /todos:
    get:
      # parameters 增加 completed 筛选参数
      parameters:
        - name: completed
          in: query
          schema:
            type: boolean
    post:
  
  /todos/{id}:
    get, put, delete

components:
  schemas:
    Todo:
      properties:
        id: integer
        title: string
        description: string (nullable)
        completed: boolean
        priority: integer (enum: 1,2,3)
        created_at: date-time
```

---

## 示例 5：评论系统（嵌套资源）

### 输入

```
帮我生成评论系统的 API 规范
- 评论：id, post_id, parent_id, content, author, created_at
- parent_id 用于支持回复功能（嵌套评论）
- 需要：评论的增删查
- 评论按 post_id 关联
```

### 输出结构

```yaml
paths:
  /posts/{post_id}/comments:
    get:      # 获取文章的所有评论
    post:     # 添加评论
  
  /comments/{id}:
    get:      # 获取评论详情
    delete:   # 删除评论

components:
  schemas:
    Comment:
      properties:
        id: integer
        post_id: integer
        parent_id: integer (nullable, 用于回复)
        content: string
        author: string
        created_at: date-time
    
    CreateCommentRequest:
      properties:
        parent_id: integer (nullable)
        content: string
```

---

## 常见模式

### 1. 分页列表

```yaml
/todos:
  get:
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
        content:
          application/json:
            schema:
              type: object
              properties:
                total: { type: integer }
                page: { type: integer }
                page_size: { type: integer }
                items: { type: array }
```

### 2. 状态筛选

```yaml
parameters:
  - name: status
    in: query
    schema:
      type: string
      enum: [pending, active, archived]
```

### 3. 搜索

```yaml
parameters:
  - name: q
    in: query
    schema:
      type: string
    description: 搜索关键词
```

### 4. 排序

```yaml
parameters:
  - name: sort
    in: query
    schema:
      type: string
      enum: [created_at, -created_at, updated_at, -updated_at]
    description: 排序字段，加 - 表示降序
```

### 5. 日期范围

```yaml
parameters:
  - name: start_date
    in: query
    schema:
      type: string
      format: date
  - name: end_date
    in: query
    schema:
      type: string
      format: date
```

---

## 输出示例（完整 YAML）

对于"用户管理"需求，生成的完整文件：

```yaml
openapi: 3.0.0
info:
  title: 用户管理 API
  description: 用户管理的增删改查接口
  version: 1.0.0

servers:
  - url: http://localhost:8000/api/v1
    description: 开发环境

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

    put:
      summary: 更新用户
      tags: [用户管理]
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: integer
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/UpdateUserRequest'
      responses:
        '200':
          description: 更新成功
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '404':
          $ref: '#/components/responses/NotFound'

    delete:
      summary: 删除用户
      tags: [用户管理]
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: integer
      responses:
        '204':
          description: 删除成功
        '404':
          $ref: '#/components/responses/NotFound'

components:
  schemas:
    User:
      type: object
      required:
        - id
        - username
        - email
        - created_at
      properties:
        id:
          type: integer
          description: 用户ID
        username:
          type: string
          description: 用户名
        email:
          type: string
          format: email
          description: 邮箱
        created_at:
          type: string
          format: date-time
          description: 创建时间
        updated_at:
          type: string
          format: date-time
          nullable: true
          description: 更新时间

    CreateUserRequest:
      type: object
      required:
        - username
        - email
      properties:
        username:
          type: string
          description: 用户名
        email:
          type: string
          format: email
          description: 邮箱
        password:
          type: string
          description: 密码

    UpdateUserRequest:
      type: object
      properties:
        username:
          type: string
          description: 用户名
        email:
          type: string
          format: email
          description: 邮箱

    UserListResponse:
      type: object
      properties:
        total:
          type: integer
        page:
          type: integer
        page_size:
          type: integer
        items:
          type: array
          items:
            $ref: '#/components/schemas/User'

    ErrorResponse:
      type: object
      properties:
        code:
          type: integer
        message:
          type: string

  responses:
    NotFound:
      description: 资源不存在
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ErrorResponse'
```
