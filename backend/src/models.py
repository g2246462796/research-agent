"""深度研究工作流使用的状态模型。"""

import operator # 提供内置操作符函数,常与 Annotated 配合用于合并操作
from dataclasses import dataclass, field    # 简化类的定义，自动生成 __init__、__repr__ 等方法。field 用于配置字段的默认值、是否参与比较等。
from typing import List, Optional           # List[str] 表示字符串列表，Optional[int] 表示可以是 int 或 None

from typing_extensions import Annotated     # 提供 Annotated 类型，用于给类型添加额外元数据


# 任务状态管理和追踪功能
@dataclass(kw_only=True)
class TodoItem:
    """单个待办任务项。"""

    id: int
    title: str
    intent: str
    query: str
    status: str = field(default="pending")
    summary: Optional[str] = field(default=None)
    sources_summary: Optional[str] = field(default=None)
    notices: list[str] = field(default_factory=list)
    note_id: Optional[str] = field(default=None)
    note_path: Optional[str] = field(default=None)
    stream_token: Optional[str] = field(default=None)


# 全局状态
@dataclass(kw_only=True)
class SummaryState:
    research_topic: str = field(default=None)  # 研究主题
    search_query: str = field(default=None)  # 已弃用
    web_research_results: Annotated[list, operator.add] = field(default_factory=list)
    sources_gathered: Annotated[list, operator.add] = field(default_factory=list)
    research_loop_count: int = field(default=0)  # 当前已执行的研究迭代次数，用于控制最大循环。
    running_summary: str = field(default=None)  # 旧版摘要字段，可能被 structured_report 取代。
    todo_items: Annotated[list, operator.add] = field(default_factory=list)
    structured_report: Optional[str] = field(default=None)
    report_note_id: Optional[str] = field(default=None)
    report_note_path: Optional[str] = field(default=None)

# 定义研究开始时必须提供的初始信息
@dataclass(kw_only=True)
class SummaryStateInput:
    research_topic: str = field(default=None)  # 研究主题

# 定义研究完成后对外输出的结果
@dataclass(kw_only=True)
class SummaryStateOutput:
    running_summary: str = field(default=None)  # Backward-compatible文本
    report_markdown: Optional[str] = field(default=None)
    todo_items: List[TodoItem] = field(default_factory=list)

