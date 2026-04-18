---
name: design-region-extractor
description: |
  从指定区域/元素提取设计风格。输入目标网站 URL + 用户喜欢的具体区域描述，
  精确提取该区域的设计 tokens（颜色、字体、间距、阴影等）。
  触发方式：用户说"我喜欢这个按钮"、"提取这个区域"、"这个卡片好好看"、
  "仿照这个导航栏"、"像 xxx 网站的那个 xxx" 等。
  输出：该区域的精确设计规范 + 可直接应用的 CSS/Tailwind 代码。
  前置要求：需要 Playwright CLI 或 browser 工具。
triggers:
  - "^我喜欢.*这个"
  - "^提取.*区域"
  - "^这个.*好好看"
  - "^像.*那个"
  - "^仿照.*导航栏"
  - "^提取.*那个.*按钮"
  - "^分析.*这个.*区域"
  - "^提取.*那个.*样式"
---

# Design Region Extractor Skill

从网页的具体区域/元素提取设计风格。

## 核心价值

**你不需要会设计，也不需要会审查元素**。看到喜欢的按钮、卡片、导航栏，直接告诉我，我帮你：

1. 🎯 定位到你喜欢的那个具体元素
2. 📊 提取精确的设计数值
3. 💻 生成可直接用的代码

## 工作流程

```
用户描述喜欢的地方 → 我定位元素 → 精确提取 → 生成代码
```

## Step 1: 理解用户想要哪个区域

用户可能这样描述：

| 用户说 | 我的理解 |
|--------|----------|
| "我喜欢这个按钮" | 用户在页面上看到了一个喜欢的按钮 |
| "这个卡片好好看" | 某个产品卡片/文章卡片 |
| "仿照那个导航栏" | header 或 nav 导航区域 |
| "像 xxx 网站的那个 CTA 按钮" | 特定网站的特定区域 |
| "提取这个 hero section" | 首屏大区块 |

**如果是自己网站的元素**：告诉我 URL + 描述是哪个区域
**如果是参考其他网站**：给我 URL + 描述

### 如果用户给了截图

用户上传了截图并在上面标注了区域：

```
✅ 收到截图！
请告诉我：
1. 这个网站是什么 URL？（如果有）
2. 你圈出的区域是网站的哪个部分？（如：登录按钮、右侧卡片、顶部导航栏）
```

## Step 2: 定位元素

### 方式 A：用户提供选择器（最快）

如果用户知道元素的选择器：
```
playwright-cli open <url>
playwright-cli eval "
(function() {
  const el = document.querySelector('USER_PROVIDED_SELECTOR');
  if (!el) return { error: '元素未找到' };
  const cs = getComputedStyle(el);
  return JSON.stringify({
    backgroundColor: cs.backgroundColor,
    color: cs.color,
    fontSize: cs.fontSize,
    fontFamily: cs.fontFamily,
    fontWeight: cs.fontWeight,
    padding: cs.padding,
    margin: cs.margin,
    borderRadius: cs.borderRadius,
    boxShadow: cs.boxShadow,
    border: cs.border,
    display: cs.display,
    flexDirection: cs.flexDirection,
    alignItems: cs.alignItems,
    justifyContent: cs.justifyContent,
    gap: cs.gap,
    width: cs.width,
    height: cs.height
  }, null, 2);
})()
"
```

### 方式 B：用户提供 URL + 描述，我推断选择器

用户：`https://xxx.com 我喜欢那个蓝色的登录按钮`

```bash
playwright-cli open https://xxx.com
# 我先用快照看看页面结构，推断选择器
playwright-cli snapshot
```

然后我分析快照，结合用户描述（如"蓝色的登录按钮"），推断可能的选择器：
- `button[type="submit"]`
- `.login-btn`
- `#submit`
- `button:contains("登录")`

执行提取：

```bash
playwright-cli eval "
(function() {
  // 尝试多个可能的选择器
  const selectors = [
    'button[type=\"submit\"]',
    '.login-btn',
    '#submit',
    'button',
    '.btn-primary'
  ];
  
  for (const sel of selectors) {
    const el = document.querySelector(sel);
    if (el) {
      const cs = getComputedStyle(el);
      return JSON.stringify({
        selector: sel,
        found: true,
        styles: {
          backgroundColor: cs.backgroundColor,
          color: cs.color,
          fontSize: cs.fontSize,
          fontFamily: cs.fontFamily,
          fontWeight: cs.fontWeight,
          padding: cs.padding,
          borderRadius: cs.borderRadius,
          boxShadow: cs.boxShadow
        }
      }, null, 2);
    }
  }
  return { error: '未找到匹配的元素' };
})()
"
```

### 方式 C：用户上传截图 + URL，让我分析

1. 先用 Playwright 截图确认页面
2. 分析截图中的区域
3. 在页面上找到对应的元素
4. 执行提取

## Step 3: 精确提取设计 Tokens

对于找到的元素，执行完整提取：

