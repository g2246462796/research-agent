"""搜索调度辅助工具"""

from __future__ import annotations

import logging
from typing import Tuple, Optional, Any, Dict, List
from langchain_community.tools import DuckDuckGoSearchResults, TavilySearchResults
from langchain_core.tools import BaseTool
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper

from config import Configuration

from utils import (
    deduplicate_and_format_sources,
    format_sources,
    get_config_value,
)

logger = logging.getLogger(__name__)

MAX_TOKENS_PER_SOURCE = 2000
# 工具缓存，避免重复创建
_SEARCH_TOOLS: Dict[str, BaseTool] = {}

def _get_search_tool(backend: str, fetch_full_page: bool):
    """根据配置获取或创建 LangChain 搜索工具实例。"""
    if backend in _SEARCH_TOOLS: # 避免重复创建
        return _SEARCH_TOOLS[backend]

    if backend == "duckduckgo":
        # DuckDuckGo 工具默认返回摘要，不支持 fetch_full_page，忽略该参数
        wrapper = DuckDuckGoSearchAPIWrapper(max_results=5)
        tool = DuckDuckGoSearchResults(api_wrapper=wrapper, source="text")
    elif backend == "tavily":
        # Tavily 需要 API Key，可从环境变量或配置获取
        api_key = get_config_value("TAVILY_API_KEY")  # 假设你已将 TAVILY_API_KEY 放在环境变量或配置中
        if not api_key:
            raise ValueError("Tavily API key not set. Set TAVILY_API_KEY environment variable.")
        # TavilySearchResults 支持 include_raw_content 等参数
        tool = TavilySearchResults(
            max_results=5,
            api_key=api_key,
            include_raw_content=fetch_full_page,  # 如果 fetch_full_page 为 True，则获取完整内容
            include_answer=True,  # 可选，是否包含 AI 生成的答案
        )
    else:
        raise ValueError(f"Unsupported search backend: {backend}")

    _SEARCH_TOOLS[backend] = tool
    return tool

def dispatch_search(
    query: str,
    config: Configuration,
    loop_count: int,
) -> Tuple[Optional[Dict[str, Any]], List[str], Optional[str], str]:
    """使用 LangChain 搜索工具执行搜索，并标准化返回格式。"""
    search_api = get_config_value(config.search_api)

    try:
        tool = _get_search_tool(search_api, config.fetch_full_page)
        # 调用工具，LangChain 工具通常以字符串或对象形式返回结果
        raw_result = tool.run(query)  # 注意：某些工具可能需要不同的调用方式，如 invoke
        # 根据工具类型将结果转换为统一格式
        payload = _normalize_search_result(raw_result, search_api, config.fetch_full_page)
    except Exception as exc:
        logger.exception("Search backend %s failed: %s", search_api, exc)
        # 返回空结果，保留原异常处理方式
        payload = {
            "results": [],
            "backend": search_api,
            "answer": None,
            "notices": [str(exc)],
        }

    notices = list(payload.get("notices") or [])
    answer_text = payload.get("answer")
    results = payload.get("results", [])
    backend_label = str(payload.get("backend") or search_api)

    if notices:
        for notice in notices:
            logger.info("Search notice (%s): %s", backend_label, notice)

    logger.info(
        "Search backend=%s resolved_backend=%s answer=%s results=%s",
        search_api,
        backend_label,
        bool(answer_text),
        len(results),
    )

    return payload, notices, answer_text, backend_label

def _normalize_search_result(raw_result: Any, backend: str, fetch_full_page: bool) -> Dict[str, Any]:
    """将不同搜索工具的结果标准化为项目期望的字典格式。"""
    # 根据 backend 和 raw_result 的类型做转换
    if backend == "duckduckgo":
        # DuckDuckGoSearchResults 返回的是字符串列表，如 ["title: url - snippet"]
        if isinstance(raw_result, str):
            # 可能返回的是纯文本，需要解析
            return _parse_duckduckgo_string(raw_result)
        elif isinstance(raw_result, list):
            # 某些情况下返回列表
            results = []
            for item in raw_result:
                # 尝试解析每个元素
                results.append(_parse_duckduckgo_string(item))
            return {
                "results": results,
                "backend": backend,
                "answer": None,
                "notices": [],
            }
        else:
            return {
                "results": [],
                "backend": backend,
                "answer": None,
                "notices": [f"Unexpected result type: {type(raw_result)}"],
            }
    elif backend == "tavily":
        # TavilySearchResults 返回的是一个字典列表，每个字典包含 title, url, content 等
        if isinstance(raw_result, list):
            results = []
            for item in raw_result:
                result = {
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "content": item.get("content", ""),
                    "raw_content": item.get("raw_content", ""),
                }
                # 根据 fetch_full_page 决定是否保留完整内容
                if not fetch_full_page:
                    result.pop("raw_content", None)
                results.append(result)
            # Tavily 有时会返回一个 "answer" 字段（如果请求了）
            answer = raw_result.get("answer") if isinstance(raw_result, dict) else None
            return {
                "results": results,
                "backend": backend,
                "answer": answer,
                "notices": [],
            }
        else:
            return {
                "results": [],
                "backend": backend,
                "answer": None,
                "notices": [f"Unexpected result type: {type(raw_result)}"],
            }
    else:
        # 未知后端，返回空
        return {
            "results": [],
            "backend": backend,
            "answer": None,
            "notices": [f"Unknown backend: {backend}"],
        }


def _parse_duckduckgo_string(text: str) -> Dict[str, str]:
    """解析 DuckDuckGo 返回的字符串，提取标题、链接和摘要。"""
    # DuckDuckGoSearchResults 返回的字符串格式通常为 "Title: url - snippet"
    # 但可能因版本而异，这里做简单分割
    parts = text.split(" - ", 1)
    if len(parts) == 2:
        header, snippet = parts
        if ":" in header:
            title, url = header.split(":", 1)
            return {
                "title": title.strip(),
                "url": url.strip(),
                "content": snippet.strip(),
            }
    # 如果格式不符，直接返回原文本
    return {
        "title": "",
        "url": "",
        "content": text,
    }



def prepare_research_context(
    search_result: dict[str, Any] | None,
    answer_text: Optional[str],
    config: Configuration,
) -> tuple[str, str]:
    """将原始搜索结果加工成下游 Agent 可以直接使用的结构化信息"""

    sources_summary = format_sources(search_result)
    context = deduplicate_and_format_sources(
        search_result or {"results": []},
        max_tokens_per_source=MAX_TOKENS_PER_SOURCE,
        fetch_full_page=config.fetch_full_page,
    )

    if answer_text:
        context = f"AI直接答案：\n{answer_text}\n\n{context}"

    return sources_summary, context
