"""超级信息收集智能体 — 完整能力体系

9大能力：
1. 网页访问   → AntiCrawl (requests/httpx/playwright/stealth)
2. 反爬对抗   → AntiCrawl (代理池/隐身浏览器/指纹模拟)
3. 内容提取   → 内置 (trafilatura/BeautifulSoup)
4. 内容转换   → 内置 (html2text/readability)
5. 多源采集   → MultiSource (RSS/社媒/视频/API/新闻)
6. 搜索发现   → SearchDiscovery (网页/子域名/OSINT/用户名)
7. 分析归类   → 内置 (关键词/LLM/去重)
8. 定时监控   → Scheduler (APScheduler/变更检测/通知)
9. 存储检索   → Storage (SQLite+FTS5/导出/统计)
"""

from typing import Optional
from ..core.base_agent import Agent
from ..models.task import Task, TaskResult
from ..capabilities import AntiCrawl, MultiSource, SearchDiscovery, Scheduler, Storage


class InfoCollectAgent(Agent):
    name = "collect"
    description = "超级信息收集：网页访问/反爬对抗/多源采集/搜索发现/定时监控/存储检索"

    def __init__(self, memory=None):
        super().__init__(memory)
        # 初始化所有能力
        self.anti_crawl = AntiCrawl()
        self.multi_source = MultiSource()
        self.search_discovery = SearchDiscovery()
        self.scheduler = Scheduler()
        self.storage = Storage()

    def run(self, task: Task) -> TaskResult:
        """智能识别任务意图并路由到对应能力"""
        content = task.content
        context = task.context

        # 意图识别
        intent = self._detect_intent(content)
        result = None

        if intent == "search":
            result = self._handle_search(content)
        elif intent == "fetch":
            result = self._handle_fetch(content)
        elif intent == "rss":
            result = self._handle_rss(content)
        elif intent == "news":
            result = self._handle_news(content)
        elif intent == "video":
            result = self._handle_video(content)
        elif intent == "subdomain":
            result = self._handle_subdomain(content)
        elif intent == "username":
            result = self._handle_username(content)
        elif intent == "analyze":
            result = self._handle_analyze(content)
        elif intent == "schedule":
            result = self._handle_schedule(content)
        elif intent == "storage":
            result = self._handle_storage(content)
        else:
            # 智能综合处理
            result = self._handle_comprehensive(content)

        return TaskResult(
            task_id=task.id,
            agent_name=self.name,
            output=result
        )

    def _detect_intent(self, content: str) -> str:
        c = content.lower()
        if "子域名" in c or "subdomain" in c:
            return "subdomain"
        if "用户名" in c or "username" in c or "找人" in c:
            return "username"
        if any(kw in c for kw in ["搜索", "搜 ", "搜一个", "搜一下", "查一下", "找一下", "search"]):
            return "search"
        if any(kw in c for kw in ["访问", "打开", "fetch", "http", "网页"]):
            return "fetch"
        if "rss" in c or "订阅" in c:
            return "rss"
        if "新闻" in c or "news" in c:
            return "news"
        if "视频" in c or "video" in c or "youtube" in c or "b站" in c:
            return "video"
        if any(kw in c for kw in ["分析", "归类", "classify", "分类"]):
            return "analyze"
        if any(kw in c for kw in ["定时", "监控", "每", "每天", "schedule", "cron"]):
            return "schedule"
        if any(kw in c for kw in ["保存", "存储", "导出", "检索", "search", "查询历史"]):
            return "storage"
        return "comprehensive"

    # ─── 各意图处理 ───

    def _handle_search(self, content: str) -> str:
        """处理搜索请求"""
        # 提取搜索词
        query = content
        for prefix in ["搜索", "搜 ", "搜一下", "查一下", "找一下", "search", "search for"]:
            query = query.replace(prefix, "")
        query = query.strip().strip('"').strip("'")

        output = [f"🔍 搜索: {query}", ""]

        # 多引擎搜索
        output.append("【DuckDuckGo】")
        results = self.search_discovery.search_web(query, engine="duckduckgo")
        for r in results[:5]:
            if "error" in r:
                output.append(f"  ⚠️ {r['error']}")
            else:
                output.append(f"  📌 {r['title']}")
                output.append(f"     {r.get('url', '')}")
                output.append(f"     {r.get('snippet', '')[:100]}")
            output.append("")

        # 可选百度搜索
        output.append("【百度】")
        baidu = self.search_discovery.search_web(query, engine="baidu")
        for r in baidu[:3]:
            if "error" in r:
                output.append(f"  ⚠️ {r['error']}")
            else:
                output.append(f"  📌 {r['title']}")
            output.append("")

        return "\n".join(output)

    def _handle_fetch(self, content: str) -> str:
        """处理网页访问"""
        # 提取URL
        words = content.split()
        urls = [w for w in words if w.startswith("http")]
        if not urls:
            return "❌ 未找到 URL，请提供要访问的网页地址"

        url = urls[0]
        output = [f"📄 访问: {url}", ""]

        # 隐身访问（带反爬）
        html = self.anti_crawl.stealth_fetch(url, render_js="js" in content or "渲染" in content)

        if html.startswith("[反爬]") or html.startswith("[错误]"):
            output.append(html)
            return "\n".join(output)

        # 提取正文
        try:
            import trafilatura
            text = trafilatura.extract(html, include_links=True)
            if text:
                output.append(f"📝 正文 ({len(text)} 字符):")
                output.append(text[:2000])
            else:
                output.append("⚠️ 未能提取正文，可能是 JS 渲染页面，试试加 '渲染' 关键词")
        except ImportError:
            output.append(html[:2000])

        return "\n".join(output)

    def _handle_rss(self, content: str) -> str:
        """处理 RSS 采集"""
        words = content.split()
        urls = [w for w in words if w.startswith("http")]
        if not urls:
            return "❌ 请提供 RSS 订阅地址"

        entries = self.multi_source.fetch_rss(urls[0])
        if not entries:
            return "⚠️ 未获取到 RSS 条目"

        output = [f"📡 RSS: {urls[0]}", f"共 {len(entries)} 条", ""]
        for e in entries[:10]:
            if "error" in e:
                output.append(f"⚠️ {e['error']}")
            else:
                output.append(f"📌 {e['title']}")
                output.append(f"   {e.get('link', '')}")
                output.append(f"   {e.get('published', '')}")
                output.append("")
        return "\n".join(output)

    def _handle_news(self, content: str) -> str:
        """处理新闻提取"""
        words = content.split()
        urls = [w for w in words if w.startswith("http")]
        if not urls:
            return "❌ 请提供新闻文章 URL"

        news = self.multi_source.extract_news(urls[0])
        if "error" in news:
            return f"⚠️ {news['error']}"

        output = [
            f"📰 {news.get('title', '')}",
            f"👤 作者: {', '.join(news.get('authors', []) or ['未知'])}",
            f"📅 日期: {news.get('publish_date', '未知')}",
            f"🏷️ 关键词: {', '.join(news.get('keywords', []) or ['无'])}",
            "",
            news.get('text', '')[:2000],
        ]
        return "\n".join(output)

    def _handle_video(self, content: str) -> str:
        """处理视频信息"""
        words = content.split()
        urls = [w for w in words if w.startswith("http")]
        if not urls:
            return "❌ 请提供视频 URL"

        info = self.multi_source.fetch_video_info(urls[0])
        if "error" in info:
            return f"⚠️ {info['error']}"

        from datetime import timedelta
        duration = timedelta(seconds=info.get("duration", 0))
        output = [
            f"🎬 {info.get('title', '')}",
            f"👤 上传者: {info.get('uploader', '未知')}",
            f"⏱️ 时长: {duration}",
            f"👁️ 播放: {info.get('view_count', 0):,}",
            f"👍 点赞: {info.get('like_count', 0):,}",
            "",
            info.get('description', '')[:500],
        ]
        return "\n".join(output)

    def _handle_subdomain(self, content: str) -> str:
        """处理子域名枚举"""
        import re
        domains = re.findall(r'[\w\-\.]+\.\w+', content)
        if not domains:
            return "❌ 请提供域名（如 example.com）"

        domain = domains[0]
        output = [f"🔎 子域名枚举: {domain}", ""]
        subs = self.search_discovery.subdomain_enum(domain)
        output.append(f"找到 {len(subs)} 个子域名:")
        for s in subs[:30]:
            output.append(f"  • {s}")
        return "\n".join(output)

    def _handle_username(self, content: str) -> str:
        """处理用户名搜索"""
        words = content.split()
        # 提取用户名（最后一个词）
        username = [w for w in words if not any(kw in w for kw in ["搜索", "用户名", "找人", "username"])]
        if not username:
            return "❌ 请提供用户名"
        username = username[-1].strip()

        output = [f"👤 用户名搜索: {username}", ""]
        results = self.search_discovery.username_search(username)
        for r in results:
            output.append(f"  • {r}")
        return "\n".join(output)

    def _handle_analyze(self, content: str) -> str:
        """处理信息分析归类"""
        return "📊 信息分析归类能力\n\n分类引擎: 关键词 + LLM（待接入）\n支持的分类: 科技、安全、金融、游戏、其他"

    def _handle_schedule(self, content: str) -> str:
        """处理定时监控"""
        return "⏰ 定时监控能力\n\n需指定: 采集任务 + 间隔分钟\n示例: '每30分钟监控这个网站'"

    def _handle_storage(self, content: str) -> str:
        """处理存储检索"""
        c = content.lower()
        if "统计" in c or "stats" in c:
            stats = self.storage.stats()
            return f"📊 存储统计\n\n总计: {stats.get('total', 0)} 条\n按来源: {stats.get('by_source', {})}\n按分类: {stats.get('by_category', {})}"
        if "search" in c or "检索" in c or "查询" in c:
            query = c.replace("检索", "").replace("查询", "").replace("search", "").strip()
            results = self.storage.search(query)
            if not results:
                return f"未找到匹配 '{query}' 的结果"
            output = [f"🔍 检索 '{query}' 共 {len(results)} 条:", ""]
            for r in results[:10]:
                output.append(f"📌 {r.get('title', '无标题')}")
                output.append(f"   来源: {r.get('source', '未知')} | {r.get('collected_at', '')}")
                output.append("")
            return "\n".join(output)
        return "💾 存储检索能力\n\n功能: 保存数据 / 全文搜索 / 导出JSON / 统计"

    def _handle_comprehensive(self, content: str) -> str:
        """综合处理：无法明确意图时，自动各能力尝试"""
        output = [
            f"🤖 超级信息收集智能体",
            f"任务: {content}",
            "",
            "可用能力:",
            "  🔍 搜索 — 多引擎网页搜索",
            "  📄 访问 — 隐身访问网页",
            "  📡 RSS — 订阅源采集",
            "  📰 新闻 — 新闻全文提取",
            "  🎬 视频 — 视频元数据",
            "  🔎 子域名 — 子域名枚举",
            "  👤 用户名 — 社交账号搜索",
            "  📊 分析 — 信息归类",
            "  ⏰ 定时 — 定时监控",
            "  💾 存储 — 数据持久化检索",
            "",
            "使用示例:",
            "  '搜索 AI 开源项目'",
            "  '访问 https://example.com'",
            "  'RSS https://example.com/rss'",
            "  '子域名 example.com'",
            "  '用户名 sherlock'",
        ]
        return "\n".join(output)