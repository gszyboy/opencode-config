# FastAdmin 命令行参考

FastAdmin 基于 ThinkPHP 的命令行功能，扩展了一系列便捷的 CLI 命令。
所有命令需在 FastAdmin 根目录（think 文件所在目录）执行。

---

## 一键生成 CRUD

**命令：** `php think crud`

### 参数列表

| 参数 | 简写 | 说明 | 示例 |
|------|------|------|------|
| `--table` | `-t` | **必填** 表名（带不带前缀均可） | `-t test` |
| `--controller` | `-c` | 控制器名，默认自动解析 | `-c Test` |
| `--model` | `-m` | 模型名，默认自动解析 | `-m Test` |
| `--fields` | `-i` | 列表可见字段，默认全部 | `-i "id,name,status"` |
| `--force` | `-f` | 强制覆盖已有文件 | `-f 1` |
| `--local` | `-l` | 本地模型(1)或公共模型(0) | `-l 0` |
| `--relation` | `-r` | 关联模型表名 | `-r category` |
| `--relationmodel` | `-e` | 关联模型名 | `-e Category` |
| `--relationforeignkey` | `-k` | 外键字段 | `-k category_id` |
| `--relationprimarykey` | `-p` | 关联表主键 | `-p id` |
| `--relationfields` | `-s` | 关联表显示字段 | `-s "id,name"` |
| `--relationmode` | `-o` | 关联模式: hasone/belongsto/hasmany | `-o belongsto` |
| `--delete` | `-d` | 删除模式，删除生成的文件 | `-d 1` |
| `--menu` | `-u` | 同时生成菜单 | `-u 1` |
| `--db` | | 多数据库配置 key | `--db=db2` |
| `--setcheckboxsuffix` | | 复选框字段后缀 | `--setcheckboxsuffix=list` |
| `--enumradiosuffix` | | 单选框字段后缀 | `--enumradiosuffix=type` |
| `--imagefield` | | 图片上传字段后缀 | `--imagefield=image` |
| `--filefield` | | 文件上传字段后缀 | `--filefield=file` |
| `--intdatesuffix` | | 日期字段后缀 | `--intdatesuffix=time` |
| `--switchsuffix` | | 开关字段后缀 | `--switchsuffix=switch` |
| `--citysuffix` | | 城市选择字段后缀 | `--citysuffix=city` |
| `--selectpagesuffix` | | Selectpage 字段后缀 | `--selectpagesuffix=page` |
| `--ignorefields` | | 排除字段 | `--ignorefields=content` |
| `--editorclass` | | 富文本字段后缀 | `--editorclass=editor` |
| `--headingfilterfield` | | 筛选选项卡字段 | `--headingfilterfield=status` |
| `--sortfield` | | 排序字段 | `--sortfield=weigh` |

### 常用示例

```bash
# 基础生成
php think crud -t test

# 生成并创建菜单
php think crud -t test -u 1

# 删除生成的文件
php think crud -t test -d 1

# 自定义控制器名（下划线表名）
php think crud -t test_log -c testlog

# 二级目录
php think crud -t test -c mydir/test

# 单关联模型
php think crud -t test -r category -k category_id -p id

# 多关联模型
php think crud -t test \
  --relation=category --relation=admin \
  --relationforeignkey=category_id --relationforeignkey=admin_id

# 多数据库
php think crud -t test --db=v_phealth_db2

# 自定义组件后缀
php think crud -t test \
  --setcheckboxsuffix=list \
  --imagefield=image \
  --filefield=file
```

---

## 一键生成菜单

**命令：** `php think menu`

### 参数

| 参数 | 简写 | 说明 | 示例 |
|------|------|------|------|
| `--controller` | `-c` | **必填** 控制器名或 `all-controller` | `-c test` |
| `--delete` | `-d` | 删除模式 | `-d 1` |
| `--force` | `-f` | 强制覆盖 | `-f 1` |

### 示例

