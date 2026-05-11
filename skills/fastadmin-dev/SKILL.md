---
name: fastadmin-dev
description: >
  FastAdmin PHP 框架开发助手。当用户提到 FastAdmin、ThinkPHP 后台开发、
  一键生成 CRUD、php think 命令、FastAdmin 安装、FastAdmin 插件、
  后台管理系统开发、Bootstrap 后台框架、权限管理、菜单生成、
  API 文档生成、JS/CSS 压缩打包时，必须加载此 Skill。
  提供完整的命令行工具参考、CRUD 生成工作流、安装配置指南、
  插件开发规范和最佳实践。
---

# FastAdmin 开发助手

FastAdmin 是基于 ThinkPHP + Bootstrap 的极速后台开发框架。
本 Skill 提供完整的开发工作流支持，帮助开发者高效使用 FastAdmin 的命令行工具和最佳实践。

## 何时使用本 Skill

- 用户提到 "FastAdmin"、"ThinkPHP 后台"、"后台框架"
- 用户询问 CRUD 生成、菜单生成、权限配置
- 用户需要命令行工具参考 (`php think`)
- 用户询问安装、配置、部署相关问题
- 用户需要插件开发指导
- 用户遇到 FastAdmin 常见问题

## 核心工作流

### 1. 项目初始化工作流

**全新安装：**
```bash
# 方法1：下载完整包安装
# 访问 https://www.fastadmin.net/download.html 下载最新完整包
# 解压到站点目录，设置运行目录为 /public
# 访问 http://your-domain/install.php 完成安装

# 方法2：命令行一键安装
cd fastadmin
php think install -a 127.0.0.1 -u root -p your_password -d dbname -r fa_
```

**环境要求：**
- PHP 7.4+ (推荐 7.4，v1.7.0+ 推荐 PHP 8.0+)
- MySQL 5.6 - 8.0 (需支持 InnoDB)
- Web 服务器：Nginx (推荐) 或 Apache
- Node.js (用于前端资源打包)

### 2. 数据库设计规范

**表命名：**
- 使用 `fa_` 前缀（可配置）
- 表名使用小写 + 下划线，如 `fa_user_profile`
- 必须有且只有一个主键，不支持复合主键

**字段设计：**
- 字段名使用小写 + 下划线
- **必须添加字段注释和表注释**（CRUD 生成的重要依据）
- 常用字段：
  - `id` - 主键，自增
  - `createtime` - 创建时间 (int)
  - `updatetime` - 更新时间 (int)
  - `deletetime` - 删除时间 (int, 默认 NULL，用于回收站)
  - `status` - 状态 (enum/normal, hidden, deleted)
  - `weigh` - 排序权重 (int)

**字段后缀约定（自动生成组件）：**
| 后缀 | 自动生成的组件 |
|------|---------------|
| `_list`, `_data` | 复选框 |
| `_image`, `_img` | 图片上传 |
| `_file` | 文件上传 |
| `_time`, `_date` | 日期时间选择器 |
| `_switch` | 开关组件 |
| `_city` | 城市选择器 |
| `_selectpage` | SelectPage 下拉 |
| `_editor` | 富文本编辑器 |

### 3. CRUD 生成工作流

**标准流程：**
```bash
# Step 1: 设计数据库表并添加注释
# Step 2: 生成 CRUD
php think crud -t table_name -u 1

# Step 3: 刷新后台页面查看菜单
```

**常用 CRUD 命令：**
```bash
# 基础生成
php think crud -t test                    # 生成 fa_test 表的 CRUD
php think crud -t test -u 1               # 生成并自动创建菜单
php think crud -t test -d 1               # 删除已生成的 CRUD

# 自定义控制器和模型名
php think crud -t test_log -c testlog     # 自定义控制器名
php think crud -t test -m TestModel       # 自定义模型名

# 二级目录
php think crud -t test -c mydir/test      # 生成到二级目录

# 关联模型
php think crud -t test -r category -k category_id -p id
php think crud -t test --relation=category --relation=admin \
  --relationforeignkey=category_id --relationforeignkey=admin_id

# 多数据库
php think crud -t test --db=db_config_key

# 指定可见字段
php think crud -t test -i "id,name,status"

# 自定义组件后缀
php think crud -t test --setcheckboxsuffix=list --imagefield=image
```

**CRUD 生成文件清单：**
```
application/admin/
  controller/Test.php          # 控制器
  model/Test.php               # 模型
  validate/Test.php            # 验证器
  lang/zh-cn/test.php          # 语言包
  view/test/
    index.html                 # 列表页
    add.html                   # 添加页
    edit.html                  # 编辑页
    recyclebin.html            # 回收站
public/assets/js/backend/test.js  # 前端 JS
```

### 4. 菜单生成工作流

