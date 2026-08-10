"""创意 Agent：文案、模板、内容创作

能力：
1. 模板生成（README/文档/报告框架）
2. 文案模板（项目介绍/PR说明）
3. 创意素材管理
"""

from typing import Optional
from ..core.base_agent import Agent
from ..models.task import Task, TaskResult


class CreativeAgent(Agent):
    name = "creative"
    description = "文案模板、文档生成、内容创作框架"

    def run(self, task: Task) -> TaskResult:
        """执行创意任务，路由到README/PR/报告模板"""
        content = task.content
        c = content.lower()

        if "readme" in c or "README" in task.content:
            return self._template_readme(content)
        if "pr" in c and ("说明" in c or "描述" in c):
            return self._template_pr(content)
        if "report" in c or "报告" in c:
            return self._template_report(content)
        if "列表" in c or "list" in c or "模板" in c:
            return self._list_templates()

        return TaskResult(
            task_id=task.id, agent_name=self.name,
            output="CreativeAgent 可用模板:\n"
                   "  • README: '生成 README 项目文档'\n"
                   "  • PR: 'PR 说明 修复了xxx'\n"
                   "  • 报告: '生成项目报告'\n"
                   "  • 列表: '查看可用模板'"
        )

    def _template_readme(self, content: str) -> TaskResult:
        out = f"""# 项目名称

## 简介
{content.replace('README', '').replace('readme', '').strip() or '项目描述'}

## 快速开始
```bash
# 安装
pip install -r requirements.txt

# 使用
python main.py
```

## 功能特性
- 特性 1
- 特性 2
- 特性 3

## 许可
MIT
"""
        return TaskResult(task_id="", agent_name=self.name, output=f"📝 README 模板\n\n{out}")

    def _template_pr(self, content: str) -> TaskResult:
        desc = content.replace("PR说明", "").replace("PR 说明", "").strip() or "本次变更"
        out = f"""## 变更说明
{desc}

## 变更类型
- [ ] 新功能
- [ ] Bug 修复
- [ ] 重构
- [ ] 文档更新

## 测试
- [ ] 本地测试通过
- [ ] 未影响现有功能
"""
        return TaskResult(task_id="", agent_name=self.name, output=f"📋 PR 说明模板\n\n{out}")

    def _template_report(self, content: str) -> TaskResult:
        out = f"""# 项目报告

## 概述
{content.replace('报告', '').strip() or '项目概况'}

## 进度
- [ ] 阶段 1
- [ ] 阶段 2
- [ ] 阶段 3

## 问题
- 

## 下一步
- 
"""
        return TaskResult(task_id="", agent_name=self.name, output=f"📊 报告模板\n\n{out}")

    def _list_templates(self) -> TaskResult:
        return TaskResult(task_id="", agent_name=self.name,
                          output="📋 可用模板列表:\n\n"
                                 "  • README 模板 — '生成 README'\n"
                                 "  • PR 说明模板 — 'PR 说明 xxx'\n"
                                 "  • 报告模板 — '生成报告 xxx'\n"
                                 "  • 项目文档模板" + "（待添加）")