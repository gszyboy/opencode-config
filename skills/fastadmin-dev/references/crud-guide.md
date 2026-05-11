# CRUD 生成详解

FastAdmin 最强大的功能之一是根据数据库表结构一键生成完整的后台 CRUD 代码。

## 生成原理

FastAdmin 通过分析数据库表的：
1. **字段类型** - 决定表单组件类型
2. **字段注释** - 生成语言包和标签文本
3. **表注释** - 生成菜单名称
4. **字段后缀** - 自动匹配组件（见下表）

## 字段后缀与组件映射

| 后缀 | 生成的组件 | 示例字段名 |
|------|-----------|-----------|
| `_list`, `_data` | 复选框 | `status_list`, `tag_data` |
| `_image`, `_img` | 图片上传 | `avatar_image`, `logo_img` |
| `_file` | 文件上传 | `attachment_file` |
| `_time`, `_date` | 日期时间选择器 | `createtime`, `publish_date` |
| `_switch` | 开关组件 | `is_switch` |
| `_city` | 城市选择器 | `address_city` |
| `_selectpage` | SelectPage 下拉 | `user_selectpage` |
| `_editor` | 富文本编辑器 | `content_editor` |

## 数据库设计最佳实践

### 标准表结构模板

```sql
CREATE TABLE `fa_article` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `category_id` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '分类ID',
  `title` varchar(255) NOT NULL DEFAULT '' COMMENT '标题',
  `content` text COMMENT '内容',
  `image` varchar(255) NOT NULL DEFAULT '' COMMENT '封面图',
  `author` varchar(50) NOT NULL DEFAULT '' COMMENT '作者',
  `status` enum('normal','hidden','deleted') NOT NULL DEFAULT 'normal' COMMENT '状态',
  `weigh` int(10) NOT NULL DEFAULT '0' COMMENT '权重',
  `createtime` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '创建时间',
  `updatetime` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '更新时间',
  `deletetime` int(10) unsigned DEFAULT NULL COMMENT '删除时间',
  PRIMARY KEY (`id`),
  KEY `category_id` (`category_id`),
  KEY `status` (`status`),
  KEY `weigh` (`weigh`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='文章表';
```

### 关键设计要点

1. **必须有主键** - 且只能有一个主键，不支持复合主键
2. **deletetime 默认 NULL** - 这样才能启用回收站功能
3. **字段注释必须写** - 这是生成语言包的基础
4. **表注释必须写** - 用于生成菜单名称
5. **status 字段** - 使用 enum 类型，值为 normal/hidden/deleted
6. **weigh 字段** - 用于后台拖拽排序
7. **createtime/updatetime** - 自动维护的时间戳字段

### 常用字段类型对应组件

| 字段类型 | 生成的表单组件 |
|---------|--------------|
| `varchar` | 文本输入框 |
| `text` | 文本域 |
| `int` | 数字输入框 |
| `decimal/float/double` | 数字输入框（含小数） |
| `enum` | 单选框/下拉框 |
| `set` | 复选框 |
| `datetime/timestamp` | 日期时间选择器 |
| `date` | 日期选择器 |

## 关联模型配置

### 一对一关联 (belongsto)

```bash
# 基础关联
php think crud -t article -r category -k category_id -p id

# 完整参数
php think crud -t article \
  -r category \
  -k category_id \
  -p id \
  -s "id,name" \
  -o belongsto
```

### 多关联模型

```bash
php think crud -t order \
  --relation=user --relation=product \
  --relationforeignkey=user_id --relationforeignkey=product_id \
  --relationprimarykey=id --relationprimarykey=id
```

### 关联显示效果

生成后，列表页会自动显示关联表的数据：
- 关联字段默认在列表中显示为关联表的名称字段
- 添加/编辑表单中会生成 SelectPage 下拉选择组件
- 支持关联表的搜索筛选

## 自定义生成配置

### 排除字段

```bash
# 排除 content 字段不在列表显示
php think crud -t article --ignorefields=content

# 排除多个字段
php think crud -t article --ignorefields="content,remark"
```

### 指定可见字段

```bash
# 列表只显示指定字段
php think crud -t article -i "id,title,category_id,status,createtime"
```

### 自定义组件后缀

```bash
# 为特定字段指定组件
php think crud -t article \
  --setcheckboxsuffix=tags \
  --imagefield=cover \
  --filefield=attachment \
  --editorclass=detail
```

## 生成后的二次开发

### 控制器 (Controller)

生成的控制器包含标准方法：
- `index()` - 列表页
- `add()` - 添加页
- `edit($ids)` - 编辑页
- `del($ids)` - 删除
- `destroy($ids)` - 真实删除
- `restore($ids)` - 还原
- `recyclebin()` - 回收站
- `multi($ids)` - 批量更新

### 模型 (Model)

生成的模型包含：
- 自动时间戳配置
- 软删除配置（如有 deletetime 字段）
- 关联模型方法
- 自定义属性获取器

### 验证器 (Validate)

根据字段属性自动生成：
- 必填验证（NOT NULL 字段）
- 类型验证
- 长度验证
- 唯一验证（unique 索引）

### 视图 (View)

生成的视图文件：
- `index.html` - 列表页（含搜索、表格、工具栏）
- `add.html` - 添加表单
- `edit.html` - 编辑表单
- `recyclebin.html` - 回收站列表

### JS 文件

`public/assets/js/backend/article.js` 包含：
- 表格初始化配置
- 事件绑定
- 表单验证
- 批量操作

## 常见问题

**Q: 为什么生成的表单组件不对？**
A: 检查字段类型和注释是否正确，必要时使用 `--setcheckboxsuffix` 等参数强制指定

**Q: 关联模型数据不显示？**
A: 确保外键字段名格式为 `模型名_id`，或手动指定 `-k` 参数

**Q: 如何添加自定义按钮？**
A: 在生成的 JS 文件中 `toolbar` 配置区域添加

**Q: 如何修改列表列的显示格式？**
A: 在控制器中使用 `->addColumns()` 方法的 `formatter` 参数

**Q: 生成后如何添加新字段？**
A: 修改数据库表结构后，使用 `-f 1` 强制重新生成，或手动修改各文件