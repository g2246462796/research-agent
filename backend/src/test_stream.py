import asyncio
from dotenv import load_dotenv
from config import Configuration
from agent import DeepResearchAgent  # 假设你的 DeepResearchAgent 在 agent.py 中

load_dotenv()

async def test_stream():
    # 创建配置和 agent（仅用于获取 _create_text_agent）
    config = Configuration.from_env()
    agent = DeepResearchAgent(config=config)

    # 获取一个文本链（用于摘要）
    text_chain = agent._create_text_agent(system_prompt="你是一个测试助手，请简单回复用户。")

    # 测试消息
    prompt = "请说 hello"

    print("开始流式输出...")
    async for chunk in text_chain.astream({"messages": [("user", prompt)]}):
        print(f"chunk type: {type(chunk)}, content: {chunk if isinstance(chunk, str) else chunk}")
    print("流式结束")

if __name__ == "__main__":
    asyncio.run(test_stream())