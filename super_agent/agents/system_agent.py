"""系统 Agent：运维、部署、进程、Docker

能力：
1. 查看系统状态（CPU/内存/磁盘）
2. 进程管理（ps/top/kill）
3. Docker 操作（ps/镜像/容器）
4. 服务管理（systemctl）
5. 磁盘/网络状态
"""

import os
import subprocess
from typing import Optional
from ..core.base_agent import Agent
from ..models.task import Task, TaskResult


class SystemAgent(Agent):
    name = "system"
    description = "系统运维：状态监控、进程管理、Docker、服务管理"

    def run(self, task: Task) -> TaskResult:
        content = task.content
        c = content.lower()

        if "docker" in c:
            return self._docker(content)
        if "systemctl" in c or "服务" in c or "启动" in c or "停止" in c:
            return self._service(content)
        if "进程" in c or "ps" in c or "kill" in c:
            return self._process(content)
        if "磁盘" in c or "内存" in c or "cpu" in c or "状态" in c or "资源" in c:
            return self._sysinfo(content)
        if "网络" in c and ("连接" in c or "端口" in c or "netstat" in c):
            return self._network(content)
        if "占用" in c or "大文件" in c:
            return self._disk_usage()

        return TaskResult(
            task_id=task.id, agent_name=self.name,
            output="SystemAgent 可用能力:\n"
                   "  • 系统状态: '查看系统状态'（CPU/内存/磁盘）\n"
                   "  • 进程: '查看进程' / '杀掉 PID 1234'\n"
                   "  • Docker: 'docker ps' / '查看容器'\n"
                   "  • 服务: '查看 nginx 服务状态'\n"
                   "  • 磁盘: '查看磁盘占用'"
        )

    def _sysinfo(self, content: str) -> TaskResult:
        return self._exec(["bash", "-c", "echo '=== CPU ==='; uptime; echo; echo '=== 内存 ==='; free -h; echo; echo '=== 磁盘 ==='; df -h | head -10"], "🖥️ 系统状态")

    def _process(self, content: str) -> TaskResult:
        import re
        m = re.findall(r'\b\d{3,6}\b', content)
        if m and ("kill" in content.lower() or "杀" in content):
            for pid in m:
                return self._exec(["kill", pid], f"🔪 杀掉进程 {pid}")
        return self._exec(["ps", "aux", "--sort=-%mem", "|", "head", "-15"], "📊 进程列表（按内存排序）")

    def _docker(self, content: str) -> TaskResult:
        c = content.lower()
        if "ps" in c or "容器" in c or "查看" in c:
            return self._exec(["docker", "ps", "-a"], "🐳 Docker 容器")
        if "images" in c or "镜像" in c:
            return self._exec(["docker", "images"], "🐳 Docker 镜像")
        if "stats" in c:
            return self._exec(["docker", "stats", "--no-stream"], "🐳 容器资源占用")
        if "logs" in c or "日志" in c:
            import re
            name = re.search(r'(?:日志|logs)\s+(\S+)', content)
            if name:
                return self._exec(["docker", "logs", "--tail", "50", name.group(1)], f"🐳 容器日志: {name.group(1)}")
        return self._exec(["docker", "ps", "-a"], "🐳 Docker 容器")

    def _service(self, content: str) -> TaskResult:
        import re
        svc = re.search(r'(?:服务|systemctl)\s+(\S+)', content)
        cmd_word = "nginx" if "nginx" in content.lower() else (svc.group(1) if svc else "")
        if not cmd_word:
            return self._exec(["systemctl", "list-units", "--type=service", "--state=running"], "📋 运行中的服务")
        if "状态" in content or "status" in content.lower():
            return self._exec(["systemctl", "status", cmd_word, "--no-pager"], f"📋 服务状态: {cmd_word}")
        if "启动" in content or "start" in content.lower():
            return self._exec(["systemctl", "start", cmd_word], f"▶️ 启动服务: {cmd_word}")
        if "停止" in content or "stop" in content.lower():
            return self._exec(["systemctl", "stop", cmd_word], f"⏹️ 停止服务: {cmd_word}")
        return self._exec(["systemctl", "status", cmd_word, "--no-pager"], f"📋 服务状态: {cmd_word}")

    def _network(self, content: str) -> TaskResult:
        return self._exec(["netstat", "-tulpn"], "🌐 网络监听端口")

    def _disk_usage(self) -> TaskResult:
        return self._exec(["bash", "-c", "du -ah --max-depth=1 / 2>/dev/null | sort -rh | head -15"], "💾 磁盘占用 TOP15")

    def _exec(self, cmd: list, label: str, timeout: int = 30) -> TaskResult:
        # 支持管道命令
        if "|" in cmd:
            shell = " ".join(cmd)
            p = subprocess.Popen(shell, shell=True, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE, text=True)
        else:
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE, text=True)
        try:
            out, err = p.communicate(timeout=timeout)
            output = out[:3000]
            if err and p.returncode != 0:
                output += f"\n[stderr]\n{err[:500]}"
            return TaskResult(
                task_id="", agent_name=self.name,
                output=f"{label}\n\n```\n{output}\n```",
                status="success" if p.returncode == 0 else "partial",
                error=err[:300] if p.returncode != 0 else None
            )
        except subprocess.TimeoutExpired:
            p.kill()
            return TaskResult(task_id="", agent_name=self.name,
                              output=f"⏱️ {label}\n超时", status="error")