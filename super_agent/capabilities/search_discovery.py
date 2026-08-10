"""能力：搜索发现

解决：找到目标信息在哪
方案：
- 网页搜索：DuckDuckGo / 百度 / 必应 / Google
- 子域名枚举：subfinder(14k) / OneForAll(10k)
- 网站 OSINT：web-check(34k) 一站分析
- 社交账号：sherlock(88k) / maigret(36k)
- 邮箱：holehe(12k) / h8mail(5k)
- 电话：phoneinfoga(17k)
"""

import json
from typing import Optional


class SearchDiscovery:
    """搜索发现能力层"""

    # ─── 网页搜索 ───

    def search_web(self, query: str, engine: str = "duckduckgo",
                   num: int = 10, region: str = "cn-zh") -> list:
        """多引擎网页搜索"""
        if engine == "duckduckgo":
            return self._search_duckduckgo(query, num)
        elif engine == "baidu":
            return self._search_baidu(query, num)
        elif engine == "bing":
            return self._search_bing(query, num)
        else:
            return [{"error": f"不支持的搜索引擎: {engine}"}]

    def _search_duckduckgo(self, query: str, num: int) -> list:
        """DuckDuckGo HTML 搜索（无需 API key）"""
        try:
            import requests
            from bs4 import BeautifulSoup
            resp = requests.get(
                "https://html.duckduckgo.com/html/",
                params={"q": query},
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=15,
            )
            soup = BeautifulSoup(resp.text, "lxml")
            results = []
            for r in soup.select(".result__body")[:num]:
                title_el = r.select_one(".result__title a")
                snippet_el = r.select_one(".result__snippet")
                if title_el:
                    results.append({
                        "title": title_el.get_text(strip=True),
                        "url": title_el.get("href", ""),
                        "snippet": snippet_el.get_text(strip=True) if snippet_el else "",
                    })
            return results
        except Exception as e:
            return [{"error": f"DuckDuckGo 搜索失败: {e}"}]

    def _search_baidu(self, query: str, num: int) -> list:
        """百度搜索"""
        try:
            import requests
            from bs4 import BeautifulSoup
            resp = requests.get(
                "https://www.baidu.com/s",
                params={"wd": query, "rn": num},
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=15,
            )
            soup = BeautifulSoup(resp.text, "lxml")
            results = []
            for r in soup.select(".result")[:num]:
                title_el = r.select_one("h3 a")
                snippet_el = r.select_one(".c-abstract")
                if title_el:
                    results.append({
                        "title": title_el.get_text(strip=True),
                        "url": title_el.get("href", ""),
                        "snippet": snippet_el.get_text(strip=True) if snippet_el else "",
                    })
            return results
        except Exception as e:
            return [{"error": f"百度搜索失败: {e}"}]

    def _search_bing(self, query: str, num: int) -> list:
        """必应搜索"""
        try:
            import requests
            from bs4 import BeautifulSoup
            resp = requests.get(
                "https://www.bing.com/search",
                params={"q": query, "count": num},
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=15,
            )
            soup = BeautifulSoup(resp.text, "lxml")
            results = []
            for r in soup.select(".b_algo")[:num]:
                title_el = r.select_one("h2 a")
                snippet_el = r.select_one(".b_caption p")
                if title_el:
                    results.append({
                        "title": title_el.get_text(strip=True),
                        "url": title_el.get("href", ""),
                        "snippet": snippet_el.get_text(strip=True) if snippet_el else "",
                    })
            return results
        except Exception as e:
            return [{"error": f"必应搜索失败: {e}"}]

    # ─── 子域名枚举 ───

    def subdomain_enum(self, domain: str, tool: str = "subfinder") -> list:
        """子域名枚举"""
        try:
            import subprocess
            import json as j
            if tool == "subfinder":
                result = subprocess.run(
                    ["subfinder", "-d", domain, "-silent"],
                    capture_output=True, text=True, timeout=60
                )
                if result.returncode == 0:
                    return [s.strip() for s in result.stdout.split("\n") if s.strip()]
                return [f"subfinder 错误: {result.stderr[:200]}"]
            else:
                return [f"不支持的工具: {tool}"]
        except FileNotFoundError:
            return ["需要安装 subfinder: go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest"]
        except Exception as e:
            return [f"子域名枚举失败: {e}"]

    # ─── 网站 OSINT 分析 ───

    def analyze_website(self, domain: str) -> dict:
        """网站基础 OSINT 分析"""
        import socket
        import ssl
        result = {}
        try:
            result["ip"] = socket.gethostbyname(domain)
        except:
            result["ip"] = "解析失败"
        try:
            cert = ssl.get_server_certificate((domain, 443))
            result["ssl"] = "有效" if cert else "无"
        except:
            result["ssl"] = "无法获取"
        try:
            result["whois"] = f"whois {domain} (需安装 whois 命令行)"  # 占位
        except:
            pass
        return result

    # ─── 用户名搜索 ───

    def username_search(self, username: str) -> list:
        """按用户名搜索社交账号（对接 sherlock 逻辑）"""
        try:
            import subprocess
            result = subprocess.run(
                ["sherlock", username, "--output", "/dev/null"],
                capture_output=True, text=True, timeout=120
            )
            lines = result.stdout.split("\n")
            found = [l for l in lines if "[+]" in l]
            return found if found else ["sherlock 未找到或需安装"]
        except FileNotFoundError:
            return ["需要安装 sherlock: pip install sherlock-project"]
        except Exception as e:
            return [f"用户名搜索失败: {e}"]