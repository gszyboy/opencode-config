# Pure Admin 布局、菜单和路由使用指南

## 概述

本技能基于 Pure Admin 官方文档 (https://pure-admin.cn) 总结，用于正确配置和使用 Pure Admin 框架的布局系统、菜单系统和路由系统。

## 1. 布局系统

### 1.1 布局模式

Pure Admin 支持 4 种布局模式：

| 模式 | 说明 | 配置 |
|------|------|------|
| **左侧菜单模式** (vertical) | 经典侧边栏布局 | `"Layout": "vertical"` |
| **顶部菜单模式** (horizontal) | 顶部导航栏 | `"Layout": "horizontal"` |
| **混合菜单模式** | 左侧+顶部混合 | 需特殊配置 |
| **双栏菜单模式** | 仅 Max 版支持 | 需 Max 版本 |

### 1.2 布局配置

在 `public/platform-config.json` 中配置：

```json
{
  "Layout": "vertical",
  "Theme": "light",
  "DarkMode": false,
  "FixedHeader": true,
  "HiddenSideBar": false,
  "ShowLogo": true,
  "SidebarStatus": true
}
```

### 1.3 关键规则

- **Layout 组件自动处理**: 父级路由（有 children 的）不需要指定 `component: "Layout"`，Pure Admin 会自动分配
- **iframe 内嵌**: 使用 `frameSrc` 属性指定 iframe 地址
- **外链**: 将 URL 写在 `name` 属性中

## 2. 路由系统

### 2.1 路由类型

| 类型 | 来源 | 文件位置 |
|------|------|----------|
| **静态路由** | 前端硬编码 | `src/router/modules/*.ts` |
| **动态路由** | 后端 API 返回 | 通过 `/get-async-routes` 获取 |
| **基础路由** | 系统必需 | `home.ts`, `error.ts`, `remaining.ts` |

### 2.2 动态路由核心机制

#### 2.2.1 路由解析流程

```
1. 后端返回路由 JSON
2. 前端调用 addAsyncRoutes() 处理
3. 匹配 component/path 到实际 .vue 文件
4. 自动添加 Layout 组件到父级
5. 自动设置 redirect 和 name
6. 添加到 Vue Router
```

#### 2.2.2 文件匹配规则

```typescript
// 前端 globs 匹配所有视图文件
const modulesRoutes = import.meta.glob("/src/views/**/*.{vue,tsx}");

// 匹配优先级：
// 1. 如果后端传 component，优先匹配 component 路径
// 2. 如果后端不传 component，path 必须与实际文件路径一致
// 3. component 值前不需要加 /，对应 views 目录下的路径
```

#### 2.2.3 动态路由处理函数

```typescript
function addAsyncRoutes(arrRoutes: Array<RouteRecordRaw>) {
  const modulesRoutesKeys = Object.keys(modulesRoutes);
  
  arrRoutes.forEach((v: RouteRecordRaw) => {
    // 标识为后端路由
    v.meta.backstage = true;
    
    // 自动设置 redirect（如果未指定）
    if (v?.children && v.children.length && !v.redirect)
      v.redirect = v.children[0].path;
    
    // 自动设置父级 name（避免与子级重复）
    if (v?.children && v.children.length && !v.name)
      v.name = (v.children[0].name as string) + "Parent";
    
    // 处理 iframe
    if (v.meta?.frameSrc) {
      v.component = IFrame;
    } else {
      // 优先匹配 component，否则匹配 path
      const index = v?.component
        ? modulesRoutesKeys.findIndex(ev => ev.includes(v.component as any))
        : modulesRoutesKeys.findIndex(ev => ev.includes(v.path));
      v.component = modulesRoutes[modulesRoutesKeys[index]];
    }
    
    // 递归处理子路由
    if (v?.children && v.children.length) {
      addAsyncRoutes(v.children);
    }
  });
}
```

### 2.3 路由配置规范

#### 2.3.1 一级菜单（无子菜单）

```typescript
// 模式1：只传 path（path 必须匹配实际文件路径）
{
  path: "/fighting",
  meta: { title: "加油" },
  children: [
    {
      path: "/fighting/index",
      name: "Fighting",
      meta: { title: "加油" }
    }
  ]
}

// 模式2：传 path + component（path 可任意，component 必须匹配文件）
{
  path: "/fighting",
  meta: { title: "加油" },
  children: [
    {
      path: "/anything",  // 可任意
      component: "fighting/index",  // 对应 src/views/fighting/index.vue
      name: "Fighting",
      meta: { title: "加油" }
    }
  ]
}
```

#### 2.3.2 二级菜单

**模式1：单个子菜单（显示父级）**

```typescript
{
  path: "/fighting",
  meta: { title: "励志" },
  children: [
    {
      path: "/fighting/index",
      name: "Fighting",
      meta: {
        title: "加油",
        showParent: true  // 关键：显示父级菜单
      }
    }
  ]
}
```

**模式2：多个子菜单**

```typescript
{
  path: "/fighting",
  meta: { title: "励志" },
  children: [
    {
      path: "/fighting/index",
      name: "Fighting",
      meta: { title: "加油" }
    },
    {
      path: "/fighting/effort",
      name: "Effort",
      meta: { title: "努力" }
    }
  ]
}
```

#### 2.3.3 三级及以上菜单

```typescript
{
  path: "/nested",
  meta: { title: "多级菜单" },
  children: [
    {
      path: "/nested/menu1",
      meta: { title: "菜单1" },
      children: [
        {
          path: "/nested/menu1/menu1-1/index",
          name: "Menu1-1",
          meta: {
            title: "菜单1-1",
            showParent: true  // 只有一个子菜单时显示父级
          }
        }
      ]
    }
  ]
}
```

### 2.4 路由 Meta 属性

| 属性 | 说明 | 类型 |
|------|------|------|
| `title` | 菜单名称（支持国际化） | `string` |
| `icon` | 菜单图标 | `string \| FunctionalComponent` |
| `showLink` | 是否在菜单显示 | `boolean` |
| `showParent` | 是否显示父级菜单（单个子菜单时） | `boolean` |
| `rank` | 菜单排序（值越大越靠后） | `number` |
| `roles` | 页面级别权限 | `Array<string>` |
| `auths` | 按钮级别权限 | `Array<string>` |
| `keepAlive` | 是否缓存页面 | `boolean` |
| `frameSrc` | iframe 地址 | `string` |
| `hiddenTag` | 禁止添加到标签页 | `boolean` |
| `activePath` | 激活指定菜单路径 | `string` |
| `transition` | 页面动画配置 | `object` |

### 2.5 关键注意事项

#### ❌ 禁止事项

1. **不要给父级路由设置 `component: "Layout"`**
   - Pure Admin 会自动处理
   - 手动设置会导致 `parentNode` 错误

2. **默认子路由（path: ""）不要设置 redirect**
   - 当子路由 path 为空字符串时，Vue Router 自动将其作为默认子路由
   - 如果父级再设置 redirect 会导致无限循环

3. **不要删除必需的路由文件**
   - `src/router/modules/home.ts`
   - `src/router/modules/error.ts`
   - `src/router/modules/remaining.ts`

#### ✅ 最佳实践

1. **路由 name 必须唯一**
   - 且必须与页面对应的 `defineOptions({ name: "xxx" })` 保持一致
   - 页面缓存 keepAlive 依赖此一致性

2. **推荐使用后端的 component 模式**
   - 后端返回 `component: "path/to/page"`
   - 前端 `path` 可任意（只需以 `/` 开头）
   - 更灵活，解耦前后端路径

3. **redirect 自动处理**
   - 动态路由不需要手动写 redirect
   - Pure Admin 自动取第一个子路由的 path

4. **静态路由作为 fallback**
   - 保留关键静态路由（home, error, remaining）
   - 业务路由优先使用动态路由

## 3. 菜单系统

### 3.1 菜单生成流程

```
静态路由 modules → 合并 → 权限过滤 → 菜单渲染
动态路由 API     →
```

### 3.2 菜单排序

使用 `rank` 字段控制排序：

```typescript
{
  path: "/content",
  meta: {
    title: "内容管理",
    rank: 1  // 值越小越靠前
  },
  children: [...]
}
```

### 3.3 菜单图标

```typescript
{
  meta: {
    title: "内容管理",
    icon: "ep:document"  // 使用 Iconify 图标
  }
}
```

## 4. 动态路由 API 规范

### 4.1 后端返回格式

```typescript
// 成功响应
{
  "success": true,
  "data": [
    {
      "path": "/content",
      "meta": {
        "title": "内容管理",
        "icon": "ep:document",
        "rank": 1
      },
      "children": [
        {
          "path": "/content/articles",
          "component": "admin/articles/index",  // 对应 src/views/admin/articles/index.vue
          "name": "AdminArticles",
          "meta": {
            "title": "文章管理"
          }
        }
      ]
    }
  ]
}
```

### 4.2 路由匹配检查清单

- [ ] 后端返回的 `component` 路径对应 `src/views/` 下的实际文件
- [ ] 父级路由不包含 `component: "Layout"`
- [ ] 默认子路由（path: `""`）的父级没有 `redirect` 指向自身
- [ ] 所有路由的 `name` 唯一且不重复
- [ ] 页面组件的 `defineOptions({ name })` 与路由 name 一致
- [ ] API 路径为 `/api/v1/get-async-routes`

## 5. 常见问题排查

### 5.1 菜单不显示

**原因**: 动态路由未正确加载
**排查**:
1. 检查 `/api/v1/get-async-routes` 是否返回正确数据
2. 检查 `component` 路径是否匹配实际文件
3. 检查浏览器控制台是否有路由匹配错误

### 5.2 404 错误

**原因**: 路由匹配失败
**排查**:
1. 检查 `path` 或 `component` 是否正确
2. 检查是否有 `redirect` 循环
3. 检查文件是否存在于 `src/views/` 目录

### 5.3 页面空白

**原因**: Layout 组件加载失败
**排查**:
1. 确保父级路由没有手动设置 `component: "Layout"`
2. 检查 Pure Admin 是否正确初始化

### 5.4 动态路由刷新后消失

**原因**: 未正确缓存
**解决**:
- 开发环境: `CachingAsyncRoutes: false`（每次刷新重新获取）
- 生产环境: `CachingAsyncRoutes: true`（缓存到 sessionStorage）

## 6. 完整示例

### 6.1 后端动态路由配置

```python
# backend/src/app/api/v1/routes.py
@router.get("/get-async-routes")
async def get_async_routes():
    return {
        "success": True,
        "data": [
            {
                "path": "/content",
                "meta": {
                    "title": "内容管理",
                    "icon": "ep:document",
                    "rank": 1
                },
                "children": [
                    {
                        "path": "/content/articles",
                        "component": "admin/articles/index",
                        "name": "AdminArticles",
                        "meta": { "title": "文章管理" }
                    },
                    {
                        "path": "/content/categories",
                        "component": "admin/categories/index",
                        "name": "AdminCategories",
                        "meta": { "title": "分类管理" }
                    }
                ]
            }
        ]
    }
```

### 6.2 前端页面组件

```vue
<!-- src/views/admin/articles/index.vue -->
<script setup lang="ts">
defineOptions({
  name: "AdminArticles"  // 必须与路由 name 一致
});
</script>

<template>
  <div>文章管理页面</div>
</template>
```

## 7. 参考资源

- **官方文档**: https://pure-admin.cn
- **布局文档**: https://pure-admin.cn/pages/layout/
- **路由文档**: https://pure-admin.cn/pages/routerMenu/
- **GitHub**: https://github.com/pure-admin/vue-pure-admin
- **在线预览**: https://pure-admin.github.io/vue-pure-admin
