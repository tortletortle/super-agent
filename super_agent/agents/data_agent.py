"""数据 Agent：数据分析、可视化、统计

能力：
1. CSV/JSON 数据加载与统计摘要
2. 数据过滤与基本分析（pandas）
3. 图表生成（matplotlib，可选）
"""

import os
import subprocess
import json
from typing import Optional
from ..core.base_agent import Agent
from ..models.task import Task, TaskResult


class DataAgent(Agent):
    name = "data"
    description = "数据分析、CSV处理、统计摘要、可视化"

    def run(self, task: Task) -> TaskResult:
        content = task.content
        c = content.lower()

        if "csv" in c or "文件" in c or "load" in c or "读取" in c:
            return self._load_and_analyze(content)
        if "统计" in c or "summary" in c or "describe" in c:
            return self._load_and_analyze(content)
        if "图表" in c or "plot" in c or "可视化" in c or "chart" in c:
            return self._plot(content)
        if "json" in c:
            return self._load_and_analyze(content)

        return TaskResult(
            task_id=task.id, agent_name=self.name,
            output="DataAgent 可用能力:\n"
                   "  • 分析CSV: '分析 data.csv'\n"
                   "  • 统计摘要: '统计 sales.csv'\n"
                   "  • 可视化: '图表 数据.csv'\n"
                   "  • 数据分析: '分析 /path/to/data.csv'"
        )

    def _load_and_analyze(self, content: str) -> TaskResult:
        import re
        fname = re.search(r'[\w\-/\.]+\.(csv|json|xlsx?)', content)
        if not fname:
            return TaskResult(task_id="", agent_name=self.name,
                              output="⚠️ 未找到数据文件（支持 .csv / .json）", status="error")
        path = fname.group(0)
        if not os.path.exists(path):
            return TaskResult(task_id="", agent_name=self.name,
                              output=f"⚠️ 文件不存在: {path}", status="error")
        try:
            import pandas as pd
            if path.endswith(".csv"):
                df = pd.read_csv(path)
            elif path.endswith(".json"):
                df = pd.read_json(path)
            else:
                return TaskResult(task_id="", agent_name=self.name,
                                  output="⚠️ 仅支持 .csv 和 .json", status="error")

            import io
            buf = io.StringIO()
            df.info(buf=buf)
            info = buf.getvalue()
            desc = df.describe(include="all").to_string()
            cols = ", ".join(df.columns.tolist())
            sample = df.head(5).to_string()

            return TaskResult(
                task_id="", agent_name=self.name,
                output=f"📊 数据分析: {path}\n"
                       f"  行数: {len(df)} | 列数: {len(df.columns)}\n"
                       f"  列: {cols}\n\n"
                       f"【统计摘要】\n{desc[:2000]}\n\n"
                       f"【前5行】\n{sample[:2000]}"
            )
        except ImportError:
            return TaskResult(task_id="", agent_name=self.name,
                              output="需要 pandas: pip install pandas", status="error")
        except Exception as e:
            return TaskResult(task_id="", agent_name=self.name,
                              output=f"❌ 分析失败: {e}", status="error")

    def _plot(self, content: str) -> TaskResult:
        import re
        fname = re.search(r'[\w\-/\.]+\.(csv|json)', content)
        if not fname:
            return TaskResult(task_id="", agent_name=self.name,
                              output="⚠️ 请提供数据文件路径", status="error")
        path = fname.group(0)
        if not os.path.exists(path):
            return TaskResult(task_id="", agent_name=self.name,
                              output=f"⚠️ 文件不存在: {path}", status="error")
        try:
            import pandas as pd
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt

            df = pd.read_csv(path) if path.endswith(".csv") else pd.read_json(path)
            numeric_cols = df.select_dtypes(include="number").columns[:3]
            if len(numeric_cols) == 0:
                return TaskResult(task_id="", agent_name=self.name,
                                  output="⚠️ 没有数值列可画图", status="error")

            out_path = f"/tmp/plot_{os.path.basename(path)}.png"
            df[numeric_cols].hist(figsize=(10, 6))
            plt.tight_layout()
            plt.savefig(out_path, dpi=100)
            plt.close()

            return TaskResult(
                task_id="", agent_name=self.name,
                output=f"📈 图表已生成: {out_path}\n"
                       f"   列: {', '.join(numeric_cols)}",
                metadata={"image": out_path}
            )
        except ImportError:
            return TaskResult(task_id="", agent_name=self.name,
                              output="需要 matplotlib: pip install matplotlib", status="error")
        except Exception as e:
            return TaskResult(task_id="", agent_name=self.name,
                              output=f"❌ 图表生成失败: {e}", status="error")