---
name: social-platform-automation
description: |
  Use when automating Chinese social platforms: Douyin (search, video playback, download),
  WeChat public account article scraping, Xiaohongshu/Weibo content discovery,
  and bypassing login walls via search-engine indexing.
  Trigger on 抖音 / Douyin / 微信公众号 / 微信文章 / 小红书 / Xiaohongshu / 微博 / 社交平台 / social platform.
  For the browser layer, use CloakBrowser via the cloakbrowser-stealth-automation skill when anti-bot is needed.
triggers:
  - 抖音 自动化
  - 抖音 下载
  - 抖音视频下载
  - 微信公众号 抓取
  - 微信公众号文章
  - 微信文章 下载
  - 小红书 自动化
  - 小红书 笔记
  - 微博 抓取
  - 社交平台 自动化
  - social platform automation
  - douyin automation
  - douyin video download
  - wechat public account scraping
  - xiaohongshu automation
  - weibo scraping
---

# Social Platform Automation

## OpenCode 适配说明

本 Skill 已从 Hermes 框架迁移到 OpenCode。执行方式统一为：

- 用 OpenCode 的 `bash` 工具运行 Python/Shell 命令。
- 浏览器自动化脚本通过 `bash` 调用 `/usr/bin/python3.10` 执行。
- 不要依赖 `terminal(...)`、`browser_navigate` 等 Hermes 专用工具名。

## 浏览器层依赖

本 skill 的示例使用 CloakBrowser 或 Playwright 作为浏览器层。
CloakBrowser 的安装、启动参数、反爬虫细节见 `cloakbrowser-stealth-automation` skill。
执行时统一用 `/usr/bin/python3.10`，不要用当前 shell 默认的 pyenv `python3`。

## Overview

Umbrella for automating Chinese social platforms: Douyin video/search/playback, WeChat public account article scraping, and bypassing login walls via search engine indexing. Consolidates formerly separate `douyin-browser-automation`, `douyin-video-download`, `wechat-public-account-scraping`, and the research utility `platform-content-discovery` skills.

## When to Use

- User asks to search, browse, extract content, or download from Douyin (抖音)
- User asks to crawl or scrape WeChat public account (公众号) articles
- User mentions a specific Douyin/Weibo/Xiaohongshu post, video, or topic
- Need to bypass login walls on Chinese social platforms via search engine proxy
- Automated interaction with Douyin comments, video IDs, or share URLs

## Platform Decision Tree

```
Task involves Douyin?
  YES → Use Section 1 (Douyin Browser Automation) + Section 2 (Douyin Video Download)
  NO
    ↓
Task involves WeChat public account articles?
  YES → Use Section 3 (WeChat Public Account Scraping)
  NO
    ↓
Task is research/discovery on Chinese platforms (no direct URL)?
  YES → Use Section 4 (Platform Content Discovery)
  NO → Use appropriate platform-specific tool
```

---

## Section 1: Douyin Browser Automation

> Absorbed from `douyin-browser-automation` (2026-05-20)

### Environment
- **Python**: `/usr/bin/python3.10` — OpenCode 当前 shell 的 `python3` 可能是 pyenv 3.12，没有 playwright/cloakbrowser，所以必须显式指定系统 Python。
- **Playwright**: pre-installed at system level (under `/usr/bin/python3.10`)
- **Browser**: Playwright's bundled Chromium headless — bypasses Douyin's captcha on `so.douyin.com`
- **WSL network**: Independent from Windows — Google returns 400 but Douyin works fine

### Verified Working Flow

**1. Search + Video Play (fully working)**
```python
from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        viewport={"width": 390, "height": 844},
        user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
        locale="zh-CN"
    )
    page = context.new_page()
    
    # Search page — NO captcha
    page.goto("https://www.douyin.com/search/跳舞", timeout=30000)
    time.sleep(5)
    
    # Videos are embedded and auto-playing on search page
    videos = page.query_selector_all("video")
    # video[0].src contains real Douyin CDN URL (v26-dymsearch.douyinvod.com)
```

**2. Extracting Comments from Search Page (NO need to open video)**

Key discovery: Comment data is embedded in `<script>` tags on the `so.douyin.com` search page.

