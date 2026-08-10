"""安全 Agent：漏洞扫描、端口扫描、安全分析

能力（调用已装工具）：
1. 端口扫描   → nmap / masscan
2. 漏洞扫描   → nuclei
3. 目录爆破   → ffuf / gobuster
4. 爬虫发现   → katana / gau
5. SQL注入    → sqlmap
6. 弱口令爆破 → hydra
7. XSS检测    → dalfox

⚠️ 仅用于授权测试。主动测试前必须确认目标授权范围。
"""

import re
import subprocess
from typing import Optional
from ..core.base_agent import Agent
from ..models.task import Task, TaskResult


class SecurityAgent(Agent):
    name = "security"
    description = "漏洞扫描、端口扫描、安全分析（nuclei/nmap/sqlmap等）"

    # 工具路径
    TOOLS = {
        "nuclei": "/root/go/bin/nuclei",
        "katana": "/root/go/bin/katana",
        "ffuf": "/root/go/bin/ffuf",
        "dalfox": "/root/go/bin/dalfox",
        "amass": "/root/go/bin/amass",
        "nmap": "nmap",
        "masscan": "masscan",
        "hydra": "hydra",
        "sqlmap": "sqlmap",
    }

    def run(self, task: Task) -> TaskResult:
        content = task.content
        c = content.lower()
        target = self._extract_target(content)

        if not target:
            return TaskResult(
                task_id=task.id, agent_name=self.name,
                output="⚠️ 未识别到目标。请提供域名或 IP。\n\n"
                       "可用命令:\n"
                       f"  • 端口扫描: '扫描 {target} 端口'（nmap）\n"
                       "  • 漏洞扫描: 'nuclei 扫描 example.com'\n"
                       "  • 目录爆破: '爆破 example.com 目录'\n"
                       "  • 子域名:   '子域名枚举 example.com'\n"
                       "  • SQL注入:  'sqlmap 测试 http://x.com?id=1'\n"
                       "  • XSS:      'dalfox 测试 http://x.com'\n",
                status="error"
            )

        if "nuclei" in c or "漏洞" in c:
            return self._run_nuclei(target)
        if "sqlmap" in c or "sql注入" in c or "sql注入" in c:
            return self._run_sqlmap(target)
        if "dalfox" in c or "xss" in c:
            return self._run_dalfox(target)
        if "ffuf" in c or "gobuster" in c or "目录" in c or "爆破" in c:
            return self._run_ffuf(target)
        if "katana" in c or "爬" in c or "端点" in c:
            return self._run_katana(target)
        if "masscan" in c:
            return self._run_masscan(target)
        if "hydra" in c or "爆破密码" in c or "弱口令" in c:
            return self._run_hydra(target)
        if "端口" in c or "端口扫描" in c or "nmap" in c:
            return self._run_nmap(target)

        # 默认：综合扫描（nmap 端口 + nuclei 漏洞）
        return self._run_quick_scan(target)

    # ─── 能力: 端口扫描 ───

    def _run_nmap(self, target: str) -> TaskResult:
        """nmap 端口扫描（快速）"""
        cmd = ["nmap", "-sn", "-T4", target]
        return self._exec(cmd, f"🔍 nmap 主机发现: {target}", timeout=15)

    def _run_masscan(self, target: str) -> TaskResult:
        """masscan 快速端口扫描"""
        cmd = ["masscan", target, "-p1-10000", "--rate", "1000"]
        return self._exec(cmd, f"🔍 masscan 快速扫描: {target}")

    # ─── 能力: 漏洞扫描 ───

    def _run_nuclei(self, target: str) -> TaskResult:
        """nuclei 漏洞扫描"""
        cmd = [self.TOOLS["nuclei"], "-u", target, "-silent", "-no-color",
               "-severity", "low,medium,high,critical"]
        return self._exec(cmd, f"🛡️ nuclei 漏洞扫描: {target}")

    def _run_quick_scan(self, target: str) -> TaskResult:
        """快速综合扫描"""
        out = []
        # 先用 nmap 快速端口
        nm = self._run_nmap(target)
        out.append(nm.output)
        # 再用 nuclei 漏洞
        nu = self._run_nuclei(target)
        out.append(nu.output)
        return TaskResult(
            task_id="", agent_name=self.name,
            output="\n\n".join(out),
            status="success" if nm.is_success() or nu.is_success() else "partial"
        )

    # ─── 能力: 目录爆破 ───

    def _run_ffuf(self, target: str) -> TaskResult:
        """ffuf 目录爆破"""
        cmd = [self.TOOLS["ffuf"], "-u", f"{target}/FUZZ",
               "-w", "/root/super-agent/data/dict/common.txt",
               "-mc", "200,301,302,403", "-t", "50", "-s"]
        return self._exec(cmd, f"📁 ffuf 目录爆破: {target}")

    # ─── 能力: 爬虫发现 ───

    def _run_katana(self, target: str) -> TaskResult:
        """katana 爬虫发现端点"""
        cmd = [self.TOOLS["katana"], "-u", target, "-silent", "-d", "2"]
        return self._exec(cmd, f"🕷️ katana 端点发现: {target}")

    # ─── 能力: SQL注入 ───

    def _run_sqlmap(self, target: str) -> TaskResult:
        """sqlmap SQL注入检测"""
        cmd = ["sqlmap", "-u", target, "--batch", "--level", "1", "--risk", "1"]
        return self._exec(cmd, f"💉 sqlmap SQL注入检测: {target}")

    # ─── 能力: XSS ───

    def _run_dalfox(self, target: str) -> TaskResult:
        """dalfox XSS检测"""
        cmd = [self.TOOLS["dalfox"], "url", target, "--silence", "--no-spinner"]
        return self._exec(cmd, f"🔥 dalfox XSS检测: {target}")

    # ─── 能力: 弱口令 ───

    def _run_hydra(self, target: str) -> TaskResult:
        """hydra 弱口令爆破（仅授权）"""
        # 提取协议
        proto = "ssh"
        if "rdp" in target.lower():
            proto = "rdp"
        elif "ftp" in target.lower():
            proto = "ftp"
        host = re.sub(r'^[\w]+://', '', target)
        cmd = ["hydra", "-l", "admin", "-P", "/root/super-agent/data/dict/passwords.txt",
               host, proto, "-t", "4", "-f"]
        return self._exec(cmd, f"🔑 hydra {proto} 弱口令测试: {host}")

    # ─── 工具方法 ───

    def _extract_target(self, content: str) -> Optional[str]:
        """从文本提取目标（域名/IP/URL）"""
        url = re.search(r'https?://[\w\-\./]+', content)
        if url:
            return url.group(0)
        domain = re.search(r'(?:[\w\-]+\.)+[a-zA-Z]{2,}', content)
        ip = re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', content)
        if domain:
            return domain.group(0)
        if ip:
            return ip.group(0)
        return None

    def _exec(self, cmd: list, label: str, timeout: int = 60) -> TaskResult:
        """执行命令并返回结果"""
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            output = result.stdout[:3000]
            if result.stderr and result.returncode != 0:
                output += f"\n[stderr]\n{result.stderr[:500]}"
            if not output.strip():
                output = "(无输出)"
            return TaskResult(
                task_id="", agent_name=self.name,
                output=f"{label}\n\n{output}",
                status="success" if result.returncode == 0 else "partial",
                error=None if result.returncode == 0 else result.stderr[:300]
            )
        except subprocess.TimeoutExpired:
            return TaskResult(
                task_id="", agent_name=self.name,
                output=f"⏱️ {label}\n执行超时（{timeout}s）", status="error"
            )
        except FileNotFoundError as e:
            return TaskResult(
                task_id="", agent_name=self.name,
                output=f"❌ 工具未安装: {e}", status="error"
            )
        except Exception as e:
            return TaskResult(
                task_id="", agent_name=self.name,
                output=f"❌ 执行异常: {e}", status="error"
            )