"""系统 Agent：运维、部署、配置管理"""

from typing import Optional
from ..core.base_agent import Agent
from ..models.task import Task, TaskResult


class SystemAgent(Agent):
    name = "system"
    description = "系统部署、Docker 编排、环境配置、运维"

    def run(self, task: Task) -> TaskResult:
        return TaskResult(
            task_id=task.id,
            agent_name=self.name,
            output=f"SystemAgent 已接收任务: {task.content}\n待接入 Docker/SSH 实现自动化运维"
        )