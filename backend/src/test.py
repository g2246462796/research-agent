#!/usr/bin/env python
# test_research.py
import logging
import sys
from dotenv import load_dotenv

# 加载 .env 文件（确保在项目根目录）
load_dotenv()

# 导入你的项目模块
from config import Configuration
from agent import DeepResearchAgent  # 根据实际路径调整导入
from models import SummaryStateOutput

# 配置日志（可选，便于观察）
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def main():
    # 研究主题
    topic = "人工智能在医疗领域的最新应用"

    print(f"开始深度研究：{topic}")
    print("=" * 50)

    # # 方式一：使用便利函数
    # result: SummaryStateOutput = run_deep_research(topic)  # 如果导入了该函数
    # 方式二：直接实例化 Agent
    agent = DeepResearchAgent()
    result = agent.run(topic)

    print("\n最终报告：")
    print("=" * 50)
    print(result.report_markdown)
    print("=" * 50)
    print("研究完成。")

if __name__ == "__main__":
    main()