```bash
# 生成指定控制器菜单
php think menu -c test

# 生成二级目录菜单
php think menu -c mydir/test

# 删除菜单
php think menu -c test -d 1

# 生成所有控制器菜单（谨慎！先备份）
php think menu -c all-controller
```

---

## 一键压缩打包

**命令：** `php think min`

### 参数

| 参数 | 简写 | 说明 | 示例 |
|------|------|------|------|
| `--module` | `-m` | 模块: all/backend/frontend | `-m all` |
| `--resource` | `-r` | 资源: all/js/css | `-r all` |
| `--optimize` | `-o` | 优化器: uglify | `-o uglify` |
| `--verbose` | `-v` | 显示详细信息 | `-vvv` |

### 示例

```bash
# 打包前后台所有资源
php think min -m all -r all

# 仅打包后台
php think min -m backend -r all

# 仅打包 JS
php think min -m all -r js

# 使用 uglify
php think min -m backend -r js -o uglify

# 调试模式查看错误
php think min -m all -r all -vvv
```

---

## 一键生成 API 文档

**命令：** `php think api`

### 参数

| 参数 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| `--url` | `-u` | API 请求域名 | "" |
| `--module` | `-m` | 模块名 | "api" |
| `--addon` | `-a` | 插件标识 | "" |
| `--output` | `-o` | 输出文件 | "api.html" |
| `--template` | `-e` | 模板文件 | "index.html" |
| `--force` | `-f` | 覆盖模式 | false |
| `--title` | `-t` | 文档标题 | "FastAdmin" |
| `--class` | `-c` | 扩展类 | "" |
| `--language` | `-l` | 语言 | "zh-cn" |
| `--controller` | `-r` | 指定控制器 | 所有 |

### 示例

```bash
# 生成所有 API 文档
php think api --force=true

# 指定域名
php think api -u https://api.example.com --force=true

# 自定义输出文件
php think api -o myapi.html --force=true

# 生成指定控制器
php think api -r Demo --force=true

# 生成插件 API 文档
php think api -a cms -o cmsapi.html --force=true
```

---

## 一键管理插件

**命令：** `php think addon`

### 参数

| 参数 | 简写 | 说明 | 示例 |
|------|------|------|------|
| `--name` | `-a` | **必填** 插件标识 | `-a example` |
| `--action` | `-c` | **必填** 操作类型 | `-c create` |

### 操作类型

| 操作 | 说明 |
|------|------|
| `create` | 创建本地插件 |
| `refresh` | 刷新插件缓存 |
| `uninstall` | 卸载插件 |
| `enable` | 启用插件 |
| `disable` | 禁用插件 |
| `package` | 打包为 zip |
| `move` | 将 CRUD 文件移动到插件目录 |

### 示例

```bash
# 创建插件
php think addon -a myaddon -c create

# 启用/禁用/卸载
php think addon -a example -c enable
php think addon -a example -c disable
php think addon -a example -c uninstall

# 刷新缓存
php think addon -a example -c refresh

# 打包
php think addon -a example -c package

# 移动 CRUD 文件到插件
php think addon -a example -c move
```

---

## 一键安装 FastAdmin

**命令：** `php think install`

### 参数

| 参数 | 简写 | 说明 | 示例 |
|------|------|------|------|
| `--hostname` | `-a` | 数据库地址 | `-a 127.0.0.1` |
| `--username` | `-u` | 数据库用户名 | `-u root` |
| `--password` | `-p` | 数据库密码 | `-p 123456` |
| `--database` | `-d` | 数据库名 | `-d dbname` |
| `--prefix` | `-r` | 表前缀 | `-r fa_` |
| `--force` | `-f` | 强制重新安装 | `-f 1` |

### 示例

```bash
# 交互式安装
php think install

# 全自动安装
php think install -a 127.0.0.1 -u root -p 123456 -d fastadmin -r fa_

# 强制重新安装
php think install -f 1
```

---

## 查看帮助

每个命令都支持 `--help` 查看详细参数：

```bash
php think crud --help
php think menu --help
php think min --help
php think api --help
php think addon --help
php think install --help
```