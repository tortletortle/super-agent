"""研究 Agent：联网搜索、技术调研、知识收集

复用 SearchDiscovery 能力：
- 多引擎网页搜索
- 用户名搜索（OSINT）
- 子域名枚举
"""

from typing import Optional
from ..core.base_agent import Agent
from ..models.task import Task, TaskResult
from ..capabilities.search_discovery import SearchDiscovery


class ResearchAgent(Agent):
    name = "research"
    description = "联网搜索、技术调研、OSINT 信息收集"

    def __init__(self, memory=None):
        super().__init__(memory)
        self.search = SearchDiscovery()

    def run(self, task: Task) -> TaskResult:
        """执行研究任务，路由到搜索/用户名/子域名"""
        content = task.content
        c = content.lower()

        if "用户名" in c or "找人" in c or "username" in c:
            return self._username_search(content)
        if "子域名" in c or "subdomain" in c:
            return self._subdomain_search(content)
        if "搜索" in c or "search" in c or "找" in c:
            return self._web_search(content)

        return self._web_search(content)

    def _web_search(self, content: str) -> TaskResult:
        query = content
        for prefix in ["搜索", "搜 ", "帮我搜", "research", "调研", "找一下", "查一下"]:
            query = query.replace(prefix, "")
        query = query.strip().strip('"').strip("'")

        out = [f"🔍 研究: {query}", ""]
        results = self.search.search_web(query, engine="duckduckgo", num=10)
        valid = [r for r in results if "error" not in r]
        if valid:
            out.append(f"【DuckDuckGo】共 {len(valid)} 条:")
            for r in valid[:10]:
                out.append(f"  📌 {r['title']}")
                out.append(f"     {r.get('url', '')}")
                if r.get("snippet"):
                    out.append(f"     {r['snippet'][:150]}")
                out.append("")
        else:
            out.append("⚠️ 搜索无结果或失败")

        return TaskResult(
            task_id=task.id, agent_name=self.name,
            output="\n".join(out)
        )

    def _username_search(self, content: str) -> TaskResult:
        words = content.split()
        username = [w for w in words if not any(k in w for k in ["搜索", "用户名", "找人", "username"])]
        if not username:
            return TaskResult(task_id="", agent_name=self.name,
                              output="⚠️ 请提供用户名", status="error")
        username = username[-1].strip()
        out = [f"👤 用户名搜索: {username}", ""]
        results = self.search.username_search(username)
        for r in results:
            out.append(f"  • {r}")
        return TaskResult(task_id="", agent_name=self.name, output="\n".join(out))

    def _subdomain_search(self, content: str) -> TaskResult:
        import re
        domains = re.findall(r'[\w\-\.]+\.\w+', content)
        if not domains:
            return TaskResult(task_id="", agent_name=self.name,
                              output="⚠️ 请提供域名", status="error")
        domain = domains[0]
        out = [f"🔎 子域名枚举: {domain}", ""]
        subs = self.search.subdomain_enum(domain)
        out.append(f"找到 {len(subs)} 个子域名:")
        for s in subs[:30]:
            out.append(f"  • {s}")
        return TaskResult(task_id="", agent_name=self.name, output="\n".join(out))