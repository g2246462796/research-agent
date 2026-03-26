from models.llm import CNLLM
from core.orchestrator import Orchestrator

def run():
    print("🚀 NVIDIA AIQ 国产重构版 启动成功")
    llm = CNLLM().get_llm()
    orchestrator = Orchestrator(llm=llm)
    
    while True:
        query = input("\n请输入你的问题：")
        if query in ["exit", "quit"]:
            break
        result = orchestrator.run(query)
        print("\n📝 回答：", result)

if __name__ == "__main__":
    run()