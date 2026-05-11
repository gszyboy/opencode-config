# python-vue-admin Skill

整合 benavlabs/FastAPI-boilerplate + vue-pure-admin 的完整全栈管理后台模板。

## 文件结构

```
python-vue-admin/
├── SKILL.md                    # 主技能文档
├── scripts/
│   ├── init-project.sh         # 一键初始化项目
│   ├── setup-auth.sh           # JWT 认证对接
│   └── nginx.conf              # Nginx 配置模板
└── README.md                   # 本文件
```

## 快速开始

### 方式一：使用 Skill 指导手动整合

1. 阅读 SKILL.md
2. 按照步骤克隆和配置后端 + 前端
3. 对接 JWT 认证
4. 配置 Docker Compose 部署

### 方式二：使用脚本一键初始化

```bash
cd {your-project-dir}
./init-project.sh
cd backend && cp src/.env.example src/.env
cd ../frontend && cp .env.example .env
docker compose up -d
```

### 方式三：Docker Compose 部署

```yaml
# docker-compose.yml
services:
  frontend:
    build: ./frontend
    ports:
      - "80:80"
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://app:apppassword@db:5432/app
      - REDIS_URL=redis://cache:6379/0
```

## 技术栈

- **后端**: FastAPI + SQLAlchemy 2.0 + Pydantic V2 + PostgreSQL + Redis
- **前端**: Vue 3 + TypeScript + Element Plus + Pinia + TailwindCSS
- **部署**: Docker + Nginx

## 资源链接

- [benavlabs/FastAPI-boilerplate](https://github.com/benavlabs/FastAPI-boilerplate)
- [vue-pure-admin](https://github.com/pure-admin/vue-pure-admin)
- [pure-admin-thin](https://github.com/pure-admin/pure-admin-thin)
- [CRUDAdmin](https://github.com/benavlabs/crudadmin)