```python
for i in range(3):
    page.evaluate(f"window.scrollBy(0, {500 * (i+1)})")
    time.sleep(2)

data = page.evaluate("""
    () => {
        const scripts = Array.from(document.querySelectorAll('script'));
        let allText = '';
        for (const s of scripts) allText += s.textContent || '';

        // 1) Comment text — match "text":"..."
        const comments = [];
        const textMatches = allText.match(/"text":"([^"]{3,200})"/g) || [];
        for (const m of textMatches) {
            const t = m.match(/"text":"([^"]+)"/)?.[1];
            if (t && t.length > 2 && !t.includes('\\n') && !comments.includes(t)) {
                comments.push(t);
            }
        }

        // 2) User nicknames
        const nicknames = [];
        const nickMatches = allText.match(/"nickname":"([^"]{1,30})"/g) || [];
        for (const m of nickMatches) {
            const n = m.match(/"nickname":"([^"]+)"/)?.[1];
            if (n && !nicknames.includes(n)) nicknames.push(n);
        }

        // 3) Comment counts
        const counts = [];
        const countMatches = allText.match(/"comment_count":(\\d+)/g) || [];
        for (const m of countMatches) {
            const c = m.match(/"comment_count":(\\d+)/)?.[1];
            if (c) counts.push(c);
        }

        // 4) Video IDs
        const ids = [];
        const idMatches = allText.match(/"video_id":[:\\s]*"?(\\d{17,20})"?/g) || [];
        for (const m of idMatches) {
            const r = m.match(/"video_id":[:\\s]*"?(\\d{17,20})"?/);
            if (r && !ids.includes(r[1])) ids.push(r[1]);
        }

        return {
            comments: comments.slice(0, 20),
            nicknames: nicknames.slice(0, 20),
            comment_counts: [...new Set(counts)],
            video_ids: ids.slice(0, 15)
        };
    }
""")
```

**3. Opening Video Detail Page**
```python
page.goto(
    f"https://m.douyin.com/share/video/{video_id}/",
    timeout=20000,
    wait_until="commit"   # ← CRITICAL: without this it times out
)
```

### Key URLs

| URL | Works? | Notes |
|-----|--------|-------|
| `www.douyin.com` | ✅ | Homepage, may need login |
| `www.douyin.com/search/{keyword}` | ⚠️ | Redirects to `so.douyin.com` |
| `so.douyin.com/search/{keyword}` | ✅ **BEST** | No captcha, has comment data in HTML |
| `www.douyin.com/video/{id}` | ❌ **TIMEOUT** | Never use this |
| `m.douyin.com/share/video/{id}` | ✅ | Mobile share page — requires `wait_until="commit"` |

### Common Errors
- **Timeout on video detail page**: Use `wait_until="commit"`
- **No comments found**: Scroll down first — search page lazy-loads content
- **0 script tag matches**: Use `all.match()` with proper escaping

---

## Section 2: Douyin Video Download

> Absorbed from `douyin-video-download` (2026-05-20)

### Download from Share Links

1. Navigate to the share URL using a Python script executed via `bash` (e.g. `bash(command="/usr/bin/python3.10 douyin_share.py ...")`)
2. Extract the direct video URL:
   ```js
   document.querySelector('video')?.src || document.querySelector('video source')?.src || Array.from(document.querySelectorAll('video')).map(v=>v.src).filter(Boolean)
   ```
3. Attempt download with `bash` + `curl`
4. If the download is tiny (~300-400 bytes) or `file` reports HTML → 403 Forbidden
5. Retry with authenticated headers:
   ```bash
   bash(
     command="curl -L -o /tmp/douyin_video2.mp4 -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36' -H 'Referer: https://www.douyin.com/' -b 'PASTE_COOKIE_STRING_HERE' VIDEO_URL",
     timeout=120000
   )
   ```
6. Verify: `bash(command="file /tmp/douyin_video2.mp4")` should report `ISO Media, MP4 Base Media`

### Key findings (verified 2026-05-20)
- `so.douyin.com` search pages load without CAPTCHA
- Videos use `v26-dymsearch.douyinvod.com` CDN domain
- Douyin CDN requires `Referer` and `User-Agent` headers for raw video download

---

## Section 3: WeChat Public Account Scraping

> Original content date: 2026-05-20

### Method A — Direct URL (Recommended, 100% Reliable)
```python
from cloakbrowser import launch
import time, os

browser = launch(headless=True, humanize=True)
page = browser.new_page()

url = 'https://mp.weixin.qq.com/s/H4PHHMUBq_Z2JQ8LrPgHMg'
page.goto(url, timeout=15000, wait_until='commit')
time.sleep(4)

title = page.evaluate('document.title')
raw_text = page.evaluate('document.body.innerText')
author = page.evaluate('() => { const el = document.querySelector("#js_name"); return el ? el.innerText : ""; }')

# Screenshot captures article WITH images
os.makedirs('/tmp/wechat_screenshots', exist_ok=True)
page.screenshot(path='/tmp/wechat_screenshots/article.png', full_page=True)

browser.close()
```

### Method B — Google News Search (Fallback)
```python
q = f'KEYWORD site:mp.weixin.qq.com'
url = f'https://www.google.com/search?q={urllib.parse.quote(q)}&tbm=nws&num=10'
# Always use tbm=nws (Google News), not standard web search
# Always use page.evaluate() to extract href, not innerText
links = page.evaluate('''
() => {
    const results = [];
    document.querySelectorAll('a').forEach(a => {
        const href = a.href;
        if (href && href.match(/https:\\/\\/mp\\.weixin\\.qq\\.com\\/s\\/[a-zA-Z0-9_-]{10,}/)) {
            if (!results.includes(href)) results.push(href);
        }
    });
    return results;
}
''')
```