```bash
# 为指定控制器生成菜单
php think menu -c test

# 生成二级目录菜单
php think menu -c mydir/test

# 删除菜单
php think menu -c test -d 1

# 生成所有控制器的菜单（谨慎使用，先备份）
php think menu -c all-controller
```

### 5. 权限配置工作流

FastAdmin 使用基于 Auth 的权限管理系统：

**核心表：**
- `fa_admin` - 管理员表
- `fa_auth_group` - 角色组表
- `fa_auth_rule` - 权限规则表
- `fa_auth_group_access` - 用户角色关联表

**权限特性：**
- 支持无限级父子级权限继承
- 支持单管理员多角色
- 支持管理子级数据或个人数据
- 控制器方法注释中的 `@auth` 标签控制权限

### 6. 前端资源打包工作流

```bash
# 打包前后台所有资源
php think min -m all -r all

# 仅打包后台
php think min -m backend -r all

# 仅打包 JS
php think min -m all -r js

# 仅打包 CSS
php think min -m backend -r css

# 使用 uglify 压缩 JS
php think min -m backend -r js -o uglify
```

**注意：**
- 需要 Node.js 环境
- `app_debug=true` 时加载未压缩资源
- `app_debug=false` 时加载压缩资源
- 不要直接修改 `.min.js` 和 `.min.css` 文件

### 7. API 文档生成工作流

```bash
# 生成 API 文档
php think api --force=true

# 指定域名
php think api -u https://api.example.com --force=true

# 指定输出文件
php think api -o myapi.html --force=true

# 生成指定控制器文档
php think api -r Demo --force=true
```

**API 注释规范：**
```php
/**
 * 测试API
 * @ApiSector   (测试分组)
 * @ApiRoute    (/api/test)
 */
class Test extends \app\common\controller\Api
{
    /**
     * 测试方法
     * @ApiTitle    (测试标题)
     * @ApiSummary  (测试描述)
     * @ApiMethod   (POST)
     * @ApiRoute    (/api/test/test)
     * @ApiParams   (name="id", type="integer", required=true, description="ID")
     * @ApiReturn   ({"code":1,"msg":"成功"})
     */
    public function test($id = '')
    {
        $this->success("返回成功", $this->request->request());
    }
}
```

### 8. 插件管理工作流

```bash
# 创建本地插件
php think addon -a myaddon -c create

# 启用插件
php think addon -a example -c enable

# 禁用插件
php think addon -a example -c disable

# 卸载插件
php think addon -a example -c uninstall

# 刷新插件缓存
php think addon -a example -c refresh

# 打包插件为 zip
php think addon -a example -c package

# 将 CRUD 文件移动到插件目录
php think addon -a example -c move
```

## 参考文档索引

| 主题 | 参考文件 | 何时查阅 |
|------|---------|---------|
| 完整命令行参考 | `references/commands.md` | 需要查看所有命令参数 |
| CRUD 生成详解 | `references/crud-guide.md` | 生成 CRUD 时 |
| 安装配置指南 | `references/install-guide.md` | 安装或部署时 |
| 插件开发指南 | `references/plugin-guide.md` | 开发插件时 |

## 常见问题速查

**Q: 生成 CRUD 后菜单不显示？**
A: 使用 `-u 1` 参数生成菜单，或手动执行 `php think menu -c controller_name`

**Q: 关联表数据在列表不显示？**
A: 检查关联模型配置，建议使用在线命令行插件可视化生成

**Q: 回收站功能不生效？**
A: 确保表中有 `deletetime` 字段且默认值为 `NULL`

**Q: 安装后提示 404？**
A: 检查伪静态配置，Nginx/Apache 需配置 ThinkPHP 规则

**Q: 后台入口文件名是什么？**
A: 安装后在 `public` 目录生成的随机文件名 `.php`

**Q: 字段注释必须写吗？**
A: **必须！** CRUD 生成依赖字段注释自动生成语言包和组件

## 最佳实践

1. **始终添加字段注释** - 这是 CRUD 自动生成的基础
2. **使用命令行生成代码** - 比手动编写快 10 倍以上
3. **先设计数据库再生成代码** - 遵循数据库驱动开发模式
4. **定期压缩打包资源** - 生产环境前执行 `php think min`
5. **使用版本控制** - 生成代码后及时提交 Git
6. **备份数据库** - 执行 `php think menu -c all-controller` 前备份
7. **开发环境开启 debug** - 方便调试，生产环境关闭
8. **不要修改框架核心表** - 如 fa_user, fa_auth_rule 等

## 官方资源

- 官网：https://www.fastadmin.net
- 文档：https://doc.fastadmin.net
- 下载：https://www.fastadmin.net/download.html
- 插件市场：https://www.fastadmin.net/store.html
- 问答社区：https://ask.fastadmin.net
- Gitee：https://gitee.com/fastadminnet/fastadmin
- GitHub：https://github.com/karsonzhang/fastadmin