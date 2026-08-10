"""能力：反爬对抗

解决：绕过 Cloudflare/反爬检测、IP 限制、浏览器指纹识别
方案：
- 代理池自动轮换（proxy_pool / 自建）
- 隐身浏览器（Playwright stealth / camoufox）
- 请求头随机化 + 指纹模拟
- Cloudflare 绕过
"""

import random
from typing import Optional


class AntiCrawl:
    """反爬对抗能力层"""

    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64; rv:126.0) Gecko/20100101 Firefox/126.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0",
    ]

    def __init__(self, proxy_list: Optional[list] = None):
        self.proxies = proxy_list or []

    def random_headers(self, referer: str = "") -> dict:
        """生成随机浏览器请求头"""
        headers = {
            "User-Agent": random.choice(self.USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
        if referer:
            headers["Referer"] = referer
        return headers

    def get_proxy(self) -> Optional[dict]:
        """从代理池取一个代理"""
        if not self.proxies:
            return None
        p = random.choice(self.proxies)
        return {"http": p, "https": p}

    def stealth_fetch(self, url: str, render_js: bool = False) -> str:
        """
        隐身访问网页（绕过反爬）。
        优先用隐身浏览器，失败回退普通请求。

        CloakBrowser / camoufox 是 pass 30/30 反爬检测的隐身 Chromium。
        安装：pip install camoufox[geoip] 或接 CloakBrowser。
        """
        if render_js:
            return self._stealth_browser_fetch(url)
        return self._normal_fetch(url)

    def _stealth_browser_fetch(self, url: str) -> str:
        """用隐身浏览器访问（绕过 JS 反爬）"""
        try:
            # 尝试 camoufox（反检测 Firefox）
            import asyncio
            from camoufox.sync_api import Camoufox
            with Camoufox() as browser:
                page = browser.new_page()
                page.goto(url, wait_until="networkidle")
                return page.content()
        except ImportError:
            self._has_camoufox = False  # 隐身浏览器未安装，回退到 Playwright
        except Exception as e:
            return f"[反爬] 隐身浏览器失败: {e}"

        # 回退：Playwright + harden
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=True,
                    args=["--disable-blink-features=AutomationControlled"]
                )
                context = browser.new_context(
                    user_agent=random.choice(self.USER_AGENTS),
                    viewport={"width": 1920, "height": 1080},
                )
                # 隐藏 webdriver 指纹
                context.add_init_script(
                    "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
                )
                page = context.new_page()
                page.goto(url, wait_until="networkidle")
                content = page.content()
                browser.close()
                return content
        except ImportError:
            return "[反爬] 需要安装 playwright: pip install playwright && playwright install chromium"
        except Exception as e:
            return f"[反爬] JS访问失败: {e}"

    def _normal_fetch(self, url: str) -> str:
        """普通请求（带随机头 + 代理）"""
        try:
            import requests
            resp = requests.get(
                url,
                headers=self.random_headers(),
                proxies=self.get_proxy(),
                timeout=20,
                verify=False,
            )
            return resp.text
        except ImportError:
            return "[反爬] 需要安装 requests"
        except Exception as e:
            return f"[反爬] 请求失败: {e}"