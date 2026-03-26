import os
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field

# 是一个枚举类，用于限定搜索 API 的可选类型
class SearchAPI(Enum):
    PERPLEXITY = "perplexity"
    TAVILY = "tavily"
    DUCKDUCKGO = "duckduckgo"
    SEARXNG = "searxng"
    ADVANCED = "advanced"


class Configuration(BaseModel):
    """深度研究助手的配置选项"""

    max_web_research_loops: int = Field(
        default=3,
        title="研究深度",
        description="执行的研究迭代次数，数值越大研究越深入。",
    )
    local_llm: str = Field(
        default="qwen3:4b",
        title="本地模型名称",
        description="本地托管的 LLM 名称（Ollama/LMStudio）",
    )
    llm_provider: str = Field(
        default="ollama",
        title="本地LLM 提供方",
        description="提供方标识（ollama、lmstudio 或 custom）",
    )
    search_api: SearchAPI = Field(
        default=SearchAPI.DUCKDUCKGO,
        title="搜索 API",
        description="要使用的网络搜索 API",
    )
    enable_notes: bool = Field(
        default=True,
        title="启用笔记",
        description="是否将任务进度存储在 NoteTool 中",
    )
    notes_workspace: str = Field(
        default="./notes",
        title="笔记工作区",
        description="NoteTool 保存任务笔记的目录",
    )
    fetch_full_page: bool = Field(
        default=True,
        title="获取完整页面",
        description="是否在搜索结果中包含完整页面内容",
    )
    ollama_base_url: str = Field(
        default="http://localhost:11434",
        title="Ollama 基础 URL",
        description="Ollama API 的基础 URL（不带 /v1 后缀）",
    )
    lmstudio_base_url: str = Field(
        default="http://localhost:1234/v1",
        title="LMStudio 基础 URL",
        description="LMStudio OpenAI 兼容 API 的基础 URL",
    )
    strip_thinking_tokens: bool = Field(
        default=True,
        title="去除思考标记",
        description="是否从模型响应中移除 <think> 标记",
    )
    use_tool_calling: bool = Field(
        default=False,
        title="使用工具调用",
        description="使用工具调用代替 JSON 模式进行结构化输出",
    )
    llm_api_key: Optional[str] = Field( # Optional 意味着该字段不是必须的，如果没有显式赋值，则默认为 None
        default=None,
        title="LLM API 密钥",
        description="使用自定义 OpenAI 兼容服务时可选的 API 密钥",
    )
    llm_base_url: Optional[str] = Field(
        default=None,
        title="LLM 基础 URL",
        description="使用自定义 OpenAI 兼容服务时可选的 API 基础 URL",
    )
    llm_model_id: Optional[str] = Field(
        default=None,
        title="LLM 模型 ID",
        description="使用自定义 OpenAI 兼容服务时可选的模型标识符",
    )
    """
    @classmethod 是 Python 的一个装饰器，用于定义类方法。类方法的第一个参数是类本身(通常命名为 cls),
    而不是实例(self)。它可以通过类直接调用，无需先创建实例。
    在你的代码中,from_env 被定义为类方法，目的是提供一种不依赖已有实例的替代构造方式。
    你可以直接通过 Configuration.from_env() 来创建一个配置对象，内部会读取环境变量并返回一个新的 Configuration 实例。
    这种用法也称为“工厂方法”，常见于需要根据外部条件灵活创建对象的场景。
    """
    @classmethod
    def from_env(cls, overrides: Optional[dict[str, Any]] = None) -> "Configuration":
        """使用环境变量和覆盖参数创建配置对象。"""

        raw_values: dict[str, Any] = {} # 表示这个字典的键是字符串，值可以是任意类型。

        # 基于字段名从环境变量中加载值
        for field_name in cls.model_fields.keys():  # 获取 Configuration 类的所有字段名
            env_key = field_name.upper()    # 转换为全大写形式
            if env_key in os.environ:
                raw_values[field_name] = os.environ[env_key]

        # 显式环境变量名的额外映射
        env_aliases = {
            "local_llm": os.getenv("LOCAL_LLM"),
            "llm_provider": os.getenv("LLM_PROVIDER"),
            "llm_api_key": os.getenv("LLM_API_KEY"),
            "llm_model_id": os.getenv("LLM_MODEL_ID"),
            "llm_base_url": os.getenv("LLM_BASE_URL"),
            "lmstudio_base_url": os.getenv("LMSTUDIO_BASE_URL"),
            "ollama_base_url": os.getenv("OLLAMA_BASE_URL"),
            "max_web_research_loops": os.getenv("MAX_WEB_RESEARCH_LOOPS"),
            "fetch_full_page": os.getenv("FETCH_FULL_PAGE"),
            "strip_thinking_tokens": os.getenv("STRIP_THINKING_TOKENS"),
            "use_tool_calling": os.getenv("USE_TOOL_CALLING"),
            "search_api": os.getenv("SEARCH_API"),
            "enable_notes": os.getenv("ENABLE_NOTES"),
            "notes_workspace": os.getenv("NOTES_WORKSPACE"),
        }

        for key, value in env_aliases.items():
            if value is not None:
                raw_values.setdefault(key, value)

        if overrides:
            for key, value in overrides.items():
                if value is not None:
                    raw_values[key] = value

        return cls(**raw_values)

    def sanitized_ollama_url(self) -> str:
        """确保 Ollama 基础 URL 包含 OpenAI 客户端所需的 /v1 后缀。"""

        base = self.ollama_base_url.rstrip("/")
        if not base.endswith("/v1"):
            base = f"{base}/v1"
        return base

    def resolved_model(self) -> Optional[str]:
        """尽力解析要使用的模型标识符。"""

        return self.llm_model_id or self.local_llm

