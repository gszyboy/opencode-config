# FastAdmin 安装配置指南

## 安装方法

### 方法一：下载完整包安装（推荐）

**步骤：**

1. **下载完整包**
   - 访问：https://www.fastadmin.net/download.html
   - 下载最新版完整包（包含所有依赖）

2. **上传到服务器**
   ```bash
   # 解压到站点目录
   unzip fastadmin-full.zip -d /www/wwwroot/your-domain/
   ```

3. **配置站点**
   - 运行目录设置为：`/public`
   - 伪静态规则：选择 `thinkphp`
   - PHP 版本：7.4+ (推荐 7.4)

4. **访问安装页面**
   ```
   http://your-domain/install.php
   ```

5. **填写数据库信息**
   - 数据库主机、用户名、密码
   - 数据库名（不存在会自动创建）
   - 表前缀（默认 `fa_`）
   - 管理员账号密码

6. **完成安装**
   - 安装完成后会显示后台入口地址
   - 后台入口为随机生成的文件名，位于 `public/` 目录

### 方法二：命令行安装

**适用于：** 已有代码，需要重新安装或自动化部署

```bash
cd /path/to/fastadmin

# 交互式安装
php think install

# 全自动安装（推荐用于脚本部署）
php think install \
  -a 127.0.0.1 \
  -u root \
  -p your_password \
  -d fastadmin_db \
  -r fa_

# 强制重新安装（会清空数据！）
php think install -f 1
```

**命令参数：**
| 参数 | 说明 | 示例 |
|------|------|------|
| `-a` | 数据库地址 | `-a 127.0.0.1` |
| `-u` | 数据库用户名 | `-u root` |
| `-p` | 数据库密码 | `-p 123456` |
| `-d` | 数据库名 | `-d fastadmin` |
| `-r` | 表前缀 | `-r fa_` |
| `-f` | 强制重新安装 | `-f 1` |

### 方法三：Composer 安装

```bash
# 创建项目
composer create-project fastadmin/fastadmin your-project

# 进入目录
cd your-project

# 安装依赖
composer install

# 执行安装
php think install
```

### 方法四：Git 克隆

```bash
# 克隆仓库
git clone https://github.com/karsonzhang/fastadmin.git

# 进入目录
cd fastadmin

# 安装依赖
composer install

# 执行安装
php think install
```

**注意：** Git 克隆的代码缺少部分资源文件，建议下载完整包覆盖。

---

## 环境配置

### 服务器要求

| 组件 | 要求 | 推荐 |
|------|------|------|
| PHP | 7.4+ | 7.4 (v1.7.0+ 推荐 8.0+) |
| MySQL | 5.6 - 8.0 | 5.7 |
| Web 服务器 | Apache/Nginx | Nginx |
| Node.js | 可选 | 14+ |

### PHP 扩展要求

必需扩展：
- `pdo_mysql`
- `mbstring`
- `gd` 或 `imagick`
- `curl`
- `fileinfo`
- `openssl`

建议扩展：
- `redis`（用于缓存）
- `swoole`（用于高性能部署）

### Nginx 配置

```nginx
server {
    listen 80;
    server_name your-domain.com;
    root /www/wwwroot/your-domain/public;
    index index.php index.html;

    location / {
        if (!-e $request_filename) {
            rewrite ^(.*)$ /index.php?s=$1 last;
            break;
        }
    }

    location ~ \.php$ {
        fastcgi_pass 127.0.0.1:9000;
        fastcgi_index index.php;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        include fastcgi_params;
    }

    location ~ /\.(?!well-known).* {
        deny all;
    }
}
```

### Apache 配置

确保 `.htaccess` 文件存在（完整包已包含）：

```apache
<IfModule mod_rewrite.c>
  Options +FollowSymlinks -Multiviews
  RewriteEngine On

  RewriteCond %{REQUEST_FILENAME} !-d
  RewriteCond %{REQUEST_FILENAME} !-f
  RewriteRule ^(.*)$ index.php?s=$1 [QSA,PT,L]
</IfModule>
```

---

## 配置文件说明

### 数据库配置

**文件：** `application/database.php`

```php
return [
    'type'        => 'mysql',
    'hostname'    => '127.0.0.1',
    'database'    => 'fastadmin',
    'username'    => 'root',
    'password'    => 'your_password',
    'hostport'    => '3306',
    'params'      => [],
    'charset'     => 'utf8mb4',
    'prefix'      => 'fa_',
];
```

### 应用配置

**文件：** `application/config.php`

关键配置项：
```php
return [
    // 应用调试模式
    'app_debug'              => true,  // 开发环境 true，生产环境 false
    
    // 应用Trace
    'app_trace'              => false,
    
    // 默认模块
    'default_module'         => 'index',
    
    // 禁止访问模块
    'deny_module_list'       => ['common'],
    
    // 默认时区
    'default_timezone'       => 'Asia/Shanghai',
    
    // 语言设置
    'default_lang'           => 'zh-cn',
];
```

### 多数据库配置

在 `application/config.php` 中添加：

```php
'database' => [
    // 默认数据库
    'default' => [
        'type'     => 'mysql',
        'hostname' => '127.0.0.1',
        'database' => 'db1',
        'username' => 'root',
        'password' => 'pass1',
    ],
    // 第二个数据库
    'db2' => [
        'type'     => 'mysql',
        'hostname' => '127.0.0.1',
        'database' => 'db2',
        'username' => 'root',
        'password' => 'pass2',
    ],
],
```

使用多数据库生成 CRUD：
```bash
php think crud -t test --db=db2
```

---

## 常见问题

### 安装问题

**Q: 提示 "请先下载完整包覆盖后再安装"**
A: Git 克隆的代码缺少资源文件，需下载完整包覆盖

**Q: 提示 "当前权限不足，无法写入配置文件"**
A: 检查 `application/database.php` 是否可写，或检查 PHP 的 `open_basedir` 配置

**Q: 提示 "找不到 fa_admin 表"**
A: 检查 MySQL 是否开启 InnoDB 引擎支持

**Q: 安装后 404 错误**
A: 检查伪静态配置，确保运行目录是 `/public`

**Q: 宝塔面板 putenv 错误**
A: 在 PHP 禁用函数中移除 `putenv`

### 部署问题

**Q: 如何找到后台入口？**
A: 在 `public/` 目录下查找随机命名的 `.php` 文件

**Q: 如何修改后台入口文件名？**
A: 重命名 `public/` 下的入口文件，并同步修改 `application/config.php` 中的 `admin` 配置

**Q: 生产环境如何配置？**
A: 
1. `app_debug` 设为 `false`
2. 执行 `php think min -m all -r all` 压缩资源
3. 配置 HTTPS
4. 开启 OPcache
5. 配置 Redis 缓存

### 开发环境建议

```bash
# 开启 debug 模式
# application/config.php
'app_debug' => true,

# 开启错误显示
error_reporting(E_ALL);
ini_set('display_errors', '1');

# 关闭缓存（开发时）
# application/config.php
'cache' => [
    'type' => 'none',
],
```