### Key limitations
- Google News coverage is extremely limited (0-2 relevant articles per keyword)
- **Always use `tbm=nws`** — standard Google search returns 0 WeChat results
- mmbiz.qpic.cn images have referer 防盗链 — use **screenshot** instead of img download
- Bing blocks CloakBrowser — do not use Bing as a search source
- Article titles appear as "微信公众平台" in Google News — real title only after fetching URL

---

## Section 4: Platform Content Discovery

> Original content date: 2026-05-20 — research utility for Chinese platforms

### Core Technique: Search Engine as Middle Layer

When a Chinese platform requires login (Douyin, Weibo, Xiaohongshu), use search engines as a proxy.

### Verified Working Search Engines

| Engine | Status | Notes |
|--------|--------|-------|
| **Yahoo** | ✅ Works | Best for Chinese content, indexes Douyin/Weibo |
| **Bing** | ✅ Works | Good coverage, less likely to block |
| Google | ❌ Blocked | WSL exit IP detected as datacenter |

### Search Syntax
```
site:douyin.com <keywords>
site:weibo.com <keywords>
site:xiaohongshu.com <keywords>
```

### Known Findings (2026-05-20)
- Yahoo successfully indexed Douyin note `7639562817738072719`: "5.20-25时代少年团在甘肃兰州和张掖录制节目"
- Yahoo indexed Douyin note `7473539087329234219`: "张掖要有时代峰峻第一场线下啦" (2025-02-21)

### Content Verification Chain
```
Search (Yahoo/Bing) → Get indexed snippet + URL
  ↓
Try direct URL in browser
  ↓ (if blocked)
Extract content ID from URL
  ↓
Search for content ID as keyword
  ↓
Get more details from indexed snippet
```

---

## Section 5: Xiaohongshu (小红书) AI Chat

> Tested 2026-06-15

### Test Results

| Target | Result | Notes |
|--------|--------|-------|
| `xiaohongshu.com/ai_chat` open | ✅ | CloakBrowser direct access, no proxy needed |
| Anonymous access AI Chat | ❌ | Redirects to logged-out homepage |
| Cookie reuse for login | ❌ | Saved cookies are anonymous, no account session |
| Web QR code login | ❌ | `/login`, `/website-login/wechat` all return "page not found" |
| Slider captcha | ⚠️ | Exists but cannot auto-pass |

**Core conclusion: XHS AI Chat (点点) requires in-app access. Web QR login is offline.**

### Verified Login Paths

- `/login` → "页面不存在"
- `/website-login/wechat` → "页面不存在"
- `/website-login/captcha` → Slider captcha (verifyUuid + verifyType=216) — cannot auto-pass
- Anonymous cookie is NOT a login session — API calls return HTTP 500

### Recommended Approaches

**Option A — APP-assisted token extraction:**
1. Open AI Chat in XHS mobile app
2. Capture cookie/token via app debugging or mitmproxy
3. Save to `/home/plf/opencode_work/.data/xhs_session.json`
4. Use in requests header: `Cookie: a1=...; webId=...; web_session=...`

**Option B — Third-party xhs Python package:**
Search GitHub for `xhs` or `xiaohongshu` Python package (e.g. `johnserf-seed/TikTokPy`-style packages). These support phone QR code token acquisition and can access notes/comments.

### Key Cookie Fields (confirmed)
- `a1` — device ID
- `webId` — web session ID
- `acw_tc` — signature token
- `xsecappid` — fixed value `ranchi`
- `ets` / `loadts` — timestamp-related

Anonymous cookies contain the above but are NOT a logged-in session.

### CloakBrowser Setup (XHS)
```python
from cloakbrowser import launch

browser = launch(headless=False, humanize=True)
context = browser.new_context(
    viewport={'width': 390, 'height': 844},
    user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)...'
)
page = context.new_page()
page.goto('https://www.xiaohongshu.com/ai_chat', timeout=30000)
```

---

## Common Pitfalls

1. **Don't use the default `python3` in OpenCode shell** — it may be pyenv 3.12 and lack playwright/cloakbrowser modules; use `/usr/bin/python3.10`
2. **Don't use `www.douyin.com/video/{id}`** — it always times out; use `m.douyin.com/share/video/{id}` with `wait_until="commit"`
3. **Douyin CDN 403 without headers** — always set `Referer` and `User-Agent` when downloading raw video URLs
4. **WeChat innerText corrupts URLs** — always use `page.evaluate('a.href')` to get real URLs
5. **Google News (tbm=nws) required** — standard Google web search returns 0 WeChat results
6. **mmbiz image download returns 400** — use CloakBrowser screenshot instead of urllib/curl
7. **XHS AI Chat requires APP login** — web QR login is offline as of 2026-06; anonymous access always redirects to logged-out homepage

## Absorbed Skills

The following formerly separate skills were consolidated here:
- `douyin-browser-automation` → Section 1 of this SKILL.md
- `douyin-video-download` → Section 2 of this SKILL.md  
- `wechat-public-account-scraping` → Section 3 of this SKILL.md
- `platform-content-discovery` → Section 4 of this SKILL.md
