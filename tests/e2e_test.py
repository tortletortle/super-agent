"""端到端真实能力测试"""
import sys, json, time
sys.path.insert(0, "/root/super-agent")

from super_agent.core import SuperAgent
from super_agent.agents import InfoCollectAgent

agent = SuperAgent('InfoKing')
agent.register_agent(InfoCollectAgent())

report = {}

def run_test(name, task):
    print(f"\n{'='*55}")
    print(f"📋 {name}")
    print(f"   指令: {task}")
    t0 = time.time()
    try:
        result = agent.run(task)
        dt = time.time() - t0
        out = result.output
        # 提取关键部分
        # 去掉编排器包装，取 collect agent 的实际输出
        body = out.split("\n\n", 1)[1] if "\n\n" in out else out
        print(f"   ✅ 状态: {result.status} | 耗时: {dt:.1f}s")
        print(f"   输出片段: {body[:250]}")
        report[name] = {"status": result.status, "time": round(dt,1), "preview": body[:200]}
    except Exception as e:
        print(f"   ❌ 异常: {e}")
        report[name] = {"status": "exception", "error": str(e)}

# 1. 搜索
run_test("搜索-多引擎", "搜索 Python 爬虫框架")
# 2. 网页访问
run_test("网页访问", "访问 https://httpbin.org/html")
# 3. 网页正文提取
run_test("网页正文提取", "访问 https://www.bbc.com/news")
# 4. RSS
run_test("RSS采集", "RSS https://feeds.bbci.co.uk/news/rss.xml")
# 5. 新闻提取
run_test("新闻全文", "新闻 https://www.bbc.com/news/world")
# 6. 子域名
run_test("子域名枚举", "子域名 example.com")
# 7. 用户名
run_test("用户名搜索", "用户名 alan")
# 8. 存储检索
run_test("存储检索", "检索 测试")

print("\n" + "="*55)
print("\n📊 能力测试报告")
print(json.dumps(report, ensure_ascii=False, indent=2))