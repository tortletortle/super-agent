"""工具注册表：所有 Agent 可调用的工具"""


class ToolRegistry:
    """全局工具注册表，管理所有可用工具"""

    def __init__(self):
        self._tools: dict[str, callable] = {}

    def register(self, name: str, fn: callable, description: str = ""):
        """注册一个工具"""
        self._tools[name] = {"fn": fn, "description": description}

    def get(self, name: str):
        """获取已注册的工具"""
        return self._tools.get(name)

    def list(self) -> dict:
        """列出所有已注册的工具及其描述"""
        return {k: v["description"] for k, v in self._tools.items()}

    def call(self, name: str, *args, **kwargs):
        """调用已注册的工具"""
        tool = self.get(name)
        if not tool:
            raise ValueError(f"工具 '{name}' 未注册")
        return tool["fn"](*args, **kwargs)