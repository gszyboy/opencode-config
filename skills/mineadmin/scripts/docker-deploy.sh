#!/bin/bash
# MineAdmin Docker 部署脚本

set -e

echo "=== MineAdmin Docker 部署 ==="

# 创建网络
docker network create mineadmin-network 2>/dev/null || true

echo "1. 构建前端镜像..."
cd frontend
docker build -t mineadmin-frontend .

echo ""
echo "2. 构建后端镜像..."
cd ../backend
docker build -t mineadmin-backend .

echo ""
echo "3. 启动所有服务..."
docker compose up -d

echo ""
echo "=== 部署完成 ==="
echo ""
echo "服务地址:"
echo "  前端: http://localhost"
echo "  后端: http://localhost:9501"
echo ""
echo "查看日志: docker compose logs -f"