"""SuperAgent 单元测试"""

import sys
sys.path.insert(0, "..")

from super_agent.core import SuperAgent
from super_agent.agents import CodeAgent, ResearchAgent


def test_super_agent_creation():
    agent = SuperAgent("TestAgent")
    assert agent.name == "TestAgent"
    assert len(agent.list_agents()) == 0


def test_register_agent():
    agent = SuperAgent()
    agent.register_agent(CodeAgent())
    assert "code" in agent.list_agents()


def test_agent_run():
    agent = SuperAgent()
    agent.register_agent(CodeAgent())
    result = agent.run("写一个 Python 函数")
    assert result.is_success()
    assert "code" in result.output.lower() or "CodeAgent" in result.output


def test_multiple_agents():
    agent = SuperAgent()
    agent.register_agent(CodeAgent())
    agent.register_agent(ResearchAgent())
    assert len(agent.list_agents()) == 2

    result = agent.run("帮我写代码并搜索资料")
    assert result.is_success()


def test_task_decompose():
    agent = SuperAgent()
    from super_agent.models.task import Task
    tasks = agent._decompose(Task(content="写代码并扫描漏洞"))
    types = [t.agent_type for t in tasks if t.agent_type]
    assert "code" in types
    assert "security" in types