"""任务与结果的数据模型"""

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class Task:
    """一个待处理的任务单元"""
    id: str
    content: str                    # 任务描述
    agent_type: Optional[str] = None  # 指定由哪类 Agent 处理
    context: dict = field(default_factory=dict)  # 附加上下文
    priority: int = 0               # 优先级，越大越先

    def __post_init__(self):
        if not self.id:
            import uuid
            self.id = uuid.uuid4().hex[:8]


@dataclass
class TaskResult:
    """Agent 处理任务后的结果"""
    task_id: str
    agent_name: str
    output: Any
    status: str = "success"          # success | error | partial
    error: Optional[str] = None
    metadata: dict = field(default_factory=dict)

    def is_success(self):
        """任务是否成功完成"""
        return self.status == "success"