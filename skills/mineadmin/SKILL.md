---
name: mineadmin
description: |
  创建 MineAdmin 全栈管理后台项目。触发场景：用户说"创建项目"、"初始化项目"、
  "新建项目"、"MineAdmin"、"PHP 后台"、"Swoole 后台"、"Hyperf 后台"、
  "PHP admin"、"高性能 PHP 管理后台"、"协程 PHP 后台"，
  或任何涉及用 PHP (Hyperf/Swoole) 后端创建新管理后台项目的场景。
  也适用于：用户想要"Swoole 高性能"、"协程 PHP"、"高并发 PHP"。
---

# MineAdmin Skill

整合 **MineAdmin** (Hyperf 3.x + Swoole 5 后端 + Vue3 前端)，创建完整的全栈管理后台项目。

## 项目信息

- **GitHub**: https://github.com/mineadmin/MineAdmin
- **文档**: https://doc.mineadmin.com/
- **Stars**: 1187+
- **协议**: AGPL / 商业授权
- **最新版本**: v3.0.9

## 核心技术栈

| 层 | 技术 |
|---|------|
| **后端框架** | Hyperf 3.x + Swoole 5 |
| **PHP 版本** | 8.1+ |
| **前端框架** | Vue 3 + Composition API + TypeScript |
| **UI 组件** | Arco Design Pro |
| **构建工具** | Vite 5 |
| **状态管理** | Pinia |
| **后端 ORM** | Hyperf\Database |
| **数据库** | MySQL / PostgreSQL / SQL Server |
| **认证** | 双 Token (Access + Refresh) |
| **部署** | Docker + Docker Compose |

## 项目结构

```
{project_root}/
├── mineadmin/                  # MineAdmin 主仓库 (前后端一体)
│   ├── backend/               # Hyperf 后端
│   │   ├── app/
│   │   │   ├── Controller/
│   │   │   ├── Model/
│   │   │   └── Service/
│   │   ├── config/
│   │   ├── docker-compose.yml
│   │   └── Dockerfile
│   └── frontend/              # Vue3 前端
│       ├── src/
│       │   ├── api/
│       │   ├── stores/
│       │   └── views/
│       ├── Dockerfile
│       └── package.json
└── README.md
```

---

## 步骤 1: 克隆 MineAdmin

### 1.1 克隆仓库

```bash
git clone https://github.com/mineadmin/MineAdmin.git mineadmin
cd mineadmin
```

### 1.2 安装依赖

```bash
# 后端依赖
cd backend
composer install

# 前端依赖
cd ../frontend
pnpm install
```

---

## 步骤 2: 环境配置

### 2.1 后端环境变量

复制环境配置示例文件：

```bash
cd backend
cp .env.example .env
```

编辑 `backend/.env`:

```env
# 应用配置
APP_ENV=dev
APP_DEBUG=true
APP_PORT=9501

# 数据库配置 (MySQL/PostgreSQL/SQL Server 三选一)
DB_DRIVER=mysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_DATABASE=mineadmin
DB_USERNAME=root
DB_PASSWORD=your_password

# Redis 配置
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

# JWT 配置
JWT_SECRET=your-super-secret-key
JWT_ACCESS_EXPIRE=7200
JWT_REFRESH_EXPIRE=604800

# Swoole 配置
SWOOLE_HTTP_PORT=9501
WORKER_NUM=4
```

### 2.2 数据库初始化

```bash
cd backend

# 创建数据库 (MySQL)
mysql -u root -p -e "CREATE DATABASE mineadmin DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 运行迁移
php bin/hyperf.php migrate

# 初始化数据 (管理员账号)
php bin/hyperf.php db:seed
```

### 2.3 前端环境变量

```bash
cd ../frontend
cp .env.example .env.development
```

编辑 `frontend/.env.development`:

```env
# API 地址
VITE_APP_API_URL=http://localhost:9501
VITE_APP_BASE_API=/
```

---

## 步骤 3: 启动开发服务

### 3.1 启动后端 (Swoole)

```bash
cd backend

# 开发模式 (热重载)
php bin/hyperf.php start

# 或使用 Composer 脚本
composer dev
```

### 3.2 启动前端 (Vite)

```bash
cd frontend

# 开发模式
pnpm dev

# 构建生产版本
pnpm build
```

### 3.3 访问

- **前端**: http://localhost:5173
- **后端 API**: http://localhost:9501
- **默认账号**: admin / mineadmin123

---

## 步骤 4: Docker Compose 部署

### 4.1 使用 MineAdmin 内置 Docker

```bash
cd backend

# 启动所有服务 (数据库 + Redis + 后端)
docker compose up -d

# 查看日志
docker compose logs -f
```

### 4.2 生产环境 Docker 配置

创建 `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "80:80"
    depends_on:
      - backend
    networks:
      - mineadmin-network

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "9501:9501"
    environment:
      - APP_ENV=prod
      - APP_DEBUG=false
      - DB_DRIVER=mysql
      - DB_HOST=db
      - DB_PORT=3306
      - DB_DATABASE=mineadmin
      - DB_USERNAME=mineadmin
      - DB_PASSWORD=mineadmin_password
      - REDIS_HOST=redis
      - REDIS_PORT=6379
    depends_on:
      - db
      - redis
    networks:
      - mineadmin-network
    volumes:
      - ./backend/runtime:/app/runtime

  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: root_password
      MYSQL_DATABASE: mineadmin
      MYSQL_USER: mineadmin
      MYSQL_PASSWORD: mineadmin_password
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
    networks:
      - mineadmin-network

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - mineadmin-network

volumes:
  mysql_data:
  redis_data:

networks:
  mineadmin-network:
    driver: bridge
```