```bash
playwright-cli eval "
(function() {
  const el = document.querySelector('SELECTOR');
  const cs = getComputedStyle(el);
  
  // 提取完整设计系统
  return {
    // 颜色（转换 HEX）
    colors: {
      background: cs.backgroundColor,
      color: cs.color,
      border: cs.borderColor
    },
    
    // 字体
    typography: {
      fontFamily: cs.fontFamily,
      fontSize: cs.fontSize,
      fontWeight: cs.fontWeight,
      lineHeight: cs.lineHeight
    },
    
    // 间距
    spacing: {
      padding: {
        top: cs.paddingTop,
        right: cs.paddingRight,
        bottom: cs.paddingBottom,
        left: cs.paddingLeft
      },
      margin: {
        top: cs.marginTop,
        right: cs.marginRight,
        bottom: cs.marginBottom,
        left: cs.marginLeft
      }
    },
    
    // 边框
    border: {
      radius: cs.borderRadius,
      width: cs.borderWidth,
      style: cs.borderStyle,
      color: cs.borderColor
    },
    
    // 阴影
    shadow: cs.boxShadow,
    
    // 布局
    layout: {
      display: cs.display,
      flexDirection: cs.flexDirection,
      alignItems: cs.alignItems,
      justifyContent: cs.justifyContent,
      gap: cs.gap
    },
    
    // 尺寸
    sizing: {
      width: cs.width,
      height: cs.height,
      maxWidth: cs.maxWidth
    }
  };
})()
"
```

## Step 4: 生成可应用的代码

根据提取的 tokens，生成代码：

### Tailwind 配置

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: '#HEX值',
        secondary: '#HEX值',
      },
      borderRadius: {
        'sm': 'Xpx',
        'md': 'Xpx',
      },
      boxShadow: {
        'card': 'X X X rgba(0,0,0,X)',
      }
    }
  }
}
```

### CSS 变量

```css
/* design-region.css */
.region-button {
  background-color: var(--color-primary);
  color: var(--color-text);
  font-size: var(--font-size-base);
  font-family: var(--font-family);
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-card);
}
```

## 输出格式

```
✅ 区域设计提取完成！

📍 目标区域：[用户描述]
🔍 选择器：[实际使用的选择器]

┌─────────────────────────────────────┐
│ 颜色                                │
├─────────────────────────────────────┤
│ Background: #HEX (rgb转HEX)         │
│ Color: #HEX                         │
│ Border: #HEX                        │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ 字体                                │
├─────────────────────────────────────┤
│ Font: PingFang SC, sans-serif       │
│ Size: 16px                          │
│ Weight: 600                         │
│ Line Height: 1.5                    │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ 间距                                │
├─────────────────────────────────────┤
│ Padding: 12px 24px                  │
│ Margin: 0 0 16px 0                  │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ 边框与阴影                          │
├─────────────────────────────────────┤
│ Border Radius: 8px                  │
│ Box Shadow: 0 4px 12px rgba(...)    │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ 布局                                │
├─────────────────────────────────────┤
│ Display: flex                        │
│ Flex Direction: row                 │
│ Align Items: center                 │
│ Gap: 12px                           │
└─────────────────────────────────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

已生成代码：
• Tailwind 配置片段
• CSS 变量文件
• 组件示例代码

你想把这个设计用到哪里？
1. 我的登录按钮
2. 我的卡片组件
3. 告诉我你想做什么
```

## 常见区域参考

### 按钮

```javascript
const buttonTokens = {
  backgroundColor: 'rgb(55, 95, 127)',   // 主色
  color: 'rgb(255, 255, 255)',          // 白色文字
  fontSize: '16px',
  fontWeight: '600',
  padding: '12px 24px',
  borderRadius: '8px',
  boxShadow: '0 4px 12px rgba(55, 95, 127, 0.3)'
}
```

### 卡片

```javascript
const cardTokens = {
  backgroundColor: 'rgb(255, 255, 255)',
  borderRadius: '12px',
  padding: '24px',
  boxShadow: '0 8px 32px rgba(0, 0, 0, 0.08)',
  border: '1px solid rgba(0, 0, 0, 0.06)'
}
```

### 导航栏

```javascript
const navTokens = {
  backgroundColor: 'rgb(255, 255, 255)',
  height: '64px',
  padding: '0 32px',
  boxShadow: '0 2px 8px rgba(0, 0, 0, 0.04)',
  borderBottom: '1px solid rgba(0, 0, 0, 0.06)'
}
```

## 注意事项

- **优先使用选择器**：告诉用户先在浏览器审查元素获取选择器，这样最准确
- **模糊描述时多尝试**：如果用户说"蓝色的按钮"，我会尝试多个蓝色相关的选择器
- **颜色转换**：如果需要 RGB 转 HEX，用 `rgb(55, 95, 127)` → `#375f7f`
- **保留精确值**：16px 就是 16px，不要四舍五入成 15px

## 适用场景

✅ **你喜欢某个网站的一个按钮，想用到自己项目**
✅ **看到一个好看的卡片设计，想参考样式**
✅ **喜欢某个导航栏的风格，想复制布局**
✅ **看到好的设计，想提取具体数值学习**

## 禁忌事项

- ❌ 不要猜测数值，必须获取实际 computed style
- ❌ 不要忽略 hover/active 状态，用户可能想了解不同状态
- ❌ 不要只说"提取完成"，必须生成可应用的代码
