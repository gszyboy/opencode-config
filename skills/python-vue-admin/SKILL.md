---
name: python-vue-admin
description: |
  创建 FastAPI + Vue3 全栈管理后台项目。当用户说"创建项目"、"初始化项目"、"新建项目"、
  "fastapi + vue"、"python + vue3"、"后端 + 前端 admin"、"全栈脚手架"、
  "benavlabs + vue-pure-admin"、"FastAPI boilerplate + Vue"、"想用 FastAPI 和 Vue 搭一个后台"，
  或任何涉及用 Python FastAPI 后端 + Vue3 前端组合创建新项目的场景，必须触发此 Skill。
  也适用于：用户提到想找一个"开箱即用的前后端整合方案"、想"快速搭建管理后台"、想"整合 benavlabs FastAPI boilerplate 和 vue-pure-admin"。
---

# python-vue-admin Skill

整合 **benavlabs/FastAPI-boilerplate** (Python 后端) + **vue-pure-admin** (Vue3 前端)，创建完整的全栈管理后台项目。

## 工作目录

所有操作在用户指定的项目目录下进行。假设用户要创建的项目位于 `{project_root}/`。

## 核心技术栈

| 层 | 技术 |
|---|------|
| **后端框架** | FastAPI (benavlabs/FastAPI-boilerplate) |
| **前端框架** | Vue 3 + Composition API + TypeScript |
| **UI 组件** | Element Plus |
| **构建工具** | Vite |
| **状态管理** | Pinia |
| **样式** | Tailwind CSS |
| **后端 ORM** | SQLAlchemy 2.0 (async) |
| **后端校验** | Pydantic V2 |
| **数据库** | PostgreSQL |
| **缓存/队列** | Redis + ARQ |
| **部署** | Docker + Docker Compose |
| **认证** | JWT (前后端打通) |

## 项目结构

```
{project_root}/
├── backend/                    # benavlabs/FastAPI-boilerplate
│   ├── src/
│   │   └── app/
│   │       ├── main.py
│   │       ├── config.py
│   │       ├── api/
│   │       │   └── v1/
│   │       │       ├── auth.py
│   │       │       └── users.py
│   │       ├── schemas/        # Pydantic models
│   │       ├── models/         # SQLAlchemy models
│   │       └── core/
│   ├── docker-compose.yml
│   └── Dockerfile
├── frontend/                  # vue-pure-admin (pure-admin-thin)
│   ├── src/
│   │   ├── api/
│   │   │   └── system/
│   │   │       └── auth.ts
│   │   ├── stores/
│   │   │   └── user.ts
│   │   └── views/
│   └── package.json
├── docker-compose.yml          # 统一部署
└── README.md
```

---

## 步骤 1: 克隆后端脚手架

### 1.1 克隆 benavlabs/FastAPI-boilerplate

```bash
git clone https://github.com/benavlabs/FastAPI-boilerplate.git backend
cd backend

# 选择部署模式 (local/staging/production)
./setup.py
```

### 1.2 环境变量配置

在 `backend/src/.env` 中配置：

```env
# 环境模式
ENVIRONMENT=local

# 数据库 (PostgreSQL)
DATABASE_URL=postgresql+asyncpg://app:apppassword@localhost:5432/app

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT 配置
SECRET_KEY=your-super-secret-key-change-this-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Admin 面板
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
CRUD_ADMIN_ENABLED=true
CRUD_ADMIN_MOUNT_PATH=/admin
```

### 1.3 验证后端启动

```bash
cd backend
uv sync
uv run uvicorn src.app.main:app --reload
# 访问 http://localhost:8000/docs 查看 API 文档
```

---

## 步骤 2: 克隆前端脚手架

### 2.1 克隆 pure-admin-thin (精简版)

```bash
# 返回项目根目录
cd ..

# 克隆 vue-pure-admin 精简版 (非国际化)
git clone https://github.com/pure-admin/pure-admin-thin.git frontend
cd frontend
pnpm install
```

### 2.2 配置前端环境变量

创建/编辑 `frontend/.env.development`:

