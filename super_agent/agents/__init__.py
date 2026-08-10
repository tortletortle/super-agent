"""专业 Agent 注册入口"""
from .code_agent import CodeAgent
from .research_agent import ResearchAgent
from .security_agent import SecurityAgent
from .creative_agent import CreativeAgent
from .data_agent import DataAgent
from .game_agent import GameAgent
from .system_agent import SystemAgent

ALL_AGENTS = [
    CodeAgent,
    ResearchAgent,
    SecurityAgent,
    CreativeAgent,
    DataAgent,
    GameAgent,
    SystemAgent,
]

__all__ = [
    "CodeAgent", "ResearchAgent", "SecurityAgent",
    "CreativeAgent", "DataAgent", "GameAgent", "SystemAgent",
    "ALL_AGENTS",
]