import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI  # 国内模型大多兼容OpenAI格式
import yaml

load_dotenv()
# 从配置文件读取模型
def load_config():
    with open("configs/config.yml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

class CNLLM:
    def __init__(self):
        self.config = load_config()
        self.api_key = os.getenv("LLM_API_KEY")
        self.base_url = os.getenv("LLM_BASE_URL")
        self.model_name = self.config["llm"]["model_name"]  # 从config读取
        
        # 适配国内所有兼容OpenAI格式的模型
        self.llm = ChatOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            model=self.model_name,
            temperature=self.config["llm"]["temperature"]
        )

    def get_llm(self):
        return self.llm