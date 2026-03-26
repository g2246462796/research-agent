class Orchestrator:
    def __init__(self, llm):
        self.llm = llm

    def run(self, query: str):
        """
        核心调度：简单问题直接回答，复杂问题启动深度研究
        """
        print(f"\n🧠 正在分析问题：{query}")
        
        # 简化版逻辑：直接调用大模型回复
        # 后面我再帮你升级成 浅层研究 / 深度研究
        response = self.llm.invoke(query)
        
        return response.content