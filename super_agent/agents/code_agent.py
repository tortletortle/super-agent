"""编码 Agent：代码生成、分析、执行

能力：
1. 写代码文件（.py/.js/.sh 等）
2. 执行代码并返回结果
3. 代码分析（统计/搜索/结构）
4. 代码搜索（grep）
"""

import os
import subprocess
import tempfile
from typing import Optional
from ..core.base_agent import Agent
from ..models.task import Task, TaskResult


class CodeAgent(Agent):
    name = "code"
    description = "代码生成、执行、分析、Bug 修复"

    def run(self, task: Task) -> TaskResult:
        content = task.content
        c = content.lower()

        if "执行" in c or "运行" in c or "run" in c or self._extract_code(content):
            return self._handle_execute(content)
        if "搜索" in c or "查找" in c or "grep" in c:
            return self._handle_search(content)
        if "统计" in c or "分析代码" in c or "结构" in c:
            return self._handle_analyze(content)
        if "写" in c or "创建" in c or "生成" in c or "新建" in c:
            return self._handle_write(content)

        # 默认：如果是代码就执行，否则生成
        code = self._extract_code(content)
        if code:
            return self._handle_execute(content)
        return TaskResult(
            task_id=task.id, agent_name=self.name,
            output="CodeAgent 可用能力:\n"
                   "  • 写代码: '写一个 Python 脚本 xxx'\n"
                   "  • 执行代码: '执行 python 代码...' 或贴代码块\n"
                   "  • 代码搜索: '搜索 main.py 里的 TODO'\n"
                   "  • 代码分析: '分析 ./project 代码结构'"
        )

    # ─── 能力1: 写代码文件 ───

    def _handle_write(self, content: str) -> TaskResult:
        """从任务中提取代码并写入文件"""
        code = self._extract_code(content)
        if not code:
            return TaskResult(
                task_id="", agent_name=self.name,
                output="⚠️ 未检测到代码块。请用 ```lang ...``` 包裹代码，并指定文件名。",
                status="error"
            )
        # 提取文件名
        import re
        fname = re.search(r'[\w\-/]+\.\w+', content)
        path = fname.group(0) if fname else "generated.py"
        if not os.path.isabs(path):
            path = os.path.join(os.getcwd(), path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(code)
        return TaskResult(
            task_id="", agent_name=self.name,
            output=f"✅ 已写入 {path}\n\n```python\n{code[:500]}\n```",
            metadata={"path": path, "lang": self._detect_lang(content)}
        )

    # ─── 能力2: 执行代码 ───

    def _handle_execute(self, content: str) -> TaskResult:
        """识别并执行代码"""
        code = self._extract_code(content)
        lang = "python" if not self._detect_lang(content) else self._detect_lang(content)

        if not code:
            # 可能是执行已有文件
            import re
            fname = re.search(r'[\w\-/]+\.\w+', content)
            if fname and os.path.exists(fname.group(0)):
                return self._run_file(fname.group(0), content)
            return TaskResult(
                task_id="", agent_name=self.name,
                output="⚠️ 没有可执行的代码或文件。", status="error"
            )

        return self._run_code(code, lang)

    def _run_code(self, code: str, lang: str) -> TaskResult:
        """运行代码片段"""
        try:
            if lang in ("python", "py"):
                result = subprocess.run(
                    ["python3", "-c", code],
                    capture_output=True, text=True, timeout=30
                )
            elif lang in ("js", "javascript", "node"):
                result = subprocess.run(
                    ["node", "-e", code],
                    capture_output=True, text=True, timeout=30
                )
            elif lang in ("bash", "sh", "shell"):
                result = subprocess.run(
                    ["bash", "-c", code],
                    capture_output=True, text=True, timeout=30
                )
            else:
                return TaskResult(
                    task_id="", agent_name=self.name,
                    output=f"⚠️ 暂不支持直接执行 {lang}，请用 python/js/bash", status="error"
                )

            output = result.stdout
            if result.stderr:
                output += f"\n\n[stderr]\n{result.stderr[:1000]}"
            if result.returncode != 0:
                return TaskResult(
                    task_id="", agent_name=self.name,
                    output=f"❌ 执行失败 (exit {result.returncode})\n{output[:2000]}",
                    status="error", error=result.stderr[:500]
                )
            return TaskResult(
                task_id="", agent_name=self.name,
                output=f"✅ 执行成功\n\n```\n{output[:3000]}\n```",
                metadata={"lang": lang}
            )
        except subprocess.TimeoutExpired:
            return TaskResult(
                task_id="", agent_name=self.name,
                output="❌ 执行超时（30s）", status="error"
            )
        except Exception as e:
            return TaskResult(
                task_id="", agent_name=self.name,
                output=f"❌ 执行异常: {e}", status="error"
            )

    def _run_file(self, path: str, content: str) -> TaskResult:
        """运行已有代码文件"""
        ext = path.rsplit(".", 1)[-1] if "." in path else ""
        cmd = None
        if ext in ("py",):
            cmd = ["python3", path]
        elif ext in ("js",):
            cmd = ["node", path]
        elif ext in ("sh",):
            cmd = ["bash", path]
        else:
            return TaskResult(
                task_id="", agent_name=self.name,
                output=f"⚠️ 不支持的扩展名: .{ext}", status="error"
            )
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            output = result.stdout
            if result.stderr:
                output += f"\n[stderr]\n{result.stderr[:1000]}" if result.returncode != 0 else ""
            return TaskResult(
                task_id="", agent_name=self.name,
                output=f"✅ 运行 {path}\n```\n{output[:3000]}\n```",
                status="error" if result.returncode != 0 else "success",
                metadata={"path": path}
            )
        except Exception as e:
            return TaskResult(
                task_id="", agent_name=self.name,
                output=f"❌ 运行失败: {e}", status="error"
            )

    # ─── 能力3: 代码搜索 ───

    def _handle_search(self, content: str) -> TaskResult:
        """grep 搜索代码"""
        import re
        # 提取搜索词
        search_terms = re.findall(r'["\']([^"\']+)["\']', content)
        query = search_terms[0] if search_terms else content.replace("搜索", "").strip()
        # 提取路径
        path = os.getcwd()
        try:
            result = subprocess.run(
                ["grep", "-rn", "--include=*.py", "--include=*.js", "--include=*.ts",
                 "--include=*.html", "--include=*.sh", query, path],
                capture_output=True, text=True, timeout=15
            )
            lines = result.stdout.split("\n")
            # 限制输出
            shown = [l for l in lines if l.strip()][:30]
            return TaskResult(
                task_id="", agent_name=self.name,
                output=f"🔍 搜索 '{query}' 找到 {len([l for l in lines if l])} 处:\n\n" + "\n".join(shown)
            )
        except Exception as e:
            return TaskResult(
                task_id="", agent_name=self.name,
                output=f"❌ 搜索失败: {e}", status="error"
            )

    # ─── 能力4: 代码分析 ───

    def _handle_analyze(self, content: str) -> TaskResult:
        """分析代码目录结构"""
        import re
        fname = re.search(r'[\w\-/\.]+', content)
        path = fname.group(0) if fname and os.path.exists(fname.group(0)) else os.getcwd()
        if os.path.isfile(path):
            path = os.path.dirname(path)
        try:
            result = subprocess.run(
                ["find", path, "-type", "f", "-name", "*.py", "-o", "-name", "*.js"],
                capture_output=True, text=True, timeout=15
            )
            files = [f for f in result.stdout.split("\n") if f]
            total_lines = 0
            by_ext = {}
            for f in files:
                ext = f.rsplit(".", 1)[-1] if "." in f else "?"
                by_ext[ext] = by_ext.get(ext, 0) + 1
                try:
                    total_lines += sum(1 for _ in open(f, errors="ignore"))
                except:
                    pass
            return TaskResult(
                task_id="", agent_name=self.name,
                output=f"📊 代码分析: {path}\n"
                       f"  文件数: {len(files)}\n"
                       f"  总行数: {total_lines}\n"
                       f"  语言分布: {by_ext}"
            )
        except Exception as e:
            return TaskResult(
                task_id="", agent_name=self.name,
                output=f"❌ 分析失败: {e}", status="error"
            )

    # ─── 工具方法 ───

    def _extract_code(self, content: str) -> Optional[str]:
        """从文本中提取代码块"""
        import re
        m = re.search(r'```(?:\w+)?\n(.*?)```', content, re.DOTALL)
        if m:
            return m.group(1).strip()
        return None

    def _detect_lang(self, content: str) -> str:
        """检测代码语言"""
        import re
        m = re.search(r'```(\w+)', content)
        if m:
            return m.group(1).lower()
        return "python"