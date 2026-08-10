"""共享记忆：Agent 间的知识传递"""

from typing import Optional


class SharedMemory(dict):
    """所有 Agent 共享的上下文记忆，本质就是一个增强的 dict"""

    def __init__(self, initial: Optional[dict] = None):
        super().__init__(initial or {})

    def remember(self, key: str, value):
        """存入记忆"""
        self[key] = value

    def recall(self, key: str, default=None):
        """取出记忆"""
        return self.get(key, default)

    def merge(self, data: dict):
        """批量合并"""
        self.update(data)

    def snapshot(self) -> dict:
        """返回当前记忆快照"""
        return dict(self)