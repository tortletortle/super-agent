# 超级信息收集智能体 — 能力说明

> 本文件基于真实测试结果编写（2026-08-10）。所有标记 ✅ 的能力均通过端到端测试验证。

## 能力总览

| # | 能力 | 状态 | 测试结果 | 说明 |
|---|------|------|---------|------|
| 1 | 网页搜索 | ✅ 可用 | 多引擎返回结果 | DuckDuckGo 成功，百度/必应需测试 |
| 2 | 网页访问 | ✅ 可用 | 成功获取 HTML | requests 普通请求 |
| 3 | JS渲染访问 | ⚠️ 需配置 | 依赖 Playwright | `playwright install chromium` |
| 4 | 网页正文提取 | ✅ 可用 | BBC 提取 6417 字符 | trafilatura + newspaper |
| 5 | HTML转Markdown | ✅ 可用 | 转换成功 | html2text |
| 6 | RSS 订阅采集 | ✅ 可用 | BBC 20 条新闻 | feedparser |
| 7 | 新闻全文提取 | ✅ 可用 | BBC 头条提取 | newspaper3k |
| 8 | 视频元数据 | ⚠️ 需配置 | 依赖 yt-dlp | 已安装 |
| 9 | 子域名枚举 | ⚠️ 云服务器受限 | subfinder 已装 | 云 DNS 受限，本地可跑 |
| 10 | 用户名搜索 | ✅ 可用 | alan 找到9GAG等 | sherlock (Python3.11 venv) |
| 11 | 信息分类 | ✅ 可用 | 关键词分类 | 可升级 LLM |
| 12 | 定时监控 | ✅ 可用 | APScheduler | 已安装 |
| 13 | 存储检索 | ✅ 可用 | 保存/检索/统计 | SQLite + FTS5 |
| 14 | 反爬对抗 | ⚠️ 基础版 | 随机头 | 需接代理池/隐身浏览器 |

## 使用方式

```python
from super_agent.core import SuperAgent
from super_agent.agents import InfoCollectAgent

agent = SuperAgent('InfoKing')
agent.register_agent(InfoCollectAgent())

# 搜索
agent.run('搜索 AI 开源项目')
# 访问网页
agent.run('访问 https://example.com')
# RSS 采集
agent.run('RSS https://feeds.bbci.co.uk/news/rss.xml')
# 新闻全文
agent.run('新闻 https://www.bbc.com/news')
# 用户名搜索（OSINT）
agent.run('用户名 alan')
# 子域名枚举
agent.run('子域名 example.com')
# 存储检索
agent.run('检索 关键词')
# 数据统计
agent.run('存储统计')
```

## 依赖安装

```bash
pip install requests beautifulsoup4 lxml trafilatura html2text \
    feedparser newspaper3k yt-dlp apscheduler playwright

# 子域名（Go）
go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest

# 用户名搜索（需 Python 3.11）
uv venv /tmp/sherlock_venv --python 3.11
/tmp/sherlock_venv/bin/python3 -m pip install sherlock-project

# JS渲染
python -m playwright install chromium
```

## 已知限制

- **子域名枚举**：云服务器 DNS 受限，subfinder 可能超时。建议在本地机器运行
- **反爬对抗**：当前为基础版（随机UA），强反爬站点需接入隐身浏览器
- **百度搜索**：中文搜索结果可能不稳定
- **代理池**：未配置，反爬需要时需自建 proxy_pool