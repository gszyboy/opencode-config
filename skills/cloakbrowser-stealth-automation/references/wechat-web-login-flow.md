# WeChat Web Login Flow — 2026-05-20

## ⚠️ 已废弃（2026-05-20 确认）

腾讯官方已封禁中国大陆账号的网页版微信登录。无论何种技术手段均无法绕过，此流程已无实际意义，仅作技术记录保留。

---

## 环境前提

WSL2 + WSLg 已配置：
```bash
export DISPLAY=:0
export WAYLAND_DISPLAY=wayland-0
export XDG_RUNTIME_DIR=/mnt/wslg/runtime-dir
```
（这些在用户 `.bashrc` 中已配置）

无头模式（无图形界面）下：
- 需要 `launch_persistent_context(..., headless=True)` + 轮询 cookie 检测登录
- 二维码通过 `bash` 调用 `curl` 下载到 `/tmp/wechat_qr.png`，然后展示给用户扫码
- 有效期极短（30-60秒），需要快速扫码

有头模式（有图形界面）下：
- `DISPLAY=:0` + `headless=False` 直接在 Windows 桌面弹窗
- 用户直接扫 PC 浏览器里的二维码，最快最可靠

---

## 微信二维码 URL 格式

```
https://login.weixin.qq.com/qrcode/{UUID}==
```

注意：
- UUID 是页面加载时动态生成的
- curl 下载时必须加 `-H "Referer: https://web.weixin.qq.com/"`，否则返回 HTML 而非图片
- 二维码有效期几十秒，过期需刷新页面重新获取 UUID

---

## 登录成功判断

微信登录 cookie 特征：
- `webwx_data_ticket`
- `wxsid`
- `wxuin`
- 正常情况只有 3 个基础 cookie（mm_lang, MM_WX_NOTIFY_STATE, MM_WX_SOUND_STATE）
- 登录成功后 cookie 总数 > 5

轮询检测逻辑：
```python
cookies = browser.cookies()
names = [c['name'] for c in cookies]
if any('wxsid' in n or 'webwx' in n or 'wxuin' in n for n in names):
    print("登录成功!")
```

---

## 已知问题

1. **二维码过期**：有效期短，下载→发送→你扫码流程太慢
2. **stealth 拦截登录请求**：CloakBrowser 的 C++ 补丁拦截了微信登录轮询，必须用普通 Playwright
3. **页面加载超时**：微信页面 `wait_until='commit'` 而非 `'load'`，否则超时
4. **截图超时**：CloakBrowser headless 截图默认等字体加载，加 `-H "Accept-Language: en-US"` 或短超时参数

---

## Profile 持久化

无论用 CloakBrowser 还是普通 Playwright，都要用 `launch_persistent_context(profile_dir)`：

```python
from cloakbrowser import launch_persistent_context

profile_dir = '/home/plf/opencode_work/.data/weixin_profile'
browser = launch_persistent_context(profile_dir, headless=True)
```

登录成功后，cookies 和 localStorage 自动持久化到 profile 目录。下次运行直接加载，无需重新扫码。
