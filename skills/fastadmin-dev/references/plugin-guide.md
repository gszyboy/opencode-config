# FastAdmin 插件开发指南

## 插件简介

FastAdmin 插件系统基于 ThinkPHP 的钩子机制，支持：
- 独立的数据库表和模型
- 独立的控制器和视图
- 独立的前端资源
- 与主系统的权限、菜单集成
- 钩子（Hook）机制扩展主系统功能

## 插件目录结构

```
addons/
└── example/                    # 插件标识（小写）
    ├── config.php              # 插件配置
    ├── info.ini                # 插件信息
    ├── install.sql             # 安装 SQL
    ├── uninstall.sql           # 卸载 SQL
    ├── Example.php             # 插件主文件（钩子处理）
    ├── controller/             # 控制器
    │   └── Index.php
    ├── model/                  # 模型
    ├── view/                   # 视图
    ├── lang/                   # 语言包
    ├── public/                 # 前端资源
    │   └── assets/
    │       └── js/
    │       └── css/
    └── library/                # 类库
```

## 创建插件

### 方法1：命令行创建（推荐）

```bash
# 创建本地插件
php think addon -a myplugin -c create
```

### 方法2：手动创建

1. 在 `addons/` 目录创建插件文件夹
2. 创建必要的文件（见下方模板）
3. 在后台 "插件管理" 中安装

### 插件信息文件 (info.ini)

```ini
name = myplugin
title = 我的插件
intro = 这是一个示例插件
author = Your Name
website = https://www.example.com
version = 1.0.0
state = 1
```

### 插件配置文件 (config.php)

```php
<?php
return [
    [
        'name' => 'switch',
        'title' => '开关',
        'type' => 'radio',
        'content' => [
            1 => '开启',
            0 => '关闭',
        ],
        'value' => '1',
        'rule' => 'required',
    ],
    [
        'name' => 'title',
        'title' => '标题',
        'type' => 'text',
        'content' => [],
        'value' => '默认标题',
        'rule' => 'required',
    ],
];
```

### 插件主文件 (Example.php)

```php
<?php
namespace addons\example;

use think\Addons;

class Example extends Addons
{
    // 插件安装方法
    public function install()
    {
        return true;
    }

    // 插件卸载方法
    public function uninstall()
    {
        return true;
    }

    // 实现的钩子方法
    public function testHook($params)
    {
        // 处理钩子逻辑
        return 'Hello from plugin';
    }
}
```

## 插件管理命令

```bash
# 创建插件
php think addon -a myplugin -c create

# 启用插件
php think addon -a myplugin -c enable

# 禁用插件
php think addon -a myplugin -c disable

# 卸载插件
php think addon -a myplugin -c uninstall

# 刷新插件缓存
php think addon -a myplugin -c refresh

# 打包插件
php think addon -a myplugin -c package

# 将 CRUD 文件移动到插件
php think addon -a myplugin -c move
```

## 常用钩子 (Hooks)

### 页面钩子

```php
// 页面顶部
{:hook('pageHeader', ['widget' => ''])}

// 页面底部
{:hook('pageFooter', ['widget' => ''])}

// 内容区域顶部
{:hook('pageContentHeader', ['widget' => ''])}

// 内容区域底部
{:hook('pageContentFooter', ['widget' => ''])}
```

### 导航钩子

```php
// 后台导航
{:hook('adminNavbar', ['widget' => ''])}

// 工具栏
{:hook('adminToolBar', ['widget' => ''])}
```

### 表单钩子

```php
// 表单顶部
{:hook('formBuilderHeader', ['widget' => ''])}

// 表单底部
{:hook('formBuilderFooter', ['widget' => ''])}
```

### 表格钩子

```php
// 表格顶部
{:hook('tableHeader', ['widget' => ''])}

// 表格底部
{:hook('tableFooter', ['widget' => ''])}
```

## 插件控制器

