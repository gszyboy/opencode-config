---
name: cloakbrowser-stealth-automation
description: |
  Use CloakBrowser — 源码级 Chromium 反爬虫浏览器 — 处理需要通过 Cloudflare Turnstile、reCAPTCHA v3、FingerprintJS、BrowserScan 等检测的自动化任务。
  也用于微信 Windows 客户端自动化、需要高隐身性的浏览器操作、以及普通 Playwright 被封禁的场景。
  只要用户提到 安全浏览器 / 反检测浏览器 / 防封浏览器 / CloakBrowser / cloudflare / recaptcha / 指纹检测 / 微信 PC 客户端自动化，立即使用本 skill。
triggers:
  - 安全浏览器
  - 用安全浏览器打开
  - 反检测浏览器
  - 防封浏览器
  - cloakbrowser 打开
  - 微信 windows 客户端自动化
  - wechat windows automation
  - 反爬虫 绕过
  - cloudflare turnstile
  - recaptcha
  - 指纹检测 绕过
  - stealth chromium
  - bot detection bypass
---

# CloakBrowser Stealth Automation

## OpenCode 适配说明

本 Skill 已从 Hermes 框架迁移到 OpenCode。执行方式统一为：

- 用 OpenCode 的 `bash` 工具运行 Python/Shell 命令。
- 浏览器自动化脚本通过 `bash` 调用 `/usr/bin/python3.10` 执行。
- 不要依赖 `terminal(...)`、`browser_navigate` 等 Hermes 专用工具名。

## 核心定位

**CloakBrowser** 是一个在 C++ 源码层面修改了浏览器指纹的 Chromium 构建，目标是让自动化浏览器通过所有主流反爬虫检测（Cloudflare Turnstile、reCAPTCHA v3、FingerprintJS、BrowserScan 等）。

核心区别：
- ❌ 不是 JS 注入（`playwright-stealth` 那套）
- ❌ 不是配置文件修改（`undetected-chromedriver`）
- ✅ 是**编译进二进制的 C++ 源码级补丁**

## 环境前提：WSLg 图形界面

WSL2 已配置 WSLg 时，图形程序直接投射到 Windows 桌面：
```bash
export DISPLAY=:0
export WAYLAND_DISPLAY=wayland-0
export XDG_RUNTIME_DIR=/mnt/wslg/runtime-dir
```

用户已确认 WSLg 可用。有头模式（`headless=False`）可以直接在 Windows 桌面上弹出浏览器窗口，比下载二维码图片快得多。

## 安装

```bash
bash(command="/usr/bin/python3.10 -m pip install cloakbrowser")
```

## 环境注意

**Python 路径问题**：
```
当前 OpenCode shell 的 `python3` 可能是 pyenv 3.12，没有 cloakbrowser/playwright。
系统 Python `/usr/bin/python3.10` 已安装所需包。

正确调用方式：
/usr/bin/python3.10 -c "from cloakbrowser import launch; ..."
```

**后台进程问题**：OpenCode 的 `bash` 工具不支持 `&` 后台语法。需要长超时请直接给 `timeout` 参数（单位毫秒）：
```python
bash(command="/usr/bin/python3.10 long_running.py", timeout=310000, workdir="/home/plf/opencode_work")
```

**不要用当前 shell 默认的 `python3`**，必须用 `/usr/bin/python3.10`。

## 快速开始

```python
from cloakbrowser import launch

browser = launch(headless=True)
page = browser.new_page()

page.goto("https://protected-site.com")
print(page.title())
browser.close()
```

## 常用参数

| 参数 | 作用 |
|------|------|
| `headless` | 无头模式，默认 True |
| `humanize=True` | 真人鼠标曲线/键盘时序/滚动，一个参数通过行为检测 |
| `proxy="http://user:pass@host:port"` | 代理支持 |
| `geoip=True` | 根据代理 IP 自动设置时区和语言（需 geoip 依赖） |
| `timezone="Asia/Shanghai"` | 显式指定时区 |
| `locale="zh-CN"` | 显式指定语言 |
| `stealth_args=False` | 关闭默认隐身参数（自己指定指纹） |

### 真人行为模式

```python
# 推荐：人类行为模拟
browser = launch(humanize=True)

# 更谨慎的人类模式
browser = launch(humanize=True, human_preset="careful")
```

### 代理配置

```python
# HTTP/SOCKS5 代理
browser = launch(proxy="http://user:pass@proxy:8080")
browser = launch(proxy="socks5://user:pass@proxy:1080")

# geoip 自动从代理 IP 推断时区+语言，并自动设置 WebRTC IP 防泄露
browser = launch(proxy="http://proxy:8080", geoip=True)
```

### 持久化上下文

```python
from cloakbrowser import launch_persistent_context

# 跨会话保持 cookies 和 localStorage，避免被检测为隐身模式
ctx = launch_persistent_context("./my-profile", headless=False)
page = ctx.newPage()
```

## Playwright API 100% 兼容

```python
from cloakbrowser import launch  # 替换 from playwright.sync_api import sync_playwright

browser = launch()
page = browser.new_page()
page.goto("...")
page.fill("#search", "keyword")
page.click("button[type=submit]")
# 所有 Playwright API 完全相同
```

## JavaScript 用法

```javascript
import { launch } from 'cloakbrowser';

const browser = await launch({ headless: true });
const page = await browser.newPage();
await page.goto('https://example.com');
await browser.close();
```

