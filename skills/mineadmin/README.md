# MineAdmin Skill

整合 MineAdmin (Hyperf 3.x + Swoole 5 + Vue3) 的完整全栈管理后台模板。

## 文件结构

```
mineadmin/
├── SKILL.md                    # 主技能文档
├── scripts/
│   ├── init-project.sh         # 一键初始化项目
│   ├── docker-deploy.sh        # Docker 部署脚本
│   └── nginx.conf              # Nginx 配置模板
└── README.md                   # 本文件
```

## 快速开始

### 方式一：使用 Skill 指导手动整合

1. 阅读 SKILL.md
2. 按照步骤克隆 MineAdmin
3. 配置环境变量
4. 启动开发服务

### 方式二：使用脚本一键初始化

```bash
cd {your-project-dir}
./init-project.sh
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
      - "9501:9501"
    environment:
      - DB_DRIVER=mysql
      - DB_HOST=db
      - REDIS_HOST=redis
  db:
    image: mysql:8.0
  redis:
    image: redis:7-alpine
```

## 技术栈

- **后端**: Hyperf 3.x + Swoole 5 + PHP 8.1+
- **前端**: Vue 3 + TypeScript + Arco Design Pro + Pinia + Vite 5
- **数据库**: MySQL / PostgreSQL / SQL Server
- **认证**: 双 Token (JWT)
- **部署**: Docker + Nginx

## 特点

- ✅ 开箱即用 (前后端一体)
- ✅ Swoole 5 协程高性能
- ✅ CRUD 代码生成器
- ✅ RBAC 权限管理
- ✅ 双 Token 认证
- ✅ 多数据库支持
- ✅ Docker 部署支持

## 默认账号

- **前端**: http://localhost:5173
- **后端**: http://localhost:9501
- **账号**: admin
- **密码**: mineadmin123

## 资源链接

- [MineAdmin GitHub](https://github.com/mineadmin/MineAdmin)
- [MineAdmin 文档](https://doc.mineadmin.com/)
- [Hyperf 框架](https://hyperf.wiki/)
- [Swoole 文档](https://www.swoole.com/)
- [Arco Design Vue](https://arco.design/vue/component/introduce)