```php
<?php
namespace addons\example\controller;

use think\addons\Controller;

class Index extends Controller
{
    public function index()
    {
        // 访问插件配置
        $config = get_addon_config('example');
        
        // 渲染视图
        return $this->fetch();
    }
}
```

**访问 URL：**
```
/addons/example/index/index
```

## 插件模型

```php
<?php
namespace addons\example\model;

use think\Model;

class Article extends Model
{
    protected $name = 'example_article';
    protected $autoWriteTimestamp = true;
}
```

## 插件视图

视图文件位于 `addons/example/view/index/index.html`

```html
{extend name='layout/default'}

{block name='content'}
<div class="panel panel-default">
    <div class="panel-heading">
        <h3 class="panel-title">我的插件</h3>
    </div>
    <div class="panel-body">
        <!-- 插件内容 -->
    </div>
</div>
{/block}

{block name='script'}
<script>
    // 插件 JS
</script>
{/block}
```

## 插件前端资源

```
addons/example/public/assets/
├── js/
│   └── example.js
├── css/
│   └── example.css
└── img/
    └── logo.png
```

在视图中引用：
```html
<link rel="stylesheet" href="/assets/addons/example/css/example.css">
<script src="/assets/addons/example/js/example.js"></script>
```

## 插件与主系统集成

### 添加后台菜单

在插件 `install.sql` 中添加菜单：

```sql
INSERT INTO `fa_auth_rule` (`type`, `pid`, `name`, `title`, `icon`, `condition`, `remark`, `ismenu`, `createtime`, `updatetime`, `weigh`, `status`) 
VALUES ('addon', 0, 'example', '示例插件', 'fa fa-plug', '', '', 1, UNIX_TIMESTAMP(), UNIX_TIMESTAMP(), 0, 'normal');
```

### 添加权限节点

```sql
INSERT INTO `fa_auth_rule` (`type`, `pid`, `name`, `title`, `icon`, `condition`, `remark`, `ismenu`, `createtime`, `updatetime`, `weigh`, `status`) 
VALUES 
('addon', @parent_id, 'example/index', '查看', 'fa fa-circle-o', '', '', 0, UNIX_TIMESTAMP(), UNIX_TIMESTAMP(), 0, 'normal'),
('addon', @parent_id, 'example/index/add', '添加', 'fa fa-circle-o', '', '', 0, UNIX_TIMESTAMP(), UNIX_TIMESTAMP(), 0, 'normal'),
('addon', @parent_id, 'example/index/edit', '编辑', 'fa fa-circle-o', '', '', 0, UNIX_TIMESTAMP(), UNIX_TIMESTAMP(), 0, 'normal'),
('addon', @parent_id, 'example/index/del', '删除', 'fa fa-circle-o', '', '', 0, UNIX_TIMESTAMP(), UNIX_TIMESTAMP(), 0, 'normal');
```

## 插件安装/卸载 SQL

### install.sql

```sql
-- 创建插件表
CREATE TABLE IF NOT EXISTS `fa_example_log` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `user_id` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '用户ID',
  `action` varchar(50) NOT NULL DEFAULT '' COMMENT '操作',
  `ip` varchar(50) NOT NULL DEFAULT '' COMMENT 'IP地址',
  `createtime` int(10) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='插件日志表';
```

### uninstall.sql

```sql
-- 删除插件表
DROP TABLE IF EXISTS `fa_example_log`;
```

## 打包发布

```bash
# 生成 zip 包
php think addon -a myplugin -c package

# 生成的文件位于
runtime/addons/myplugin-1.0.0.zip
```

## 插件开发最佳实践

1. **命名规范** - 插件标识使用小写字母和下划线
2. **配置化** - 将可变参数放入 config.php
3. **数据库前缀** - 使用 `fa_` 前缀或自定义前缀
4. **权限控制** - 正确注册权限节点
5. **资源分离** - 前端资源放在插件目录
6. **钩子命名** - 使用插件标识作为前缀，避免冲突
7. **版本管理** - 在 info.ini 中维护版本号
8. **安装校验** - install() 方法返回 true/false