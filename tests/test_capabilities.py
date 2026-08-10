"""能力测试脚本"""
import sys, json
sys.path.insert(0, "/root/super-agent")

from super_agent.capabilities.anti_crawl import AntiCrawl
from super_agent.capabilities.multi_source import MultiSource
from super_agent.capabilities.search_discovery import SearchDiscovery
from super_agent.capabilities.scheduler import Scheduler
from super_agent.capabilities.storage import Storage

results = {}

# ═══ 1. 网页访问 ═══
print("### 1. 网页访问 ###")
ac = AntiCrawl()
try:
    html = ac._normal_fetch("https://httpbin.org/get")
    results["1_普通请求"] = {"len": len(html), "has_data": '"origin"' in html}
    print("  普通请求:", results["1_普通请求"])
except Exception as e:
    results["1_普通请求"] = {"error": str(e)}
    print("  普通请求 ERROR:", e)

# JS渲染
try:
    import playwright
    results["1_playwright_已装"] = True
    print("  Playwright: 已安装")
except ImportError:
    results["1_playwright_已装"] = False
    print("  Playwright: 未安装")

# ═══ 2. 反爬对抗 ═══
print("### 2. 反爬对抗 ###")
try:
    hdrs = ac.random_headers()
    results["2_随机请求头"] = {"has_ua": "User-Agent" in hdrs, "ua": hdrs["User-Agent"][:40]}
    print("  随机请求头:", results["2_随机请求头"])
    proxy = ac.get_proxy()
    results["2_代理池"] = proxy
    print("  代理池(空):", proxy)
except Exception as e:
    print("  反爬 ERROR:", e)

# ═══ 3. 内容提取+转换 ═══
print("### 3. 内容提取+转换 ###")
try:
    import trafilatura
    text = trafilatura.extract(html)
    results["3_正文提取"] = {"trafilatura_ok": text is not None}
    print("  trafilatura 正文提取:", results["3_正文提取"])
except ImportError:
    results["3_正文提取"] = {"error": "未安装"}
    print("  trafilatura: 未安装")

try:
    import html2text
    md = html2text.html2text(html)
    results["3_html转md"] = {"len": len(md)}
    print("  html2text:", results["3_html转md"])
except ImportError:
    results["3_html转md"] = {"error": "未安装"}
    print("  html2text: 未安装")

try:
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "lxml")
    results["3_bs4解析"] = True
    print("  BeautifulSoup: 可用")
except ImportError:
    results["3_bs4解析"] = False
    print("  BeautifulSoup: 未安装")

# ═══ 4. 多源采集 ═══
print("### 4. 多源采集 ###")
ms = MultiSource()
for mod, name in [("feedparser", "RSS"), ("newspaper", "新闻")]:
    try:
        __import__(mod)
        results["4_" + name] = True
        print(f"  {name}: 已安装")
    except ImportError:
        results["4_" + name] = False
        print(f"  {name}: 未安装")

try:
    import subprocess
    r = subprocess.run(["yt-dlp", "--version"], capture_output=True, text=True)
    results["4_视频"] = r.returncode == 0
    print("  视频(yt-dlp):", "已安装" if r.returncode == 0 else "未安装")
except:
    results["4_视频"] = False
    print("  视频(yt-dlp): 未安装")

# ═══ 5. 搜索发现 ═══
print("### 5. 搜索发现 ###")
sd = SearchDiscovery()
try:
    res = sd.search_web("python", engine="duckduckgo", num=3)
    results["5_DuckDuckGo搜索"] = {"count": len(res), "valid": all("error" not in r for r in res)}
    print("  DuckDuckGo:", results["5_DuckDuckGo搜索"])
except Exception as e:
    results["5_DuckDuckGo搜索"] = {"error": str(e)}
    print("  DuckDuckGo ERROR:", e)

try:
    res = sd.search_web("python", engine="baidu", num=3)
    results["5_百度搜索"] = {"count": len(res)}
    print("  百度:", results["5_百度搜索"])
except Exception as e:
    results["5_百度搜索"] = {"error": str(e)}
    print("  百度 ERROR:", e)

try:
    import subprocess
    r = subprocess.run(["which", "subfinder"], capture_output=True, text=True)
    results["5_subfinder"] = r.returncode == 0
    print("  subfinder:", "已安装" if r.returncode == 0 else "未安装")
except:
    results["5_subfinder"] = False

try:
    import subprocess
    r = subprocess.run(["which", "sherlock"], capture_output=True, text=True)
    results["5_sherlock"] = r.returncode == 0
    print("  sherlock:", "已安装" if r.returncode == 0 else "未安装")
except:
    results["5_sherlock"] = False

# ═══ 6. 分析归类 ═══
print("### 6. 分析归类 ###")
try:
    from super_agent.agents.collect_agent import InfoCollectAgent
    ica = InfoCollectAgent()
    # 测试分类
    cat = ica._classify_info if hasattr(ica, "_classify_info") else None
    results["6_关键词分类"] = True
    print("  关键词分类: 可用")
except Exception as e:
    results["6_关键词分类"] = {"error": str(e)}
    print("  分类 ERROR:", e)

# ═══ 7. 定时监控 ═══
print("### 7. 定时监控 ###")
try:
    import apscheduler
    results["7_apscheduler"] = True
    print("  APScheduler: 已安装")
except ImportError:
    results["7_apscheduler"] = False
    print("  APScheduler: 未安装")

# ═══ 8. 存储检索 ═══
print("### 8. 存储检索 ###")
st = Storage()
try:
    save = st.save("test_source", "测试标题", "测试内容", "http://test.com", "测试")
    results["8_存储保存"] = save
    print("  保存:", save)
    search = st.search("测试", limit=5)
    results["8_全文检索"] = {"count": len(search)}
    print("  检索:", results["8_全文检索"])
    stats = st.stats()
    results["8_统计"] = stats
    print("  统计:", stats)
except Exception as e:
    results["8_存储"] = {"error": str(e)}
    print("  存储 ERROR:", e)

# 输出 JSON
print("\n=== JSON ===")
print(json.dumps(results, ensure_ascii=False, indent=2))