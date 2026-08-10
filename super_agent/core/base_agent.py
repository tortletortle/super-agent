"""Agent 基类：所有专业 Agent 的父类"""

from abc import ABC, abstractmethod
from typing import Optional
from ..models.task import Task, TaskResult


class Agent(ABC):
    """所有专业 Agent 的抽象基类"""

    name: str = "agent"            # Agent 唯一标识
    description: str = ""          # 描述它能做什么
    version: str = "0.1.0"

    def __init__(self, memory: Optional[dict] = None):
        self.memory = memory or {}  # 共享记忆

    @abstractmethod
    def run(self, task: Task) -> TaskResult:
        """执行任务，返回结果（子类必须实现）"""
        ...

    def can_handle(self, task: Task) -> bool:
        """判断是否适合处理此任务（可被子类重写）"""
        return True

    def __repr__(self):
        return f"<{self.__class__.__name__}({self.name})>"