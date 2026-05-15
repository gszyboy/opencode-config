# 后端开发规范

## 技术栈选择

根据项目技术栈选择对应规范。

---

## Python + FastAPI 规范

### 推荐项目结构

```
backend/
├── main.py              # 应用入口
├── database.py          # 数据库连接
├── config.py            # 配置管理
├── models/              # ORM 模型（数据库表结构）
│   ├── __init__.py
│   └── user.py
├── schemas/             # Pydantic 模型（请求/响应）
│   ├── __init__.py
│   └── user.py
├── routers/             # 路由（只处理 HTTP）
│   ├── __init__.py
│   └── user.py
└── crud/                # 数据库操作（可选）
    ├── __init__.py
    └── user.py
```

### 各层职责

| 层级 | 职责 | 禁止 |
|------|------|------|
| **models/** | 定义数据库表结构 | 不写业务逻辑 |
| **schemas/** | 请求验证、响应格式 | 不直接操作数据库 |
| **routers/** | 接收请求、返回响应 | 不写复杂业务逻辑 |
| **crud/** | 数据库增删改查 | 不写业务规则 |

### 什么时候加 crud/ 目录
- 单个实体的查询超过 3 行 SQL 时
- 同一个模型被多个路由复用时
- 简单查询直接写在路由里即可

### 什么时候加 Service 层

**默认**：暂不加，等业务逻辑出现 3+ 处重复

**例外**（需说明理由）：
- 项目初始化/架构设计阶段
- 用户明确要求分层架构
- 复杂业务需要解耦

### 数据库
- 使用 SQLAlchemy ORM
- ORM 模型和 Pydantic 模型必须分离
- 不直接在路由里写 SQL 字符串

### 错误处理
- 使用 HTTPException
- 统一错误响应格式

---

## ThinkPHP 8 规范

- 遵循 ThinkPHP 官方规范
- 控制器：`app/controller/`
- 模型：`app/model/`
- 验证器：`app/validate/`
- 中间件：`app/middleware/`

### 错误处理
- 使用 `throw new \think\exception\ValidateException()`
- 或 `json()` 直接返回错误

---

## 后端设计原则

**分层原则**（默认）：
- 不在路由里直接写复杂业务逻辑
- 不在 models 里写业务逻辑
- 不返回 ORM 模型给前端（必须转 Pydantic）
- 不过度使用中间件

**允许情况**（需说明收益）：
- 简单查询直接写在路由里（≤3行）
- 出现 3+ 重复时提取到 crud/ 或 service/
- 创建必要的验证器（避免重复校验）


