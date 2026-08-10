"""Super Agent 简单使用示例"""

from super_agent.core import SuperAgent
from super_agent.agents import CodeAgent, ResearchAgent, SecurityAgent, DataAgent

def main():
    # 1. 创建超级智能体
    agent = SuperAgent(name="MySuperAgent")

    # 2. 注册专业 Agent
    for AgentClass in [CodeAgent, ResearchAgent, SecurityAgent, DataAgent]:
        agent.register_agent(AgentClass())

    print(f"已注册 Agent: {agent.list_agents()}\n")

    # 3. 提交任务
    tasks = [
        "帮我写一个 Python 爬虫",
        "扫描这个网站是否存在 SQL 注入漏洞 website.com",
        "分析这份销售数据",
    ]

    for t in tasks:
        print(f"\n{'='*50}")
        print(f"📋 任务: {t}")
        result = agent.run(t)
        print(f"✅ 结果: {result.output[:200]}...")

if __name__ == "__main__":
    main()