### 4.3 前端 Dockerfile

创建 `frontend/Dockerfile`:

```dockerfile
FROM node:20-alpine as builder

WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN corepack enable && pnpm install

COPY . .
RUN pnpm build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### 4.4 Nginx 配置

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
        proxy_pass http://backend:9501/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

---

## 步骤 5: CRUD 代码生成

MineAdmin 提供图形化 CRUD 生成器。

### 5.1 使用命令行生成

```bash
cd backend

# 生成 CRUD
php bin/hyperf.php gen:curd User

# 生成迁移文件
php bin/hyperf.php gen:migration create_users_table

# 生成模型
php bin/hyperf.php gen:model User
```

### 5.2 手动创建 CRUD

创建控制器 `app/Controller/UserController.php`:

```php
<?php

declare(strict_types=1);

namespace App\Controller;

use Mine\Annotation\Route;
use Mine\MineController;

#[Route]
class UserController extends MineController
{
    #[Route(methods: 'GET', path: '/user/list')]
    public function list(): Response
    {
        $page = $this->request->input('page', 1);
        $pageSize = $this->request->input('pageSize', 10);

        $result = $this->service->paginate($page, $pageSize);

        return $this->success($result);
    }

    #[Route(methods: 'POST', path: '/user')]
    public function save(): Response
    {
        $data = $this->request->all();

        $result = $this->service->create($data);

        return $this->success($result);
    }

    #[Route(methods: 'PUT', path: '/user/{id}')]
    public function update(int $id): Response
    {
        $data = $this->request->all();

        $result = $this->service->update($id, $data);

        return $this->success($result);
    }

    #[Route(methods: 'DELETE', path: '/user/{id}')]
    public function delete(int $id): Response
    {
        $this->service->delete($id);

        return $this->success();
    }
}
```

---

## 步骤 6: 权限配置

### 6.1 角色权限

访问后台管理 -> 系统管理 -> 角色管理

1. 创建角色 (如: admin, editor)
2. 分配菜单权限
3. 分配数据权限

### 6.2 用户权限

访问后台管理 -> 系统管理 -> 用户管理

1. 创建用户
2. 分配角色
3. 设置部门归属

### 6.3 菜单权限

```
系统管理
├── 用户管理 (user)
│   ├── 用户列表 (user:list)
│   ├── 用户新增 (user:save)
│   ├── 用户编辑 (user:update)
│   └── 用户删除 (user:delete)
├── 角色管理 (role)
└── 菜单管理 (menu)
```

---

## 常用命令

```bash
# 后端
cd backend

# 启动 (开发)
php bin/hyperf.php start

# 启动 (生产)
php bin/hyperf.php start -d

# 迁移
php bin/hyperf.php migrate

# 回滚迁移
php bin/hyperf.php migrate:rollback

# 生成 CRUD
php bin/hyperf.php gen:curd {name}

# 清理缓存
php bin/hyperf.php cache:clear

# 前端
cd frontend

# 安装依赖
pnpm install

# 开发服务器
pnpm dev

# 构建
pnpm build

# 构建 SSR 版本
pnpm build:ssr
```

---

## 后端 API 端点参考

MineAdmin 后端提供的管理接口：

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | /api/system/user/login | 登录 |
| POST | /api/system/user/refresh | 刷新 Token |
| GET | /api/system/user/info | 获取用户信息 |
| POST | /api/system/user/logout | 登出 |
| GET | /api/system/menu/list | 获取菜单列表 |
| GET | /api/system/role/list | 获取角色列表 |
| CRUD | /api/system/{module}/{action} | 通用 CRUD |

---

## 故障排查

### Swoole 启动失败

1. 检查 PHP 版本 (需要 8.1+)
2. 检查 Swoole 扩展是否安装: `php -m | grep swoole`
3. 查看错误日志: `tail -f runtime/log/*.log`

### 数据库连接失败

1. 确认数据库服务运行中
2. 检查 `.env` 数据库配置
3. 确认数据库已创建: `mysql -u root -p -e "SHOW DATABASES;"`

### 前端无法访问后端 API

1. 检查后端是否启动: `curl http://localhost:9501`
2. 检查 Vite 代理配置 (vite.config.ts)
3. 检查 CORS 配置 (backend/config/autoload/cors.php)

### 权限不生效

1. 清除缓存: `php bin/hyperf.php cache:clear`
2. 检查用户角色配置
3. 检查菜单权限标识

---

## 相关资源

- [MineAdmin GitHub](https://github.com/mineadmin/MineAdmin)
- [MineAdmin 文档](https://doc.mineadmin.com/)
- [Hyperf 框架](https://hyperf.wiki/)
- [Swoole 文档](https://www.swoole.com/)
- [Arco Design Vue](https://arco.design/vue/component/introduce)

---

## 与 vue-pure-admin 的区别

| 维度 | MineAdmin | vue-pure-admin |
|------|-----------|----------------|
| **前端** | 自带 Vue3 + **Arco Design** | 自带 Vue3 + Element Plus |
| **后端** | 自带 Hyperf (Swoole) | 需要自建 |
| **融合度** | ✅ 开箱即用 | ❌ 需自建 API |
| **协议** | AGPL / 商业 | MIT |
| **性能** | Swoole 高性能 |取决于后端 |