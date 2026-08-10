"""游戏 Agent：游戏开发、3D 场景搭建"""

from typing import Optional
from ..core.base_agent import Agent
from ..models.task import Task, TaskResult


class GameAgent(Agent):
    name = "game"
    description = "Three.js 游戏开发、3D 场景、超休闲游戏"

    def run(self, task: Task) -> TaskResult:
        return TaskResult(
            task_id=task.id,
            agent_name=self.name,
            output=f"GameAgent 已接收任务: {task.content}\n待接入 Three.js 生成逻辑"
        )