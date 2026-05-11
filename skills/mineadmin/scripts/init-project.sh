#!/bin/bash
# MineAdmin 一键初始化脚本

set -e

echo "=== MineAdmin 初始化脚本 ==="

# 检查 PHP
if ! command -v php &> /dev/null; then
    echo "错误: 需要 PHP 8.1+"
    exit 1
fi

PHP_VERSION=$(php -v | head -n1 | awk '{print $2}')
echo "PHP 版本: $PHP_VERSION"

# 检查 Composer
if ! command -v composer &> /dev/null; then
    echo "错误: 需要 Composer"
    exit 1
fi

# 检查 Node
if ! command -v node &> /dev/null; then
    echo "错误: 需要 Node.js"
    exit 1
fi

# 检查 pnpm
if ! command -v pnpm &> /dev/null; then
    echo "安装 pnpm..."
    npm install -g pnpm
fi

echo ""
echo "1. 克隆 MineAdmin..."
git clone https://github.com/mineadmin/MineAdmin.git mineadmin
cd mineadmin

echo ""
echo "2. 安装后端依赖..."
cd backend
composer install

echo ""
echo "3. 配置后端环境..."
cp .env.example .env

echo ""
echo "4. 安装前端依赖..."
cd ../frontend
pnpm install

echo ""
echo "=== 初始化完成 ==="
echo ""
echo "下一步:"
echo "1. 编辑 backend/.env 配置数据库"
echo "2. 创建数据库: mysql -u root -p -e \"CREATE DATABASE mineadmin\""
echo "3. 运行迁移: cd backend && php bin/hyperf.php migrate"
echo "4. 启动后端: cd backend && php bin/hyperf.php start"
echo "5. 启动前端: cd frontend && pnpm dev"
echo ""
echo "访问: http://localhost:5173"
echo "默认账号: admin / mineadmin123"