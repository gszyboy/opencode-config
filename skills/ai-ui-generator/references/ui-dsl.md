# UI Prompt DSL 结构

## DSL 格式

```text
[PRODUCT]
产品类型

[PAGE]
页面类型

[PLATFORM]
平台类型

[STYLE]
设计风格

[DESIGN_SYSTEM]
设计系统

[COMPONENTS]
页面组件

[LAYOUT]
布局结构

[IMPLEMENTATION]
工程约束

[NEGATIVE]
负向约束
```

---

## 字段说明

### [PRODUCT]
描述产品类型和业务场景。例如：
- AI 导游助手
- 电商平台
- SaaS 管理后台
- 社交应用

### [PAGE]
描述当前页面类型。例如：
- 首页
- 列表页
- 详情页
- 个人中心

### [PLATFORM]
描述目标平台。可选值：
- h5 - 移动网页
- wechat-mini-program - 微信小程序
- app - 原生应用
- pc-web - 桌面端网页
- admin - 管理后台

### [STYLE]
描述设计风格。可组合多个风格：
- ios - iOS 风格
- tencent - 腾讯系风格
- stripe - Stripe 风格
- linear - Linear 风格
- material - Material Design

### [DESIGN_SYSTEM]
描述设计系统规范：
- spacing system（如：8px spacing）
- shadow style（如：soft shadow）
- accent color（如：blue accent）
- corner radius（如：rounded corners）

### [COMPONENTS]
列出页面包含的组件，每行一个：
- search bar
- banner
- card
- tabbar
- timeline
- data table
- etc.

### [LAYOUT]
描述布局结构：
- mobile-first
- desktop
- scroll layout
- sidebar layout
- grid layout

### [IMPLEMENTATION]
工程实现约束：
- frontend-friendly
- production-ready
- component-based
- responsive

### [NEGATIVE]
负向约束，排除不想要的风格：
- not dribbble
- not futuristic
- not concept art
- not abstract

---

## 完整示例

```text
[PRODUCT]
AI 导游助手

[PAGE]
首页

[PLATFORM]
wechat-mini-program

[STYLE]
ios + tencent

[DESIGN_SYSTEM]
8px spacing
soft shadow
blue accent

[COMPONENTS]
search bar
banner
travel card
timeline
tabbar

[LAYOUT]
mobile-first
scroll layout

[IMPLEMENTATION]
frontend-friendly
production-ready
component-based

[NEGATIVE]
not dribbble
not futuristic
not concept art
```
