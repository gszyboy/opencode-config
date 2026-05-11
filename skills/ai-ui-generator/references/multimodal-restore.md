# 多模态还原

## UI 转前端 Prompt

当需要将 UI 截图转换为前端代码时，使用以下 Prompt 模板：

```text
请严格参考这张 UI 截图。

要求：
1. 完整还原布局
2. 不允许擅自修改设计
3. 精确还原：
   - spacing
   - color
   - typography
   - border radius
   - shadows
4. 使用组件化结构
5. 保持响应式
6. 输出完整代码
7. 使用现代前端规范
8. 不允许省略任何模块
9. 保持真实互联网产品风格
10. 所有 UI 必须 frontend-friendly
```

## 推荐技术栈

### React 技术栈

```text
React
TailwindCSS
shadcn/ui
lucide-react
```

### Vue 技术栈

```text
Vue3
TailwindCSS
NaiveUI
Pinia
```

### 小程序技术栈

```text
Taro
UniApp
NutUI
TailwindCSS
```

### 纯 HTML/CSS

```text
HTML5
CSS3
Vanilla JavaScript
TailwindCSS
```

## 还原标准

### 精确度要求

- 布局：100% 还原结构
- 颜色：误差 < 5%
- 间距：误差 < 2px
- 字体：大小、字重、行高精确匹配
- 圆角：精确匹配
- 阴影：方向、模糊、颜色精确匹配

### 代码质量要求

- 语义化 HTML
- BEM 或 Tailwind 命名规范
- 组件化结构
- 响应式设计
- 无障碍支持
- 性能优化
