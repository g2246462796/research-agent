class Researcher:
    def __init__(self, llm):
        self.llm = llm

    def shallow_search(self, query):
        return "快速搜索结果"

    def deep_research(self, query):
        return "深度研究报告"