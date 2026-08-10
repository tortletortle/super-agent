"""SuperAgent 编排器：超级智能体的大脑"""

import uuid
from typing import Optional
from ..models.task import Task, TaskResult
from .base_agent import Agent
from .message_bus import MessageBus
from .memory import SharedMemory


class SuperAgent:
    """
    超级智能体编排器。

    职责：
    1. 接收用户任务
    2. 分解任务为子任务
    3. 按类型路由到专业 Agent
    4. 汇总结果
    5. 动态编排：支持串行、并行、条件分支
    """

    def __init__(self, name: str = "SuperAgent"):
        self.name = name
        self.memory = SharedMemory()
        self.bus = MessageBus()
        self._agents: dict[str, Agent] = {}

    # ─── Agent 注册 ───

    def register_agent(self, agent: Agent):
        """注册一个专业 Agent"""
        agent.memory = self.memory
        self._agents[agent.name] = agent
        self.bus.subscribe("task_completed", self._on_task_completed)

    def get_agent(self, name: str) -> Optional[Agent]:
        return self._agents.get(name)

    def list_agents(self) -> list[str]:
        return list(self._agents.keys())

    # ─── 任务执行 ───

    def run(self, task_content: str, context: Optional[dict] = None) -> TaskResult:
        """
        主入口：接收自然语言任务，自动分解并执行。
        """
        # 1. 创建主任务
        main_task = Task(
            id=uuid.uuid4().hex[:8],
            content=task_content,
            context=context or {},
            priority=10
        )

        # 2. 分解任务
        sub_tasks = self._decompose(main_task)

        # 3. 执行每个子任务
        results = []
        for sub in sub_tasks:
            result = self._dispatch(sub)
            results.append(result)

        # 4. 汇总结果
        return self._synthesize(main_task, results)

    def _decompose(self, task: Task) -> list[Task]:
        """
        任务分解：分析任务内容，拆成多个子任务。
        简单策略：根据任务关键词匹配 Agent 类型。
        高级策略可接入 LLM 做语义分解。
        """
        content = task.content.lower()
        keywords = {
            "code": ["写代码", "修复", "编程", "实现", "开发", "code", "bug", "重构"],
            "research": ["研究", "调研", "research"],
            "collect": ["搜索", "搜", "查询", "找", "收集", "采集", "抓取", "爬取",
                        "信息", "数据", "collect", "scrape", "search", "访问",
                        "打开", "http", "子域名", "用户名", "rss", "订阅",
                        "新闻", "视频", "监控", "定时", "保存", "存储", "导出",
                        "分析", "归类", "分类"],
            "security": ["漏洞", "扫描", "安全", "渗透", "注入", "security", "vuln"],
            "creative": ["设计", "创意", "文案", "写", "创作", "创意", "design"],
            "data": ["分析", "数据", "统计", "图表", "可视化", "data", "csv"],
            "game": ["游戏", "three.js", "3d", "game", "跑酷"],
            "system": ["部署", "安装", "配置", "运维", "deploy", "docker"],
        }

        sub_tasks = []
        for agent_type, kws in keywords.items():
            if any(kw in content for kw in kws):
                sub_tasks.append(Task(
                    id=f"{task.id}_{agent_type}",
                    content=task.content,
                    agent_type=agent_type,
                    context=dict(task.context),
                    priority=len(sub_tasks)
                ))

        if not sub_tasks:
            sub_tasks.append(task)

        return sub_tasks

    def _dispatch(self, task: Task) -> TaskResult:
        """根据 task.agent_type 派发到对应的 Agent"""
        if not task.agent_type:
            return TaskResult(
                task_id=task.id, agent_name="orchestrator",
                output=f"无法确定任务类型: {task.content}",
                status="error"
            )

        # 匹配已注册的 Agent
        agent = self._agents.get(task.agent_type)
        if not agent:
            return TaskResult(
                task_id=task.id, agent_name="orchestrator",
                output=f"没有找到类型为 {task.agent_type} 的 Agent",
                status="error"
            )

        # 执行
        result = agent.run(task)
        self.bus.broadcast(task, result)
        return result

    def _on_task_completed(self, event):
        """任务完成回调（可扩展）"""
        pass

    def _synthesize(self, main_task: Task, results: list[TaskResult]) -> TaskResult:
        """汇总所有子任务的结果"""
        success = sum(1 for r in results if r.is_success())
        total = len(results)

        combined = f"## 任务完成汇总\n\n"
        combined += f"主任务: {main_task.content}\n"
        combined += f"完成: {success}/{total}\n\n"

        for r in results:
            status_icon = "✅" if r.is_success() else "❌"
            combined += f"{status_icon} **[{r.agent_name}]** {r.output}\n\n"

        return TaskResult(
            task_id=main_task.id,
            agent_name=self.name,
            output=combined,
            status="success" if success == total else "partial",
            metadata={"total": total, "success": success, "results": results}
        )