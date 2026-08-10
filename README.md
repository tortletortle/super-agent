# Super Agent — 超级智能体框架

一个模块化、可扩展的多智能体编排框架。把多个专业小智能体（Agent）拼装成一个能处理任何任务的超级智能体（Super Agent）。

## 核心思想

不做一个"万能的巨兽"，而是管理一群**各司其职的专业 Agent**，由一个 **Orchestrator（编排器）** 统一调度：

- **任务分解**：把大任务拆成可并行/串行的小子任务
- **路由分发**：按子任务类型派发给最合适的专业 Agent
- **结果汇总**：收集各 Agent 结果，合成最终答案
- **记忆共享**：所有 Agent 共享上下文字典，跨任务协作

## 架构

```
┌─────────────────────────────────────────────┐
│              Super Agent (Orchestrator)      │
│  接收任务 → 分解 → 路由 → 汇总 → 输出       │
└──────────────┬──────────────────────────────┘
               │ 消息总线 (MessageBus)
   ┌───────────┼───────────┬───────────┐
   ▼           ▼           ▼           ▼
 CodeAgent  ResearchAgt  SecurityAgt  CreativeAgt
   │           │           │           │
   ▼           ▼           ▼           ▼
 DataAgent  GameAgent   SystemAgent  ...(可扩展)
```

## 快速开始

```bash
# 安装
git clone https://github.com/tortletortle/super-agent.git
cd super-agent
pip install -r requirements.txt

# 运行示例
python examples/simple_workflow.py
```

## 自定义 Agent

```python
from super_agent.core.base_agent import Agent

class MyAgent(Agent):
    name = "my_agent"

    def run(self, task):
        return f"处理了任务: {task.content}"
```

## 许可

MIT