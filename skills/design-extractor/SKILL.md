---
name: design-extractor
description: |
  设计元素提取技能。输入任意网站 URL，提取设计风格（颜色、字体、间距、布局、组件），
  生成设计规范文档，并应用到你的项目中。
  触发方式：用户说 "分析这个网站"、"提取设计风格"、"这个网站好好看"、"仿照这个设计"、
  "像 xxx 那种风格"、"设计参考 <url>" 等。
  输出：DESIGN.md 格式的设计规范 + 可直接应用的 CSS/Tailwind 代码。
  前置要求：需要浏览器自动化工具（Playwright CLI 或 browser 工具）。
triggers:
  - "^分析\\s+https?://"
  - "^提取.*设计"
  - "^这个网站"
  - "^像.*那种风格"
  - "^仿照.*设计"
  - "^设计参考\\s+https?://"
  - "^参考\\s+https?://"
  - "^抄\\s+https?://"
  - "^看看.*的设计"
  - "^学习.*设计"
---

# Design Extractor Skill

从任意网站提取设计风格，生成可应用的设计规范。

## 核心价值

**你不需要会设计**。看到喜欢的网站，只需要把 URL 给我，我帮你：
1. 🔍 分析网站的设计元素
2. 📄 生成设计规范文档
3. 💻 按规范生成你项目中的代码

## ⚠️ 前置要求

**必须先检查浏览器自动化工具**：

1. Playwright CLI - `playwright-cli open <url>`
2. Browser MCP - `skill_mcp(mcp_name="browser", tool_name="...")`
3. 其他浏览器工具

**如果没有浏览器工具**，尝试备选方案：
1. 使用 `webfetch` 获取页面 HTML + CSS
2. 或者建议用户安装 Playwright CLI

## Step 1: 提取设计元素

### 1.1 截图（保留参考）

用 Playwright CLI 截取目标网站截图：
- 桌面端 (1440px) 首页全图
- 移动端 (390px) 可选

```bash
playwright-cli open <url>
playwright-cli resize 1440 900
playwright-cli screenshot --filename=desktop.png
playwright-cli resize 390 844
playwright-cli screenshot --filename=mobile.png
playwright-cli close
```

### 1.2 提取设计 Tokens

用 playwright-cli eval 执行以下提取脚本：

```bash
playwright-cli open <url>
playwright-cli eval "
(function() {
  const root = document.documentElement;
  const colors = {};
  const rootStyles = getComputedStyle(root);
  for (const prop of rootStyles) {
    if (prop.startsWith('--')) {
      const value = rootStyles.getPropertyValue(prop).trim();
      if (value && value !== '') {
        colors[prop] = value;
      }
    }
  }
  const elements = document.querySelectorAll('h1, h2, h3, p, a, button, .btn, .button, header, nav, main, footer, [class*=\"card\"], [class*=\"hero\"], [class*=\"banner\"]');
  const sampledColors = [];
  const seenColors = new Set();
  elements.forEach(el => {
    const cs = getComputedStyle(el);
    const bg = cs.backgroundColor;
    const color = cs.color;
    const border = cs.borderColor;
    [bg, color, border].forEach(c => {
      if (c && c !== 'rgba(0, 0, 0, 0)' && c !== 'transparent' && !seenColors.has(c)) {
        seenColors.add(c);
        sampledColors.push({ color: c, usage: el.tagName.toLowerCase() });
      }
    });
  });
  const fonts = [...new Set([...document.querySelectorAll('*')].slice(0, 500).map(el => getComputedStyle(el).fontFamily))].filter(f => f && !f.includes('system-ui') && f.length < 100);
  const spacings = new Set();
  [...document.querySelectorAll('section, div[class], main, article, .container')].slice(0, 50).forEach(el => {
    const cs = getComputedStyle(el);
    const pt = parseFloat(cs.paddingTop);
    const pb = parseFloat(cs.paddingBottom);
    const pl = parseFloat(cs.paddingLeft);
    const pr = parseFloat(cs.paddingRight);
    if (pt > 0) spacings.add(pt);
    if (pb > 0) spacings.add(pb);
    if (pl > 0) spacings.add(pl);
    if (pr > 0) spacings.add(pr);
  });
  const borderRadii = new Set();
  [...document.querySelectorAll('button, a, img, .card, input, [class*=\"btn\"]')].slice(0, 30).forEach(el => {
    const br = getComputedStyle(el).borderRadius;
    if (br && br !== '0px') borderRadii.add(br);
  });
  const shadows = new Set();
  [...document.querySelectorAll('[class*=\"card\"], [class*=\"shadow\"], [class*=\"elevat\"], button, nav')].slice(0, 20).forEach(el => {
    const shadow = getComputedStyle(el).boxShadow;
    if (shadow && shadow !== 'none' && shadow !== 'initial') {
      shadows.add(shadow);
    }
  });
  const typography = [...document.querySelectorAll('h1, h2, h3, h4, h5, h6, p, small, span:not([class])')].slice(0, 50).map(el => {
    const cs = getComputedStyle(el);
    return {
      tag: el.tagName.toLowerCase(),
      fontSize: cs.fontSize,
      fontWeight: cs.fontWeight,
      lineHeight: cs.lineHeight,
      fontFamily: cs.fontFamily.split(',')[0].trim(),
      color: cs.color
    };
  });
  return JSON.stringify({
    cssVariables: colors,
    sampledColors: sampledColors.slice(0, 20),
    fonts: fonts.slice(0, 10),
    spacingSystem: [...spacings].sort((a, b) => a - b).slice(0, 10),
    borderRadii: [...borderRadii].sort((a, b) => parseFloat(a) - parseFloat(b)).slice(0, 6),
    shadows: [...shadows].slice(0, 6),
    typography: typography.filter(t => t.fontWeight !== '400' || t.tag === 'h1' || t.tag === 'p')
  }, null, 2);
})()
"
playwright-cli close
```

