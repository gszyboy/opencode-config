#!/bin/bash
# init-project.sh - 初始化 FastAPI + Vue3 Admin 项目
# 用法: ./init-project.sh [项目名称]

set -e

PROJECT_NAME=${1:-my-fullstack-project}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🚀 创建项目: $PROJECT_NAME"
echo "📁 项目目录: $PROJECT_ROOT"

# 1. 克隆后端
echo "📦 克隆 benavlabs/FastAPI-boilerplate..."
git clone https://github.com/benavlabs/FastAPI-boilerplate.git backend

# 2. 选择后端部署模式
echo "⚙️ 选择后端部署模式 (local/staging/production):"
select MODE in local staging production; do
  if [ -n "$MODE" ]; then
    echo "   选择了: $MODE"
    break
  fi
done

cd backend && ./setup.py $MODE && cd ..

# 3. 克隆前端
echo "📦 克隆 vue-pure-admin 精简版..."
git clone https://github.com/pure-admin/pure-admin-thin.git frontend

# 4. 安装前端依赖
echo "📦 安装前端依赖..."
cd frontend && pnpm install && cd ..

# 5. 创建 docker-compose.yml
echo "🐳 创建 docker-compose.yml..."
cat > docker-compose.yml << 'EOF'
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
      - app-network

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://app:apppassword@db:5432/app
      - REDIS_URL=redis://cache:6379/0
      - SECRET_KEY=change-me-in-production
      - ENVIRONMENT=staging
    depends_on:
      - db
      - cache
    networks:
      - app-network

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: app
      POSTGRES_PASSWORD: apppassword
      POSTGRES_DB: app
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - app-network

  cache:
    image: redis:7-alpine
    networks:
      - app-network

volumes:
  postgres_data:

networks:
  app-network:
    driver: bridge
EOF

echo "✅ 项目初始化完成!"
echo ""
echo "下一步:"
echo "  1. cd backend && cp src/.env.example src/.env && vim src/.env"
echo "  2. cd frontend && cp .env.example .env && vim .env"
echo "  3. docker compose up -d"
echo "  4. 访问 http://localhost"