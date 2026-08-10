"""工具注册表：所有 Agent 可调用的工具"""


class ToolRegistry:
    """全局工具注册表，管理所有可用工具"""

    def __init__(self):
        self._tools: dict[str, callable] = {}

    def register(self, name: str, fn: callable, description: str = ""):
        self._tools[name] = {"fn": fn, "description": description}

    def get(self, name: str):
        return self._tools.get(name)

    def list(self) -> dict:
        return {k: v["description"] for k, v in self._tools.items()}

    def call(self, name: str, *args, **kwargs):
        tool = self.get(name)
        if not tool:
            raise ValueError(f"工具 '{name}' 未注册")
        return tool["fn"](*args, **kwargs)