也支持 Puppeteer：`import { launch } from 'cloakbrowser/puppeteer'`

## 性能对比（实测）

| 检测项 | 普通 Playwright | CloakBrowser |
|--------|---------------|-------------|
| reCAPTCHA v3 分数 | 0.1（机器人） | **0.9**（真人） |
| Cloudflare Turnstile | 失败 | **通过** |
| FingerprintJS | 检测为机器人 | **通过** |
| BrowserScan | 检测为机器人 | **4/4 通过** |
| navigator.webdriver | true | **false** |
| UA 字符串 | HeadlessChrome | **Chrome/146.0.0.0** |
| window.chrome | undefined | **object** |

## 二进制下载

首次运行自动下载 ~200MB，二进制缓存位于：
- Linux: `~/.cloakbrowser/chromium-*/`
- macOS: `~/.cloakbrowser/`

手动指定二进制路径：
```bash
export CLOAKBROWSER_BINARY_PATH=/path/to/chromium
```

## 降级

新版本出问题可回滚（wrapper 和二进制版本绑定）：
```bash
pip install cloakbrowser==0.3.21
```

## 局限性

- **不解决已出现的 CAPTCHA**：只防它不出现
- **不内置代理轮换**：需要自带代理
- **macOS 部分站点可能比 Linux 表现差**：指纹 profile 有已知不一致
- **reCAPTCHA 分数低时**：避免用 `page.wait_for_timeout()`（发 CDP 命令会被检测），用 `time.sleep()` 代替

## 微信自动化：两条路线（2026-05-20 更新）

### 路线A：微信网页版（web.weixin.qq.com）— 已废弃

**腾讯官方已封禁中国大陆账号的网页版登录**（2021年起陆陆续续封禁，2026年确认完全关闭）。

表现：扫码后提示「为保障账号安全，暂不支持使用网页版微信」。

无论用 CloakBrowser 还是普通 Playwright、无论是否 headless、无论用什么 profile——只要是中国大陆微信账号，都无法登录网页版。**不是技术问题，无法绕过。**

### 路线B：微信 Windows 客户端自动化（推荐）

通过 `uiautomation` 控制微信 PC 客户端，模拟鼠标键盘操作，支持：
- 自动给指定用户/群发消息（文本、图片）
- HTTP API 服务化，可被 Agent 调用
- 非 Hook/非协议，安全可靠

**项目**：LAVARONG/wechat-automation-api（⭐114，活跃维护）
- 原理：Flask HTTP API + Windows uiautomation
- 端口：默认 `127.0.0.1:8808`
- 支持：文本/图片发送、批量发送、队列管理、Token 认证
- 安装：Windows 上 `pip install -r requirements.txt` + 启动微信 + `run.bat`
- Agent 调用示例（该命令属于 wechat-automation-api 项目，非本 skill 自带脚本）：
  ```bash
  bash(command="python scripts/skill_cli.py --to \\"文件传输助手\\" --content \\"测试消息\\"")
  ```
- HTTP 调用：
  ```python
  requests.post("http://127.0.0.1:8808/", json={
      "token": "123123",
      "action": "sendtext",
      "to": ["联系人名称"],
      "content": "消息内容"
  })
  ```

**注意**：微信 PC 客户端必须是传统桌面版（exe），不支持 Windows Store UWP 版（UWP 应用不暴露 UI 自动化接口）。

### 路线C：微信公众号文章抓取

微信公众号文章抓取的具体流程（直链访问、截图、Google News 索引等）已迁移到 `social-platform-automation` skill 的 Section 3。本 skill 只负责提供 CloakBrowser 的浏览器层能力；当 `social-platform-automation` 需要绕过腾讯检测时，再调用本 skill 的启动参数。

## 截图超时处理

CloakBrowser 的 headless screenshot 默认会等字体加载完，可能超时。两种解法：

```python
# 法1：加短超时 + full_page=False
page.screenshot(path='/tmp/shot.png', timeout=5000, full_page=False)

# 法2：用 page.goto 加 wait_until='commit'（不等资源加载完）
page.goto(url, wait_until='commit')
page.screenshot(path='/tmp/shot.png')
```

## 常用选择器速查

| 目标 | 选择器 |
|------|--------|
| 图片 src | `page.query_selector_all('img')` → `img.get_attribute('src')` |
| 搜索结果 | `page.query_selector_all('div.g')`（Google）|
| 页面文本 | `page.inner_text('body')` |
| body HTML | `page.content()` |
| 所有链接 | `page.query_selector_all('a')` |

## 相关工具对比

| | Playwright | playwright-stealth | undetected-chromedriver | CloakBrowser |
|--|---|---|---|---|
| 补丁方式 | 无 | JS 注入 | Config | **C++ 源码** |
| reCAPTCHA v3 | 0.1 | 0.3-0.5 | 0.3-0.7 | **0.9** |
| Chrome 更新后 | — | 常失效 | 常失效 | **不失效** |
| Playwright API | 原生 | 原生 | 否 | **原生** |

## Links

- CloakBrowser GitHub: https://github.com/CloakHQ/CloakBrowser
- CloakBrowser PyPI: https://pypi.org/project/cloakbrowser
- CloakBrowser npm: https://www.npmjs.com/package/cloakbrowser
- **微信 Windows 客户端自动化**：https://github.com/LAVARONG/wechat-automation-api
- **微信公众号爬虫**：https://github.com/LayFz/WeChat_Article_Crawler
