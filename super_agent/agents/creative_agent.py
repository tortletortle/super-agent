"""创意 Agent：文案、设计、内容创作"""

from typing import Optional
from ..core.base_agent import Agent
from ..models.task import Task, TaskResult


class CreativeAgent(Agent):
    name = "creative"
    description = "文案撰写、创意设计、内容创作"

    def run(self, task: Task) -> TaskResult:
        return TaskResult(
            task_id=task.id,
            agent_name=self.name,
            output=f"CreativeAgent 已接收任务: {task.content}\n待接入 LLM 实现创意生成"
        )