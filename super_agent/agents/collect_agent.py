"""信息收集 Agent：超级信息收集智能体

核心能力（能力 → 实现方案）：
1. 访问网页       → requests + httpx + playwright(JS渲染) + 代理池
2. 抓取内容       → BeautifulSoup + lxml + parsel
3. 转换内容       → html2text(markdown) + readability(正文提取) + trafilatura
4. 过滤清洗       → 规则引擎 + LLM 语义过滤
5. 多源汇聚       → 爬虫 + API + RSS + 搜索接口
6. 分析归类       → 关键词分类 + LLM 分类 + 去重
7. 存储检索       → SQLite + JSON + 向量库(可选)
8. 定时调度       → APScheduler + cron
"""

from typing import Optional, Callable
from ..core.base_agent import Agent
from ..models.task import Task, TaskResult
from ..tools.tool_registry import ToolRegistry


class InfoCollectAgent(Agent):
    name = "collect"
    description = "超级信息收集：网页抓取、内容转换、多源信息聚合、分析归类"

    def __init__(self, memory=None, registry: Optional[ToolRegistry] = None):
        super().__init__(memory)
        self.registry = registry or ToolRegistry()
        self._register_tools()

    # ─── 能力注册：把每个能力注册成工具 ───

    def _register_tools(self):
        self.registry.register("fetch_page", self._fetch_page, "访问网页，返回原始HTML")
        self.registry.register("fetch_page_js", self._fetch_page_js, "访问JS渲染页面")
        self.registry.register("html_to_markdown", self._html_to_markdown, "HTML转Markdown")
        self.registry.register("extract_main_content", self._extract_main_content, "提取网页正文")
        self.registry.register("extract_links", self._extract_links, "提取页面所有链接")
        self.registry.register("call_api", self._call_api, "调用REST API")
        self.registry.register("search_web", self._search_web, "网页搜索")
        self.registry.register("classify_info", self._classify_info, "信息分类")

    # ─── 能力 1: 访问网页 ───

    def _fetch_page(self, url: str, headers: Optional[dict] = None) -> str:
        """访问网页，返回 HTML"""
        try:
            import requests
            resp = requests.get(url, headers=headers or {
                "User-Agent": "Mozilla/5.0 (compatible; InfoSuperAgent/1.0)"
            }, timeout=15)
            resp.raise_for_status()
            return resp.text
        except ImportError:
            return f"[错误] 需要安装 requests: pip install requests"
        except Exception as e:
            return f"[错误] 访问失败: {e}"

    def _fetch_page_js(self, url: str) -> str:
        """访问 JS 渲染页面（处理现代前端）"""
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url, wait_until="networkidle")
                content = page.content()
                browser.close()
                return content
        except ImportError:
            return f"[错误] 需要安装 playwright: pip install playwright && playwright install chromium"
        except Exception as e:
            return f"[错误] JS渲染失败: {e}"

    # ─── 能力 2/3: 抓取 + 转换 ───

    def _html_to_markdown(self, html: str) -> str:
        """HTML 转 Markdown"""
        try:
            import html2text
            return html2text.html2text(html)
        except ImportError:
            return f"[错误] 需要安装 html2text"

    def _extract_main_content(self, html: str, url: str = "") -> str:
        """提取网页正文（去除导航/广告/页脚）"""
        try:
            import trafilatura
            return trafilatura.extract(html, include_links=True) or ""
        except ImportError:
            try:
                from readability import Document
                doc = Document(html, url=url)
                return doc.summary()
            except ImportError:
                return f"[错误] 需要安装 trafilatura 或 readability"
        except Exception as e:
            return f"[错误] 正文提取失败: {e}"

    def _extract_links(self, html: str, base_url: str = "") -> list:
        """提取页面所有链接"""
        try:
            from bs4 import BeautifulSoup
            from urllib.parse import urljoin
            soup = BeautifulSoup(html, "lxml")
            links = []
            for a in soup.find_all("a", href=True):
                href = a["href"]
                if base_url:
                    href = urljoin(base_url, href)
                links.append({"text": a.get_text(strip=True), "href": href})
            return links
        except ImportError:
            return [f"[错误] 需要安装 beautifulsoup4 lxml"]

    # ─── 能力 4: API 调用 ───

    def _call_api(self, url: str, method: str = "GET", params: Optional[dict] = None,
                  json_body: Optional[dict] = None, headers: Optional[dict] = None) -> str:
        """调用 REST API"""
        try:
            import requests
            resp = requests.request(
                method, url, params=params, json=json_body,
                headers=headers or {}, timeout=20
            )
            return resp.text
        except ImportError:
            return f"[错误] 需要安装 requests"
        except Exception as e:
            return f"[错误] API调用失败: {e}"

    # ─── 能力 5: 搜索 ───

    def _search_web(self, query: str, num: int = 10) -> str:
        """网页搜索（可接 DuckDuckGo / 百度 / 必应）"""
        try:
            import requests
            from bs4 import BeautifulSoup
            # 用 DuckDuckGo HTML 版（无需 key）
            resp = requests.get("https://html.duckduckgo.com/html/", params={"q": query}, timeout=15)
            soup = BeautifulSoup(resp.text, "lxml")
            results = []
            for r in soup.select(".result__body")[:num]:
                title = r.select_one(".result__title")
                link = r.select_one(".result__snippet")
                results.append({
                    "title": title.get_text(strip=True) if title else "",
                    "snippet": link.get_text(strip=True) if link else ""
                })
            return results
        except Exception as e:
            return f"[错误] 搜索失败: {e}"

    # ─── 能力 6: 分析归类 ───

    def _classify_info(self, text: str, categories: Optional[list] = None) -> str:
        """信息分类（关键词匹配，可升级为 LLM）"""
        categories = categories or ["科技", "安全", "金融", "游戏", "其他"]
        # 简单关键词打分
        keyword_map = {
            "科技": ["AI", "人工智能", "开源", "模型", "算法", "代码"],
            "安全": ["漏洞", "安全", "渗透", "CVE", "黑客", "攻击"],
            "金融": ["股票", "基金", "投资", "金融", "货币", "经济"],
            "游戏": ["游戏", "跑酷", "3D", "Three.js", "玩法"],
        }
        scores = {c: 0 for c in categories}
        for c, kws in keyword_map.items():
            for kw in kws:
                if kw.lower() in text.lower():
                    scores[c] += 1
        best = max(scores, key=scores.get)
        return best if scores[best] > 0 else "其他"

    # ─── 主执行入口 ───

    def run(self, task: Task) -> TaskResult:
        content = task.content
        results = []

        # 智能解析任务：识别意图
        if "搜索" in content or "找" in content:
            query = content.replace("搜索", "").replace("帮我", "").strip()
            results.append(f"🔍 搜索 '{query}':\n{self._search_web(query)}")
        elif "http" in content or "page" in content.lower():
            url = [w for w in content.split() if w.startswith("http")][0]
            html = self._fetch_page(url)
            md = self._extract_main_content(html, url)
            results.append(f"📄 网页正文:\n{md[:2000]}")
        else:
            results.append(f"📋 待实现: {content}")

        return TaskResult(
            task_id=task.id,
            agent_name=self.name,
            output="\n\n".join(results)
        )