"""Task summarization utilities."""

from __future__ import annotations

from collections.abc import Callable, Iterator
from typing import Any, Tuple

from models import SummaryState, TodoItem
from config import Configuration
from utils import strip_thinking_tokens
from services.text_processing import strip_tool_calls


class SummarizationService:
    """Handles synchronous and streaming task summarization."""

    def __init__(
        self,
        summarizer_factory: Callable[[], Any],
        config: Configuration,
    ) -> None:
        self._agent_factory = summarizer_factory
        self._config = config

    # ------------------------------------------------------------------
    # 同步摘要
    # ------------------------------------------------------------------
    def summarize_task(self, state: SummaryState, task: TodoItem, context: str) -> str:
        prompt = self._build_prompt(state, task, context)
        chain = self._agent_factory()  # 现在返回的是纯文本链
        output = chain.invoke({"messages": [("user", prompt)]})  # 直接返回纯文本
        summary_text = output.strip()
        if self._config.strip_thinking_tokens:
            summary_text = strip_thinking_tokens(summary_text)
        summary_text = strip_tool_calls(summary_text).strip()
        return summary_text or "暂无可用信息"

    # ------------------------------------------------------------------
    # 流式摘要
    # ------------------------------------------------------------------
    def stream_task_summary(
        self, state: SummaryState, task: TodoItem, context: str
    ) -> Tuple[Iterator[str], Callable[[], str]]:
        prompt = self._build_prompt(state, task, context)
        remove_thinking = self._config.strip_thinking_tokens
        raw_buffer = ""
        visible_output = ""
        emit_index = 0
        chain = self._agent_factory()  # 纯文本链

        def flush_visible() -> Iterator[str]:
            nonlocal emit_index, raw_buffer
            while True:
                start = raw_buffer.find("<think>", emit_index)
                if start == -1:
                    if emit_index < len(raw_buffer):
                        segment = raw_buffer[emit_index:]
                        emit_index = len(raw_buffer)
                        if segment:
                            yield segment
                    break

                if start > emit_index:
                    segment = raw_buffer[emit_index:start]
                    emit_index = start
                    if segment:
                        yield segment

                end = raw_buffer.find("</think>", start)
                if end == -1:
                    break
                emit_index = end + len("</think>")

        def generator() -> Iterator[str]:
            nonlocal raw_buffer, visible_output, emit_index
            try:
                for chunk in chain.stream({"messages": [("user", prompt)]}):
                    # print(f"chunk type: {type(chunk)}, content: {chunk[:100] if isinstance(chunk, str) else chunk}")
                    # chunk 已经是纯文本字符串
                    # 1. 兼容 StrOutputParser 已经生效的情况
                    if isinstance(chunk, str):
                        new_content = chunk
                    # 2. 兼容原始 agent 输出（字典）
                    elif isinstance(chunk, dict) and "messages" in chunk:
                        last_msg = chunk["messages"][-1]
                        new_content = last_msg.content if hasattr(last_msg, "content") else str(last_msg)
                    else:
                        new_content = str(chunk)
                    # 计算增量（因为流式通常是累积的）
                    if len(new_content) > len(raw_buffer):
                        delta = new_content[len(raw_buffer):]
                        raw_buffer = new_content
                    else:
                        delta = new_content
                        raw_buffer += new_content

                    if remove_thinking:
                        for segment in flush_visible():
                            visible_output += segment
                            if segment:
                                yield segment
                    else:
                        if delta:
                            visible_output += delta
                            yield delta
            finally:
                if remove_thinking:
                    for segment in flush_visible():
                        visible_output += segment
                        if segment:
                            yield segment

        def get_summary() -> str:
            if remove_thinking:
                cleaned = strip_thinking_tokens(visible_output)
            else:
                cleaned = visible_output
            return strip_tool_calls(cleaned).strip()

        return generator(), get_summary

    # ------------------------------------------------------------------
    # 提示构建
    # ------------------------------------------------------------------
    def _build_prompt(self, state: SummaryState, task: TodoItem, context: str) -> str:
        return (
            f"任务主题：{state.research_topic}\n"
            f"任务名称：{task.title}\n"
            f"任务目标：{task.intent}\n"
            f"检索查询：{task.query}\n"
            f"任务上下文：\n{context}\n"
            # f"{build_note_guidance(task)}\n"
            "返回一份面向用户的 Markdown 总结（仍遵循任务总结模板）。"
        )