"""安全漏洞扫描示例"""

from super_agent.core import SuperAgent
from super_agent.agents import SecurityAgent, ResearchAgent

def main():
    agent = SuperAgent(name="SecurityScanner")
    agent.register_agent(SecurityAgent())
    agent.register_agent(ResearchAgent())

    # 安全扫描工作流
    target = input("请输入目标域名: ")

    result = agent.run(f"""
    对 {target} 进行安全评估：
    1. ResearchAgent: 收集子域名、端口、技术栈信息
    2. SecurityAgent: 扫描常见漏洞（SQL注入、XSS、SSRF等）
    3. 汇总报告
    """)

    print("\n" + "="*50)
    print(result.output)

if __name__ == "__main__":
    main()