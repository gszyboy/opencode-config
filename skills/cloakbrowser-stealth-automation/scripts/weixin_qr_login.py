#!/usr/bin/env /usr/bin/python3.10
"""
WeChat Web QR Login — WeChat 扫码登录

用法：
    /usr/bin/python3.10 weixin_qr_login.py

注意：
    - 需要 /usr/bin/python3.10（OpenCode shell 默认 python3 可能是 pyenv 3.12，没有 playwright）
    - 登录成功后 cookies 持久化到 profile_dir，下次直接复用无需再扫码
    - CloakBrowser 会拦截微信登录请求，登录阶段必须用普通 Playwright
"""
import sys
import os
import time
import json

# 确保用系统 Python
if sys.executable != '/usr/bin/python3.10':
    os.execv('/usr/bin/python3.10', [sys.executable] + sys.argv)

from playwright.sync_api import sync_playwright


def get_qr_url(page) -> str:
    """从页面提取微信登录二维码 URL"""
    imgs = page.query_selector_all('img')
    for img in imgs:
        src = img.get_attribute('src') or ''
        if 'qrcode' in src.lower():
            if src.startswith('http'):
                return src
            elif src.startswith('//'):
                return 'https:' + src
            else:
                return 'https:' + src
    return ''


def wait_for_login(browser) -> bool:
    """
    轮询检测微信登录状态。
    返回 True 表示登录成功，False 表示超时。
    超时时间：120 秒
    """
    KNOWN_LOGIN_COOKIES = ['webwx_data_ticket', 'wxsid', 'wxuin', 'webwxauth']
    
    for i in range(120):
        time.sleep(1)
        cookies = browser.cookies()
        cookie_names = [c['name'] for c in cookies]
        
        # 检测登录 cookie
        for name in cookie_names:
            if any(k in name.lower() for k in KNOWN_LOGIN_COOKIES):
                print(f"[{i}s] ✓ 登录成功! {len(cookies)} cookies")
                for c in cookies:
                    val = c['value']
                    print(f"  {c['name']}: {val[:60]}..." if len(val) > 60 else f"  {c['name']}: {val}")
                return True
        
        if i % 10 == 0 and i > 0:
            print(f"[{i}s] 等待扫码... cookies={len(cookies)}")
    
    print("超时未检测到登录")
    return False


def download_qr(qr_url: str, path: str = '/tmp/weixin_qr.png') -> bool:
    """下载微信二维码到本地（必须带 Referer header）"""
    import subprocess
    result = subprocess.run(
        ['curl', '-s', '-o', path, '-H', 'User-Agent: Mozilla/5.0',
         '-H', 'Referer: https://web.weixin.qq.com/', qr_url],
        capture_output=True, text=True
    )
    # 验证是图片
    result2 = subprocess.run(['file', '-b', path], capture_output=True, text=True)
    if 'JPEG' in result2.stdout or 'PNG' in result2.stdout:
        print(f"二维码已保存: {path}")
        return True
    print(f"下载失败或不是图片: {result2.stdout}")
    return False


def main():
    import argparse
    parser = argparse.ArgumentParser(description='WeChat Web QR Login')
    parser.add_argument('--profile', default='/home/plf/opencode_work/.data/weixin_profile',
                        help='持久化 profile 目录路径')
    parser.add_argument('--qr-output', default='/tmp/weixin_qr.png',
                        help='二维码图片输出路径')
    parser.add_argument('--check-only', action='store_true',
                        help='只检查是否已登录，不重新扫码')
    args = parser.parse_args()

    profile_dir = os.path.expanduser(args.profile)
    os.makedirs(profile_dir, exist_ok=True)

    print(f"Profile 目录: {profile_dir}")
    
    with sync_playwright() as p:
        # 尝试加载已有 profile
        try:
            browser = p.chromium.launch_persistent_context(
                profile_dir,
                headless=True,
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36'
            )
            cookies = browser.cookies()
            cookie_names = [c['name'] for c in cookies]
            
            # 检查是否已登录
            if any('wxsid' in n or 'webwx' in n or 'wxuin' in n for n in cookie_names):
                print(f"✓ 已登录状态! {len(cookies)} cookies")
                for c in cookies:
                    print(f"  {c['name']}: {c['value'][:60]}..." if len(c['value']) > 60 else f"  {c['name']}: {c['value']}")
                return
            
            # 已存在 profile 但未登录
            print("Profile 存在但未登录，将打开新二维码")
            browser.close()
        except Exception:
            pass

        # 启动新浏览器会话
        browser = p.chromium.launch_persistent_context(
            profile_dir,
            headless=True,
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36'
        )
        page = browser.new_page()
        
        print("打开微信登录页...")
        page.goto('https://web.weixin.qq.com', timeout=20000, wait_until='commit')
        time.sleep(2)
        
        qr_url = get_qr_url(page)
        if not qr_url:
            print("错误：未能获取二维码 URL")
            browser.close()
            return
        
        print(f"二维码 URL: {qr_url}")
        
        # 下载二维码
        if download_qr(qr_url, args.qr_output):
            print(f"\n二维码已保存: {args.qr_output}")
            print("请扫码登录后继续...")
        
        # 等待登录
        if wait_for_login(browser):
            print("\n✓ 登录成功! Cookies 已保存到 profile 目录")
            print(f"  下次运行直接复用，无需再扫码")
        else:
            print("\n✗ 登录超时，请重新运行")
        
        browser.close()


if __name__ == '__main__':
    main()
