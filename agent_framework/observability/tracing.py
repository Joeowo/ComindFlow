"""
S4-T2: 链路追踪管理器

提供 Skill 执行的链路追踪功能，记录调用链和状态转换。
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any

from agent_framework.observability.models.trace import TraceData, StateTransition


class TraceManager:
    """链路追踪管理器

    管理 Skill 执行的完整追踪链路，包括：
    - trace_id 和 span_id 生成
    - 调用链记录
    - 状态转换记录

    Attributes:
        _traces: 存储所有追踪数据的字典
    """

    def __init__(self) -> None:
        """初始化追踪管理器"""
        self._traces: Dict[str, Dict[str, Any]] = {}
        # 每个 trace 存储: {trace_id: {spans: [], skill_chain: [], timestamps: {}}}

    def start_trace(self, context: Dict[str, Any]) -> str:
        """开始一个新的追踪

        Args:
            context: 初始上下文信息

        Returns:
            trace_id: 新生成的追踪 ID
        """
        trace_id = str(uuid.uuid4())
        self._traces[trace_id] = {
            "spans": [],
            "skill_chain": [],
            "timestamps": {
                "start": datetime.now(),
            },
            "state_transitions": [],
        }
        return trace_id

    def create_span(
        self,
        trace_id: str,
        skill_name: str,
        parent_span_id: Optional[str] = None
    ) -> str:
        """创建一个 span

        Args:
            trace_id: 追踪 ID
            skill_name: 技能名称
            parent_span_id: 父 span ID（可选）

        Returns:
            span_id: 新生成的 span ID

        Raises:
            KeyError: trace_id 不存在
        """
        if trace_id not in self._traces:
            raise KeyError(f"Trace {trace_id} not found")

        span_id = str(uuid.uuid4())
        span_data = {
            "span_id": span_id,
            "parent_span_id": parent_span_id,
            "skill_name": skill_name,
            "start_time": datetime.now(),
            "end_time": None,
            "result": None,
        }

        self._traces[trace_id]["spans"].append(span_data)

        # 添加到技能调用链（去重）
        if skill_name not in self._traces[trace_id]["skill_chain"]:
            self._traces[trace_id]["skill_chain"].append(skill_name)

        return span_id

    def end_span(
        self,
        trace_id: str,
        span_id: str,
        result: Dict[str, Any]
    ) -> None:
        """结束一个 span

        Args:
            trace_id: 追踪 ID
            span_id: span ID
            result: 执行结果

        Raises:
            KeyError: trace_id 不存在
            ValueError: span_id 不存在
        """
        if trace_id not in self._traces:
            raise KeyError(f"Trace {trace_id} not found")

        # 查找并更新 span
        for span in self._traces[trace_id]["spans"]:
            if span["span_id"] == span_id:
                span["end_time"] = datetime.now()
                span["result"] = result
                return

        raise ValueError(f"Span {span_id} not found in trace {trace_id}")

    def get_trace(self, trace_id: str) -> Optional[TraceData]:
        """获取完整追踪数据

        Args:
            trace_id: 追踪 ID

        Returns:
            TraceData 完整追踪数据，如果不存在返回 None
        """
        if trace_id not in self._traces:
            return None

        trace_data = self._traces[trace_id]

        # 获取最新的 span 作为当前 span
        current_span = None
        if trace_data["spans"]:
            current_span = trace_data["spans"][-1]

        return TraceData(
            trace_id=trace_id,
            parent_span_id=current_span["parent_span_id"] if current_span else None,
            span_id=current_span["span_id"] if current_span else "",
            skill_chain=trace_data["skill_chain"].copy(),
            timestamps=trace_data["timestamps"].copy(),
            state_transitions=list(trace_data["state_transitions"]),
        )
