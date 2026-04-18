---
name: clone-website
description: |
  网站克隆技能。输入任意 URL，自动逆向工程为目标网站的像素级克隆。
  触发方式：用户说 "clone <url>"、"逆向这个网站"、"仿制 <url>"、"把这个网站做成代码" 等。
  工作流程：截图分析 → 设计 token 提取 → 组件规范生成 → 并行构建 → Next.js 项目输出。
  适用于：网站迁移、源码恢复、学习现代网站实现方式。
  前置要求：需要浏览器自动化工具（Playwright CLI 或 browser 工具）。
triggers:
  - "^clone\\s+https?://"
  - "^逆向\\s+"
  - "^仿制\\s+"
  - "^把这个网站"
  - "^做个.*像.*一样的"
  - "^克隆\\s+"
  - "^clone-website\\s+"
---

# Clone Website Skill

逆向工程并重建任意网站为像素级克隆。

## 概述

给定一个目标 URL，自动完成：
1. 截图分析 + 设计 token 提取
2. 交互行为探测（滚动、点击、悬停）
3. 组件规范文档生成
4. 并行 AI 构建
5. 视觉 QA 对比

**输出**：Next.js + TypeScript + Tailwind CSS + shadcn/ui 项目

## ⚠️ 前置要求

**必须先检查浏览器自动化工具**。按以下优先级检查：

1. **Playwright CLI** - `playwright-cli open <url>`
2. **Browser MCP** - `skill_mcp(mcp_name="browser", tool_name="...")`
3. **其他浏览器工具**

如果没有任何浏览器工具可用，**立即告知用户**：
```
"网站克隆需要浏览器自动化工具。请先安装/配置以下之一：
- Playwright CLI: npm install -g playwright-cli
- Browserbase MCP
- 或确认你已配置的浏览器 MCP 工具"
```

## Step 1: 预检（Pre-Flight）

### 1.1 URL 验证
解析 `$ARGUMENTS` 为一个或多个 URL，验证格式有效。

### 1.2 环境检查
```
npm run build
```
确保 Next.js + shadcn/ui + Tailwind v4 脚手架已就绪。

### 1.3 目录准备
创建必要目录：
```
docs/research/
docs/research/components/
docs/design-references/
public/images/
public/videos/
public/seo/
scripts/
```

### 1.4 项目设置
如果项目未初始化，告知用户先执行：
```bash
git clone https://github.com/JCodesMore/ai-website-cloner-template.git my-clone
cd my-clone
npm install
```

## Step 2: 侦察阶段（Reconnaissance）

**必须用 Playwright CLI 访问目标 URL**。

### 2.1 截图
- **桌面端**：1440px 整页截图
- **移动端**：390px 整页截图
- 保存到 `docs/design-references/`

```bash
playwright-cli open <url>
playwright-cli resize 1440 900
playwright-cli screenshot --filename=desktop.png
playwright-cli resize 390 844
playwright-cli screenshot --filename=mobile.png
playwright-cli close
```

### 2.2 全局信息提取

**字体**：
- 检查 `<link>` 标签中的 Google Fonts
- 用 `playwright-cli eval` 提取关键元素的 font-family
- 记录：family, weight, style

**颜色**：
- 提取页面 CSS 变量中的颜色
- 更新 `src/app/globals.css` 的 `:root` 和 `.dark`

**Favicon & Meta**：
- 下载 favicons, apple-touch-icons, OG images 到 `public/seo/`
- 更新 `layout.tsx` metadata

**全局交互模式**：
- 检查自定义滚动条
- 检查 scroll-snap
- 检查 smooth scroll 库（Lenis: `.lenis` class）
- 检查全局 keyframe 动画

### 2.3 强制交互探测

**滚动扫描**：
```bash
playwright-cli mousewheel 0 100  # 慢速滚动，记录 header 变化
```

**点击扫描**：
```bash
playwright-cli click <element-ref>
playwright-cli snapshot  # 记录行为
```

**悬停扫描**：
```bash
playwright-cli hover <element-ref>
# 记录 hover 状态的颜色/阴影/缩放变化
```

**响应式扫描**：
```bash
playwright-cli resize 1440 900
playwright-cli snapshot
playwright-cli resize 768 1024
playwright-cli snapshot
playwright-cli resize 390 844
playwright-cli snapshot
```

### 2.4 页面拓扑
映射页面每个区块：
- 视觉顺序
- fixed/sticky vs flow content
- z-index 层
- 区块间的交互模式

## Step 3: 基础构建（Foundation Build）

**按顺序执行，自己完成不分派**：

### 3.1 更新字体
在 `layout.tsx` 配置目标站点的实际字体

### 3.2 更新全局 CSS
在 `globals.css` 配置：
- 颜色 tokens
- 间距值
- 关键帧动画
- 全局滚动行为

### 3.3 创建类型定义
在 `src/types/` 创建 TypeScript interfaces

### 3.4 提取 SVG 图标
查找所有 inline `<svg>`，去重后保存为 React 组件到 `src/components/icons.tsx`

### 3.5 下载资源
写 Node.js 脚本 `scripts/download-assets.mjs`：
```javascript
// 发现所有资源
const assets = {
  images: [...document.querySelectorAll('img')].map(img => ({
    src: img.src,
    alt: img.alt,
    width: img.naturalWidth,
    height: img.naturalHeight
  })),
  videos: [...document.querySelectorAll('video')].map(v => ({
    src: v.src,
    poster: v.poster
  })),
  backgroundImages: [...document.querySelectorAll('*')].filter(el => {
    const bg = getComputedStyle(el).backgroundImage;
    return bg && bg !== 'none';
  })
};
```
并行下载到 `public/`（最多 4 个并发）

### 3.6 验证
```bash
npm run build
```

