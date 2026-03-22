---
name: playwright-mcp
description: 强制使用 Playwright MCP 进行浏览器自动化测试，禁止在项目中安装 playwright npm 包。当用户需要测试前端项目、截图、爬取页面、执行浏览器自动化时必须使用此 skill。
tools: [playwright_navigate, playwright_screenshot, playwright_click, playwright_fill, playwright_select, playwright_hover, playwright_evaluate, playwright_close, playwright_get_visible_text, playwright_get_visible_html, playwright_aria_snapshot, playwright_console_logs, playwright_pdf, playwright_upload_file, playwright_press_key, playwright_drag, playwright_resize, playwright_iframe_click, playwright_iframe_fill, playwright_expect_response, playwright_assert_response, playwright_get, playwright_post, playwright_put, playwright_patch, playwright_delete, playwright_go_back, playwright_go_forward, playwright_click_and_switch_tab, playwright_save_as_pdf, playwright_custom_user_agent, playwright_start_codegen_session, playwright_end_codegen_session, playwright_get_codegen_session, playwright_clear_codegen_session]
---

# Playwright MCP 使用规范

## 核心原则

**绝对禁止**在项目中执行 `npm install playwright`、`yarn add playwright` 或 `pnpm add playwright`。
所有浏览器自动化必须通过 Playwright MCP Server 工具完成。

## 触发场景

- 测试前端项目的登录、表单、交互功能
- 截图对比 UI 状态
- 验证页面元素可见性和可访问性
- 生成 PDF 或抓取页面内容
- 爬取动态页面数据
- 执行浏览器端 JavaScript
- 测试响应式布局

## 执行前检查清单

1. ✅ 已检测到 `playwright_navigate` 工具可用
2. ✅ **未执行**任何 `npm/yarn/pnpm install playwright` 命令
3. ✅ 操作目标 URL 已确认可访问

---

## 工具分类参考

### 导航与浏览

| 工具 | 用途 | 关键参数 |
|------|------|----------|
| `playwright_navigate` | 导航到 URL | `url`, `browser`, `headless` |
| `playwright_go_back` | 后退 | - |
| `playwright_go_forward` | 前进 | - |
| `playwright_click_and_switch_tab` | 点击链接并切换新标签页 | `selector` |
| `playwright_custom_user_agent` | 设置自定义 User Agent | `userAgent` |

### 截图与 PDF

| 工具 | 用途 | 关键参数 |
|------|------|----------|
| `playwright_screenshot` | 截图 | `name`, `fullPage`, `selector` |
| `playwright_save_as_pdf` | 保存为 PDF | `outputPath`, `format`, `printBackground` |

### 元素交互

| 工具 | 用途 | 关键参数 |
|------|------|----------|
| `playwright_click` | 点击 | `selector` |
| `playwright_fill` | 填充输入框 | `selector`, `value` |
| `playwright_select` | 选择下拉选项 | `selector`, `value` |
| `playwright_hover` | 悬停 | `selector` |
| `playwright_press_key` | 按键 | `key`, `selector` |
| `playwright_drag` | 拖拽 | `sourceSelector`, `targetSelector` |
| `playwright_upload_file` | 文件上传 | `selector`, `filePath` |

### iframe 操作

| 工具 | 用途 | 关键参数 |
|------|------|----------|
| `playwright_iframe_click` | iframe 内点击 | `iframeSelector`, `selector` |
| `playwright_iframe_fill` | iframe 内填充 | `iframeSelector`, `selector`, `value` |

### 内容获取

| 工具 | 用途 | 关键参数 |
|------|------|----------|
| `playwright_get_visible_text` | 获取可见文本 | - |
| `playwright_get_visible_html` | 获取 HTML 内容 | `selector`, `removeScripts` |
| `playwright_aria_snapshot` | 获取无障碍树 | - |
| `playwright_console_logs` | 获取控制台日志 | `type`, `search`, `limit` |
| `playwright_evaluate` | 执行 JavaScript | `script` |

### 响应拦截

| 工具 | 用途 | 关键参数 |
|------|------|----------|
| `playwright_expect_response` | 等待 HTTP 响应 | `id`, `url` |
| `playwright_assert_response` | 验证响应内容 | `id`, `value` |

### HTTP 请求

