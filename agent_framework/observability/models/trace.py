"""
S4-T1: 可观测性数据模型

定义链路追踪和状态转换的数据结构。
遵循项目编码风格：使用 dataclass(frozen=True) 确保不可变性。
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any, List


@dataclass(frozen=True)
class ToolCallRecord:
    """工具调用记录

    记录单个工具调用的详细信息。

    Attributes:
        tool_name: 工具名称
        arguments: 调用参数
        result: 调用结果
        duration_ms: 执行时长（毫秒）
        timestamp: 调用时间戳
        error: 错误信息（如有）
    """

    tool_name: str
    arguments: Dict[str, Any]
    result: str
    duration_ms: int
    timestamp: datetime
    error: Optional[str] = None


@dataclass(frozen=True)
class StateTransition:
    """状态转换记录

    记录 Agent 状态的变化过程。

    Attributes:
        from_state: 转换前的状态
        to_state: 转换后的状态
        timestamp: 转换发生的时间戳
        metadata: 额外的元数据信息
    """

    from_state: str
    to_state: str
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TraceData:
    """执行链路追踪数据

    记录 Skill 执行的完整调用链和状态变化。

    Attributes:
        trace_id: 追踪 ID，唯一标识一次完整的执行
        parent_span_id: 父 span ID，用于建立调用层次关系
        span_id: 当前 span ID，唯一标识一个执行单元
        skill_chain: 技能调用链，记录执行的技能序列
        timestamps: 关键时间戳字典
        state_transitions: 状态转换列表
    """

    trace_id: str
    parent_span_id: Optional[str] = None
    span_id: str = ""
    skill_chain: List[str] = field(default_factory=list)
    timestamps: Dict[str, datetime] = field(default_factory=dict)
    state_transitions: List[StateTransition] = field(default_factory=list)
