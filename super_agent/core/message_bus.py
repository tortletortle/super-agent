"""消息总线：Agent 间的通信通道"""

from typing import Any, Optional
from ..models.task import Task, TaskResult


class MessageBus:
    """Agent 间的发布/订阅通信"""

    def __init__(self):
        self._subscribers: dict[str, list] = {}
        self._history: list = []

    def subscribe(self, event_type: str, callback):
        """订阅某类事件"""
        self._subscribers.setdefault(event_type, []).append(callback)

    def publish(self, event_type: str, data: Any):
        """发布事件，通知所有订阅者"""
        self._history.append((event_type, data))
        for cb in self._subscribers.get(event_type, []):
            cb(data)

    def broadcast(self, task: Task, result: TaskResult):
        """广播任务完成事件"""
        self.publish("task_completed", {"task": task, "result": result})

    def get_history(self, event_type: Optional[str] = None) -> list:
        """获取历史事件"""
        if event_type:
            return [(t, d) for t, d in self._history if t == event_type]
        return self._history.copy()