"""能力：存储检索

解决：数据持久化 + 快速检索
方案：
- SQLite 结构化存储
- FTS5 全文搜索
- JSON 文件备份
- 向量检索（可选 chromadb）
"""

import json
import sqlite3
import os
from datetime import datetime
from typing import Optional, Any


class Storage:
    """存储检索能力层"""

    def __init__(self, db_path: str = "~/.super_agent/data.db"):
        self.db_path = os.path.expanduser(db_path)
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS collected_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT,
                title TEXT,
                content TEXT,
                url TEXT,
                category TEXT,
                collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # 全文搜索索引
        try:
            conn.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS content_fts
                USING fts5(title, content, source, content=collected_data, content_rowid=id)
            """)
        except Exception as _e:
            self._fts_available = False
        conn.commit()
        conn.close()

    # ─── 写入 ───

    def save(self, source: str, title: str, content: str,
             url: str = "", category: str = "general") -> dict:
        """保存一条采集数据"""
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.execute(
                "INSERT INTO collected_data (source, title, content, url, category) VALUES (?, ?, ?, ?, ?)",
                (source, title, content[:50000], url, category)
            )
            conn.commit()
            row_id = cur.lastrowid
            # 同步 FTS
            try:
                conn.execute(
                    "INSERT INTO content_fts (rowid, title, content, source) VALUES (?, ?, ?, ?)",
                    (row_id, title, content[:50000], source)
                )
                conn.commit()
            except Exception as _e:
                self._fts_sync_ok = False
            conn.close()
            return {"id": row_id, "status": "saved"}
        except Exception as e:
            return {"error": f"存储失败: {e}"}

    # ─── 检索 ───

    def search(self, query: str, limit: int = 20) -> list:
        """全文搜索"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            # 先试 FTS5
            try:
                cur = conn.execute(
                    """SELECT c.* FROM content_fts f
                       JOIN collected_data c ON c.id = f.rowid
                       WHERE content_fts MATCH ?
                       ORDER BY rank LIMIT ?""",
                    (query, limit)
                )
            except:
                # 回退 LIKE 搜索
                cur = conn.execute(
                    """SELECT * FROM collected_data
                       WHERE content LIKE ? OR title LIKE ?
                       ORDER BY collected_at DESC LIMIT ?""",
                    (f"%{query}%", f"%{query}%", limit)
                )
            results = [dict(r) for r in cur.fetchall()]
            conn.close()
            return results
        except Exception as e:
            return [{"error": f"检索失败: {e}"}]

    # ─── 导出 ───

    def export_json(self, filepath: str, category: Optional[str] = None) -> dict:
        """导出为 JSON 文件"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            if category:
                cur = conn.execute("SELECT * FROM collected_data WHERE category = ?", (category,))
            else:
                cur = conn.execute("SELECT * FROM collected_data")
            data = [dict(r) for r in cur.fetchall()]
            conn.close()
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return {"status": "exported", "count": len(data), "path": filepath}
        except Exception as e:
            return {"error": f"导出失败: {e}"}

    # ─── 统计 ───

    def stats(self) -> dict:
        """数据统计"""
        try:
            conn = sqlite3.connect(self.db_path)
            total = conn.execute("SELECT COUNT(*) FROM collected_data").fetchone()[0]
            by_source = conn.execute(
                "SELECT source, COUNT(*) as cnt FROM collected_data GROUP BY source ORDER BY cnt DESC"
            ).fetchall()
            by_category = conn.execute(
                "SELECT category, COUNT(*) as cnt FROM collected_data GROUP BY category ORDER BY cnt DESC"
            ).fetchall()
            conn.close()
            return {
                "total": total,
                "by_source": dict(by_source),
                "by_category": dict(by_category),
            }
        except Exception as e:
            return {"error": f"统计失败: {e}"}