```env
# API 基础路径 (代理到后端)
VITE_APP_BASE_API = '/api/v1'
VITE_APP_TITLE = '管理后台'
VITE_ROUTER_HISTORY = 'hash'

# 接口地址 (开发环境)
VITE_APP_API_URL = 'http://localhost:8000'
```

### 2.3 配置 Vite 代理 (开发环境)

编辑 `frontend/vite.config.ts`，添加代理：

```typescript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src')
    }
  },
  server: {
    port: 5173,
    proxy: {
      // 代理 API 请求到后端
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
```

---

## 步骤 3: 前端 API 封装 (JWT 对接)

### 3.1 安装 axios

```bash
pnpm add axios
```

### 3.2 创建 API 请求封装

创建 `frontend/src/utils/http.ts`:

```typescript
import axios from 'axios'
import type { AxiosInstance, AxiosRequestConfig } from 'axios'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'

const service: AxiosInstance = axios.create({
  baseURL: '/api/v1',
  timeout: 5000
})

// 请求拦截器: 添加 JWT Token
service.interceptors.request.use(
  (config) => {
    const userStore = useUserStore()
    if (userStore.token) {
      config.headers.Authorization = `Bearer ${userStore.token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// 响应拦截器: 处理 Token 过期
service.interceptors.response.use(
  (response) => {
    const { code, message, data } = response.data
    if (code === 200 || code === 0) {
      return data
    }
    ElMessage.error(message || '请求失败')
    return Promise.reject(new Error(message || '请求失败'))
  },
  async (error) => {
    // 401: Token 过期，尝试刷新
    if (error.response?.status === 401) {
      const userStore = useUserStore()
      try {
        await userStore.refreshToken()
        // 重试原请求
        return service(error.config)
      } catch {
        userStore.logout()
        window.location.href = '/login'
      }
    }
    ElMessage.error(error.response?.data?.message || '请求失败')
    return Promise.reject(error)
  }
)

export default service
```

### 3.3 创建 User Store (Pinia)

创建 `frontend/src/stores/user.ts`:

```typescript
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { login as loginApi, refreshToken as refreshTokenApi } from '@/api/system/auth'

export const useUserStore = defineStore('user', () => {
  const token = ref<string>(localStorage.getItem('token') || '')
  const refresh_token = ref<string>(localStorage.getItem('refresh_token') || '')

  async function login(username: string, password: string) {
    const res = await loginApi({ username, password })
    token.value = res.access_token
    refresh_token.value = res.refresh_token
    localStorage.setItem('token', res.access_token)
    localStorage.setItem('refresh_token', res.refresh_token)
  }

  async function refreshToken() {
    try {
      const res = await refreshTokenApi({ refresh_token: refresh_token.value })
      token.value = res.access_token
      localStorage.setItem('token', res.access_token)
    } catch {
      logout()
    }
  }

  function logout() {
    token.value = ''
    refresh_token.value = ''
    localStorage.removeItem('token')
    localStorage.removeItem('refresh_token')
  }

  return { token, refresh_token, login, refreshToken, logout }
})
```

### 3.4 创建认证 API

创建 `frontend/src/api/system/auth.ts`:

```typescript
import http from '@/utils/http'

export interface LoginReq {
  username: string
  password: string
}

export interface LoginRes {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface RefreshReq {
  refresh_token: string
}

export const login = (data: LoginReq) => {
  return http.request<LoginRes>('post', '/auth/login', { data })
}

export const refreshToken = (data: RefreshReq) => {
  return http.request<LoginRes>('post', '/auth/refresh', { data })
}
```

### 3.5 修改登录页面

编辑 `frontend/src/views/login/index.vue`，对接后端登录 API：

```vue
<script setup lang="ts">
import { useUserStore } from '@/stores/user'
import { useRouter } from 'vue-router'

const userStore = useUserStore()
const router = useRouter()

async function handleLogin() {
  try {
    await userStore.login(form.username, form.password)
    router.push('/')
  } catch (error) {
    console.error('登录失败:', error)
  }
}
</script>
```

---

## 步骤 4: Docker Compose 统一部署

### 4.1 创建统一 docker-compose.yml

在 `{project_root}/docker-compose.yml`:

```yaml
version: '3.8'

services:
  # 前端 (Nginx)
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "80:80"
    depends_on:
      - backend
    networks:
      - app-network

  # 后端 (FastAPI + Uvicorn)
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://app:apppassword@db:5432/app
      - REDIS_URL=redis://cache:6379/0
      - SECRET_KEY=your-secret-key-change-in-production
      - ENVIRONMENT=staging
    depends_on:
      - db
      - cache
    networks:
      - app-network
    volumes:
      - ./backend/src:/app/src

  # PostgreSQL 数据库
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: app
      POSTGRES_PASSWORD: apppassword
      POSTGRES_DB: app
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - app-network

  # Redis 缓存
  cache:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - app-network

volumes:
  postgres_data:
  redis_data:

networks:
  app-network:
    driver: bridge
```

### 4.2 修改前端 Dockerfile (生产环境)

创建/编辑 `frontend/Dockerfile`:

```dockerfile
# 前端构建
FROM node:20-alpine as builder

WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN corepack enable && pnpm install

COPY . .
RUN pnpm build

# Nginx 部署
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### 4.3 创建 Nginx 配置

创建 `frontend/nginx.conf`:

```conf
server {
    listen 80;
    server_name localhost;

    root /usr/share/nginx/html;
    index index.html;

    # 前端路由 (SPA)
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API 代理到后端
    location /api/ {
        proxy_pass http://backend:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 4.4 修改后端 Dockerfile

编辑 `backend/Dockerfile` (local_with_uvicorn 版本):

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# 安装 uv
RUN pip install uv

# 复制依赖文件
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# 复制代码
COPY . .

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 步骤 5: 验证部署

### 5.1 启动所有服务

```bash
# 在项目根目录
docker compose up -d

# 查看日志
docker compose logs -f
```

### 5.2 访问

- **前端**: http://localhost
- **后端 API 文档**: http://localhost:8000/docs
- **Admin 面板**: http://localhost:8000/admin (可选，benavlabs 内置)

### 5.3 测试登录

1. 访问 http://localhost
2. 使用后端配置的 Admin 账号登录 (默认: admin / admin123)
3. 验证 Token 能正确刷新

---

## 常用命令

```bash
# 进入后端目录
cd backend

# 安装依赖
uv sync

# 运行开发服务器
uv run uvicorn src.app.main:app --reload

# 数据库迁移
cd src && uv run alembic revision --autogenerate -m "add xxx"
cd src && uv run alembic upgrade head

# 运行测试
uv run pytest

# 进入前端目录
cd ../frontend

# 安装依赖
pnpm install

# 开发服务器
pnpm dev

# 构建生产版本
pnpm build
```

---

## 后端 API 端点参考

benavlabs/FastAPI-boilerplate 提供的端点：

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | /api/v1/auth/login | 登录 |
| POST | /api/v1/auth/refresh | 刷新 Token |
| POST | /api/v1/auth/logout | 登出 |
| GET | /api/v1/users/me | 获取当前用户 |
| GET | /api/v1/users | 获取用户列表 (需认证) |
| POST | /api/v1/tasks/task | 触发后台任务 |

---

## 故障排查

### CORS 问题
检查后端 `src/app/core/config.py` 中的 CORS 配置：
```python
CORS_ORIGINS = ["http://localhost:80", "http://localhost:5173"]
```

### 数据库连接问题
确认 PostgreSQL 容器已启动：
```bash
docker compose ps db
docker compose logs db
```

### Token 相关问题
1. 确认后端 JWT 密钥配置正确
2. 检查前端 axios 拦截器是否正确添加 Authorization 头
3. 确认 Redis 正在运行（用于 Token 黑名单）

---

## 相关资源

- [benavlabs/FastAPI-boilerplate](https://github.com/benavlabs/FastAPI-boilerplate)
- [vue-pure-admin](https://github.com/pure-admin/vue-pure-admin)
- [pure-admin-thin (精简版)](https://github.com/pure-admin/pure-admin-thin)
- [benavlabs CRUDAdmin](https://github.com/benavlabs/crudadmin)