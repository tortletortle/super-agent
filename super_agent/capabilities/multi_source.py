"""能力：多源采集

解决：从不同来源（RSS/社媒/视频/API）采集数据
方案：
- RSS 订阅：feedparser 解析
- 中文社媒：对接 MediaCrawler(60k) 模式
- 视频信息：yt-dlp(183k) 提取
- 新闻：newspaper(15k) 全文提取
- 通用 API：REST 接口对接
"""

import json
from typing import Optional


class MultiSource:
    """多源采集能力层"""

    # ─── RSS 采集 ───

    def fetch_rss(self, feed_url: str, max_items: int = 20) -> list:
        """采集 RSS 订阅源"""
        try:
            import feedparser
            feed = feedparser.parse(feed_url)
            entries = []
            for entry in feed.entries[:max_items]:
                entries.append({
                    "title": entry.get("title", ""),
                    "link": entry.get("link", ""),
                    "summary": entry.get("summary", "")[:500],
                    "published": entry.get("published", ""),
                })
            return entries
        except ImportError:
            return [{"error": "需要安装 feedparser: pip install feedparser"}]
        except Exception as e:
            return [{"error": f"RSS 采集失败: {e}"}]

    # ─── 新闻全文提取 ───

    def extract_news(self, url: str) -> dict:
        """提取新闻文章全文"""
        try:
            from newspaper import Article
            article = Article(url)
            article.download()
            article.parse()
            return {
                "title": article.title or "",
                "authors": article.authors,
                "publish_date": str(article.publish_date) if article.publish_date else "",
                "text": article.text[:5000],
                "keywords": article.keywords[:10] if article.keywords else [],
            }
        except ImportError:
            return {"error": "需要安装 newspaper3k: pip install newspaper3k"}
        except Exception as e:
            return {"error": f"新闻提取失败: {e}"}

    # ─── 视频信息采集 ───

    def fetch_video_info(self, url: str) -> dict:
        """提取视频元数据（标题/描述/时长等）"""
        try:
            import subprocess
            import json as j
            result = subprocess.run(
                ["yt-dlp", "--dump-json", "--no-download", url],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                data = j.loads(result.stdout)
                return {
                    "title": data.get("title", ""),
                    "description": (data.get("description", "") or "")[:500],
                    "duration": data.get("duration", 0),
                    "uploader": data.get("uploader", ""),
                    "view_count": data.get("view_count", 0),
                    "like_count": data.get("like_count", 0),
                }
            return {"error": f"yt-dlp 错误: {result.stderr[:200]}"}
        except FileNotFoundError:
            return {"error": "需要安装 yt-dlp: pip install yt-dlp"}
        except Exception as e:
            return {"error": f"视频信息提取失败: {e}"}

    # ─── 通用 API 采集 ───

    def call_api(self, url: str, method: str = "GET",
                 params: Optional[dict] = None,
                 headers: Optional[dict] = None,
                 json_body: Optional[dict] = None) -> dict:
        """调用第三方 REST API"""
        try:
            import requests
            resp = requests.request(
                method, url,
                params=params, json=json_body,
                headers=headers or {},
                timeout=20
            )
            return {
                "status_code": resp.status_code,
                "headers": dict(resp.headers),
                "body": resp.text[:5000],
            }
        except ImportError:
            return {"error": "需要安装 requests"}
        except Exception as e:
            return {"error": f"API 调用失败: {e}"}

    # ─── 社媒通用采集（标记位，对接 MediaCrawler） ───

    def social_media_config(self, platform: str = "all") -> dict:
        """
        返回社媒采集配置模板。
        实际采集需对接 MediaCrawler(60k)，支持：
        小红书 / 抖音 / 快手 / B站 / 微博 / 贴吧 / 知乎
        """
        platforms = {
            "xiaohongshu": "小红书",
            "douyin": "抖音",
            "kuaishou": "快手",
            "bilibili": "B站",
            "weibo": "微博",
            "tieba": "贴吧",
            "zhihu": "知乎",
        }
        return {
            "note": "需对接 MediaCrawler 项目 (github.com/NanmiCoder/MediaCrawler)",
            "platforms": platforms,
            "config_template": {
                "cookies": "需要各平台登录 Cookie",
                "keywords": ["搜索关键词"],
                "max_count": 100,
            }
        }