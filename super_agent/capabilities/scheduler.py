"""能力：定时监控

解决：定时采集、变更检测、结果通知
方案：
- APScheduler 定时触发
- 内容变更检测（diff 对比）
- 结果通知（Telegram / 邮件）
"""

import json
import hashlib
from datetime import datetime
from typing import Optional, Callable


class Scheduler:
    """定时监控能力层"""

    def __init__(self):
        self._jobs = {}

    # ─── 定时任务 ───

    def schedule(self, name: str, interval_minutes: int,
                 callback: Callable, *args, **kwargs):
        """注册定时任务"""
        try:
            from apscheduler.schedulers.background import BackgroundScheduler
            sched = BackgroundScheduler()
            sched.add_job(
                callback, "interval",
                minutes=interval_minutes,
                id=name,
                args=args, kwargs=kwargs,
                replace_existing=True,
            )
            sched.start()
            self._jobs[name] = sched
            return {"status": "ok", "job": name, "interval": f"{interval_minutes}min"}
        except ImportError:
            return {"error": "需要安装 apscheduler: pip install apscheduler"}
        except Exception as e:
            return {"error": f"定时任务失败: {e}"}

    def stop(self, name: str):
        """停止定时任务"""
        if name in self._jobs:
            self._jobs[name].shutdown()
            del self._jobs[name]
            return {"status": "stopped", "job": name}
        return {"error": f"任务 {name} 不存在"}

    def list_jobs(self) -> list:
        """列出所有定时任务"""
        return list(self._jobs.keys())

    # ─── 变更检测 ───

    def check_change(self, new_content: str, old_hash: Optional[str] = None) -> dict:
        """检测内容是否变化"""
        new_hash = hashlib.md5(new_content.encode()).hexdigest()
        if old_hash and old_hash == new_hash:
            return {"changed": False, "hash": new_hash}
        return {"changed": True, "hash": new_hash}

    # ─── 通知 ───

    def notify(self, message: str, channel: str = "console") -> dict:
        """发送通知"""
        if channel == "console":
            print(f"[{datetime.now()}] {message}")
            return {"status": "ok", "channel": "console"}
        elif channel == "telegram":
            return {"note": "需对接 Telegram Bot API"}
        elif channel == "email":
            return {"note": "需配置 SMTP"}
        return {"error": f"不支持的通道: {channel}"}