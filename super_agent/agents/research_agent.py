"""研究 Agent：信息检索、调研、知识收集"""

from typing import Optional
from ..core.base_agent import Agent
from ..models.task import Task, TaskResult


class ResearchAgent(Agent):
    name = "research"
    description = "联网搜索、信息收集、技术调研"

    def run(self, task: Task) -> TaskResult:
        return TaskResult(
            task_id=task.id,
            agent_name=self.name,
            output=f"ResearchAgent 已接收任务: {task.content}\n待接入搜索 API 实现联网检索"
        )