## Step 4: 组件规范与构建

**核心循环**：提取 → 写规范 → 分派 builder

### 4.1 提取

每个区块需要：
1. **截图**：滚动到区块，截取视口截图
2. **CSS 提取**：用 `playwright-cli eval` 获取精确值
3. **多状态提取**：hover/active/scroll 状态都记录
4. **实际内容**：textContent 提取所有文本
5. **资源识别**：该区块使用的图片/图标

**提取脚本**：
```bash
playwright-cli eval "
(function(selector) {
  const el = document.querySelector(selector);
  if (!el) return JSON.stringify({ error: 'Element not found: ' + selector });
  const props = [
    'fontSize','fontWeight','fontFamily','lineHeight','letterSpacing','color',
    'backgroundColor','background','padding','margin','width','height',
    'display','flexDirection','justifyContent','alignItems','gap',
    'borderRadius','border','boxShadow','position','top','right','bottom','left','zIndex',
    'opacity','transform','transition','cursor'
  ];
  function extractStyles(element) {
    const cs = getComputedStyle(element);
    const styles = {};
    props.forEach(p => {
      const v = cs[p];
      if (v && v !== 'none' && v !== 'normal' && v !== 'auto' && v !== '0px')
        styles[p] = v;
    });
    return styles;
  }
  function walk(element, depth) {
    if (depth > 4) return null;
    const children = [...element.children];
    return {
      tag: element.tagName.toLowerCase(),
      classes: element.className?.toString().split(' ').slice(0, 5).join(' '),
      text: element.childNodes.length === 1 && element.childNodes[0].nodeType === 3
        ? element.textContent.trim().slice(0, 200) : null,
      styles: extractStyles(element),
      images: element.tagName === 'IMG' ? { src: element.src, alt: element.alt } : null,
      childCount: children.length,
      children: children.slice(0, 20).map(c => walk(c, depth + 1)).filter(Boolean)
    };
  }
  return JSON.stringify(walk(el, 0), null, 2);
})('SELECTOR')
"
```

### 4.2 识别交互模型

**在写规范前必须回答**：这个区块是点击驱动还是滚动驱动？

判断方法：
1. **先滚动**：观察内容是否自动变化
2. **如有变化**：是 scroll-driven，记录 IntersectionObserver 或 scroll 监听
3. **如无变化**：再测试点击/悬停

### 4.3 写规范文件

**路径**：`docs/research/components/<component-name>.spec.md`

**模板**：
```markdown
# <ComponentName> 规范

## 概述
- **目标文件**：`src/components/<ComponentName>.tsx`
- **截图**：`docs/design-references/<screenshot-name>.png`
- **交互模型**：<static | click-driven | scroll-driven | hover-driven>

## DOM 结构
<描述元素层级关系>

## 精确 CSS 值（来自 getComputedStyle）

### 容器
- display: ...
- padding: ...
- maxWidth: ...

### 子元素
...

## 状态与行为

### <状态名称，如 "滚动后">
- **触发**：<精确机制>
- **状态 A（触发前）**：...
- **状态 B（触发后）**：...
- **过渡**：transition: ...

### Hover 状态
- **元素**：<property>: <before> → <after>

## 内容（逐字复制）
<所有文本内容>

## 响应式行为
- **桌面 (1440px)**：...
- **平板 (768px)**：...
- **移动 (390px)**：...

## 资源
- 背景图：`public/images/<file>.webp`
- 图标：`<IconName>` from icons.tsx
```

### 4.4 分派 Builder

**简单区块**（1-2 个子组件）：一个 builder

**复杂区块**（3+ 个子组件）：拆分，每个子组件一个 builder

**每个 builder 收到**：
- 规范文件完整内容（内联在 prompt 中）
- 区块截图路径
- 共享组件信息（icons.tsx, cn(), shadcn primitives）
- 目标文件路径
- 验证指令：`npx tsc --noEmit`

### 4.5 合并

builder 完成后：
- 合并到 main
- 验证：`npm run build`
- 如有类型错误立即修复

## Step 5: 页面组装

在 `src/app/page.tsx`：
- 导入所有 section 组件
- 实现页面级布局（scroll containers, sticky positioning, z-index）
- 连接实际内容到组件 props
- 实现页面级行为（scroll snap, 动画, 过渡）

## Step 6: 视觉 QA

**必须执行**：
1. 并排对比原站和克隆站
2. 桌面端 (1440px) 和移动端 (390px) 各检查一遍
3. 测试所有交互：滚动、点击、悬停
4. 如有差异：
   - 规范文件错了 → 重新提取，修复组件
   - builder 错了 → 直接修复组件

## 输出格式

克隆完成后报告：
```
✅ 克隆完成
- 总区块数：X
- 组件数：X
- 规范文件：X
- 下载资源：X 张图片, X 个视频
- 构建状态：✅/❌
- 视觉 QA：通过/有 X 处差异
```

## ⚠️ 禁忌事项

- **不要猜测 CSS 值**：使用 `getComputedStyle()` 精确提取
- **不要遗漏 overlay 图片**：检查每个容器的完整 DOM 树
- **不要用点击驱动实现滚动驱动的交互**
- **不要跳过规范文件**：每个组件必须有规范
- **不要让 builder 做太多**：规范超过 ~150 行说明需要拆分
- **不要近似**：16px 和 15.8px 不一样！
- **不要跳过响应式测试**：必须在 1440px, 768px, 390px 都测试

## 适用场景

✅ **适合**：
- 从 WordPress/Webflow/Squarespace 迁移到你自己的站点
- 源码丢失的站点重建
- 学习现代网站的布局/动画/响应式实现

❌ **不适合**：
- 钓鱼或冒充
- 侵犯商标/版权
- 违反服务条款的站点
