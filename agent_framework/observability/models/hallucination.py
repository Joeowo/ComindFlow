"""
S4-T4/T5: 幻觉检测数据模型
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any


@dataclass(frozen=True)
class UnauthorizedChange:
    """未授权的状态变更记录

    Attributes:
        key: 变化的键名
        old_value: 变化前的值
        new_value: 变化后的值
    """

    key: str
    old_value: Any
    new_value: Any


@dataclass(frozen=True)
class PollutionReport:
    """污染检测报告

    Attributes:
        has_pollution: 是否存在污染
        unauthorized_changes: 未授权的变更列表
        timestamp: 检测时间
    """

    has_pollution: bool
    unauthorized_changes: List[UnauthorizedChange] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class HallucinationReport:
    """幻觉检测报告

    Attributes:
        has_hallucination: 是否存在幻觉
        grounding_score: 贴地度分数 (0-1)
        critique_result: LLM 自我评估结果
        ungrounded_claims: 无依据的主张列表
    """

    has_hallucination: bool
    grounding_score: float = 0.0
    critique_result: Optional[str] = None
    ungrounded_claims: List[str] = field(default_factory=list)