| 工具 | 用途 | 关键参数 |
|------|------|----------|
| `playwright_get` | GET 请求 | `url`, `headers`, `token` |
| `playwright_post` | POST 请求 | `url`, `value`, `headers`, `token` |
| `playwright_put` | PUT 请求 | `url`, `value`, `headers`, `token` |
| `playwright_patch` | PATCH 请求 | `url`, `value`, `headers`, `token` |
| `playwright_delete` | DELETE 请求 | `url`, `headers`, `token` |

### 浏览器控制

| 工具 | 用途 | 关键参数 |
|------|------|----------|
| `playwright_resize` | 调整窗口大小 | `width`, `height`, `device` |
| `playwright_close` | 关闭浏览器 | - |

### 代码生成

| 工具 | 用途 | 关键参数 |
|------|------|----------|
| `playwright_start_codegen_session` | 开始录制会话 | `options` |
| `playwright_end_codegen_session` | 结束录制并生成测试 | `sessionId` |
| `playwright_get_codegen_session` | 获取会话信息 | `sessionId` |
| `playwright_clear_codegen_session` | 清除会话 | `sessionId` |

---

## 标准工作流程

### 流程 1: 基础测试

```
1. playwright_navigate → 打开页面
2. playwright_screenshot → 记录初始状态
3. 执行交互操作 (click/fill/hover)
4. playwright_screenshot → 记录结果状态
5. playwright_console_logs → 检查错误
6. playwright_close → 清理
```

### 流程 2: 表单提交测试

```
1. playwright_navigate
2. playwright_fill (多个字段)
3. playwright_click (提交按钮)
4. playwright_expect_response (可选)
5. playwright_get_visible_text → 验证结果
6. playwright_close
```

### 流程 3: 多页面测试

```
1. playwright_navigate (首页)
2. playwright_click_and_switch_tab (点击链接)
3. playwright_click_and_switch_tab → 切换到新标签页
4. playwright_screenshot
5. playwright_close
```

---

## 常见操作示例

### 登录测试

```tool
playwright_navigate:0 {"url": "http://localhost:3000/login", "browser": "chromium"}
playwright_fill:1 {"selector": "input[name=\"email\"]", "value": "test@example.com"}
playwright_fill:2 {"selector": "input[name=\"password\"]", "value": "password123"}
playwright_click:3 {"selector": "button[type=\"submit\"]"}
playwright_get_visible_text:4 {}
playwright_close:5 {}
```

### 截图对比

```tool
playwright_navigate:0 {"url": "http://localhost:3000"}
playwright_screenshot:1 {"name": "before", "fullPage": true}
playwright_click:2 {"selector": ".modal-toggle"}
playwright_screenshot:3 {"name": "after-modal", "fullPage": true}
playwright_close:4 {}
```

### 响应式测试

```tool
playwright_navigate:0 {"url": "http://localhost:3000"}
playwright_resize:1 {"width": 375, "height": 667}
playwright_screenshot:2 {"name": "mobile-view"}
playwright_resize:3 {"width": 1920, "height": 1080}
playwright_screenshot:4 {"name": "desktop-view"}
playwright_close:5 {}
```

### 文件上传

```tool
playwright_navigate:0 {"url": "http://localhost:3000/upload"}
playwright_upload_file:1 {"selector": "input[type=\"file\"]", "filePath": "/path/to/file.pdf"}
playwright_click:2 {"selector": "button[type=\"submit\"]"}
playwright_get_visible_text:3 {}
playwright_close:4 {}
```

---

## 禁止行为

以下行为**严格禁止**：

- ❌ 运行 `npm install playwright` 或 `yarn add playwright`
- ❌ 创建 `tests/` 目录并编写 `.spec.ts` 测试文件
- ❌ 使用 `npx playwright test` 命令
- ❌ 修改 `package.json` 添加 playwright 依赖
- ❌ 使用 `playwright.chromium.launch()` 等代码式调用

---

## 错误纠正

如果用户要求使用 Playwright 测试，必须：

1. 立即确认使用 **Playwright MCP** 进行浏览器自动化
2. 检查工具列表中是否存在 `playwright_navigate` 等 MCP 工具
3. 如 MCP 工具不可用，提示用户安装：
   ```bash
   opencode mcp add --scope user playwright npx @playwright/mcp@latest
   ```
4. **绝不**自动执行 npm install

---

## 输出要求

每次操作后必须：

1. 报告使用的 MCP 工具名称
2. 展示截图文件路径（如适用）
3. 总结页面状态变化