### 1.3 简化颜色提取（快速版）

如果上方脚本太慢，用这个简化版：

```javascript
// 快速颜色提取
(function() {
  const getColor = (el) => {
    const cs = getComputedStyle(el);
    return {
      bg: cs.backgroundColor,
      color: cs.color,
      border: cs.borderColor,
      shadow: cs.boxShadow
    };
  };

  const samples = [];
  document.querySelectorAll('header, nav, main, section, footer, .hero, .card, button').forEach((el, i) => {
    if (i > 30) return;
    const c = getColor(el);
    if (c.bg !== 'rgba(0, 0, 0, 0)' && c.bg !== 'transparent') samples.push({type: 'bg', ...c});
    if (c.color !== 'rgb(0, 0, 0)') samples.push({type: 'text', ...c});
  });

  // 去重
  const unique = [];
  const seen = new Set();
  samples.forEach(s => {
    const key = s.color;
    if (!seen.has(key)) {
      seen.add(key);
      unique.push(s);
    }
  });

  return JSON.stringify(unique.slice(0, 15), null, 2);
})();
```

## Step 2: 生成设计规范

根据提取的数据，生成 DESIGN.md 格式的规范：

```markdown
# Design System: [网站名]

## 1. Visual Theme & Atmosphere
[描述整体感觉：专业/简约/活泼/暗色系等]

## 2. Color Palette
[用提取的实际颜色，按语义命名]
- Primary: #xxx
- Secondary: #xxx
- Background: #xxx
- Text: #xxx
- Accent: #xxx

## 3. Typography
[提取的字体 + 层级]
- 标题: [font] - [size]/[weight]
- 正文: [font] - [size]/[weight]

## 4. Spacing System
[间距比例: 4px / 8px / 16px / 24px / 32px / 48px / 64px]

## 5. Component Stylings
[按钮/卡片等的样子]
- 按钮: border-radius: X, padding: X, shadow: X
- 卡片: border-radius: X, padding: X, shadow: X

## 6. Border Radius
[圆角比例: sm / md / lg / xl]

## 7. Shadows
[阴影层级]
```

## Step 3: 生成可应用的代码

根据提取的设计规范，生成可直接使用的 CSS/Tailwind 代码片段：

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
:root {
  --color-primary: #HEX值;
  --color-secondary: #HEX值;
  --spacing-base: Xpx;
  --radius-sm: Xpx;
  --radius-md: Xpx;
  --shadow-card: X X X rgba(0,0,0,X);
}
```

## Step 4: 询问应用场景

生成规范后，**主动问用户**：

```
✅ 设计规范已提取！

📐 [网站名] 设计风格：
- 主色: #HEX
- 字体: Font Family
- 间距基准: Xpx
- 圆角: Xpx
- 阴影: ...

你想把这个风格用到哪里？
1. 我的登录页面
2. 我的仪表盘
3. 我的卡片组件
4. [告诉我你想做哪个页面/组件]
```

## 输出格式

### 完整输出示例

```
✅ 设计分析完成！

📐 设计规范: [网站名]
━━━━━━━━━━━━━━━━━━━━━━

🎨 颜色
   Primary:   #HEX (主按钮、重点元素)
   Secondary: #HEX (次要元素)
   Background: #HEX (背景)
   Text:      #HEX (正文)
   Muted:     #HEX (辅助文字)
   Border:    #HEX (边框)

🔤 字体
   标题: "Font Name", sans-serif
   正文: "Font Name", sans-serif
   代码: "JetBrains Mono", monospace

📏 间距系统
   4px / 8px / 16px / 24px / 32px / 48px

🎯 圆角
   sm: 4px | md: 8px | lg: 12px | xl: 16px

🌫 阴影
   sm: 0 1px 2px rgba(...)
   md: 0 4px 6px rgba(...)
   lg: 0 10px 15px rgba(...)

━━━━━━━━━━━━━━━━━━━━━━

已生成可直接使用的代码片段：
• tailwind.config.js 颜色/圆角/阴影扩展
• CSS 变量文件 (design-tokens.css)

你想把这个风格用到哪个页面/组件？
```

## 注意事项

- **不需要完整克隆**：只提取风格元素，不复制内容
- **生成的是可应用代码**：不是参考图，是可以直接用的 CSS/Tailwind
- **渐进式使用**：可以只用在某个组件，不需要整个项目
- **如有多处使用**：可以导出为全局 CSS 变量或 Tailwind 扩展

## 适用场景

✅ **你看到喜欢的网站，想用它的风格做自己的页面**
✅ **你不会配色，让 AI 帮你参考优秀网站的配色**
✅ **你想学某个网站是怎么设计的，但它没有开源**
✅ **你有多个网站想统一设计风格**
