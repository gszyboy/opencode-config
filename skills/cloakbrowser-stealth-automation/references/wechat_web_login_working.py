# 微信网页版扫码登录 — 经过实测验证的工作脚本
# 2026-05-20 验证通过

from playwright.sync_api import sync_playwright
import time
import os

PROFILE_DIR = os.path.expanduser("/home/plf/opencode_work/.data/weixin_profile")
os.makedirs(PROFILE_DIR, exist_ok=True)

# ============================================================
# Step 1: 用普通 Playwright 完成登录（二维码 + 扫码）
# 注意：不要用 CloakBrowser，它的 stealth 会拦截微信登录轮询
# ============================================================
def login_wechat():
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            PROFILE_DIR,
            headless=True,
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36'
        )
        page = browser.new_page()
        page.goto('https://web.weixin.qq.com', timeout=20000, wait_until='commit')
        time.sleep(2)

        # 提取二维码 URL
        imgs = page.query_selector_all('img')
        qr_url = None
        for img in imgs:
            src = img.get_attribute('src')
            if src and 'qrcode' in src.lower():
                qr_url = src if src.startswith('http') else 'https:' + src
                break

        if not qr_url:
            print("ERROR: 未找到二维码")
            return None

        print(f"二维码URL: {qr_url}")

        # 下载二维码（发给用户扫码）
        import subprocess
        subprocess.run([
            'curl', '-s', '-o', '/tmp/wechat_qr.png',
            qr_url,
            '-H', 'User-Agent: Mozilla/5.0',
            '-H', 'Referer: https://web.weixin.qq.com/'
        ])
        print("二维码已下载到 /tmp/wechat_qr.png，请发送给用户扫码")

        # 等待登录成功（轮询 cookie）
        for i in range(120):
            time.sleep(1)
            cookies = browser.cookies()
            names = [c['name'] for c in cookies]
            if any(n in ['wxsid', 'webwx_data_ticket', 'wxuin'] for n in names) or len(cookies) > 10:
                print(f"登录成功! {len(cookies)} cookies")
                browser.close()
                return True
            if i % 10 == 0:
                print(f"[{i}s] 等待扫码... cookies={len(cookies)}")

        print("超时未登录")
        browser.close()
        return False

# ============================================================
# Step 2: 登录成功后，用 CloakBrowser 加载同一 profile 做后续操作
# ============================================================
def open_wechat_automated():
    from cloakbrowser import launch_persistent_context

    browser = launch_persistent_context(PROFILE_DIR, headless=True)
    page = browser.new_page()
    page.goto('https://web.weixin.qq.com', timeout=20000, wait_until='commit')
    time.sleep(2)

    # 验证是否已登录
    text = page.inner_text('body')
    if 'Scan' in text or '登录' in text[:20]:
        print("未登录或登录已过期，需要重新扫码")
        browser.close()
        return None

    print(f"页面标题: {page.title()}")
    print("登录状态正常，可以开始自动化操作")
    return browser

# ============================================================
# 执行
# ============================================================
if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--auto':
        # 自动模式：直接尝试复用已有 profile
        browser = open_wechat_automated()
        if browser:
            print("可用!")
        else:
            print("需要重新登录")
    else:
        # 登录模式
        login_wechat()
