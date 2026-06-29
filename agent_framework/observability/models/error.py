"""
S4-T1: 错误记录数据模型

定义异常诊断相关的数据结构。
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum


class Severity(Enum):
    """异常严重程度

    P0 - 可用性异常：系统无法正常工作，必须立即修复
    P1 - 依赖异常：功能部分受损，影响用户体验
    P2 - 性能异常：系统可用但性能低于预期
    """

    P0 = "P0"  # 可用性异常（最高优先级）
    P1 = "P1"  # 依赖异常
    P2 = "P2"  # 性能异常


@dataclass(frozen=True)
class ErrorRecord:
    """错误记录

    记录 Skill 执行过程中的异常信息。

    Attributes:
        error_id: 错误唯一标识
        error_type: 错误类型（类名）
        severity: 严重程度（P0/P1/P2）
        message: 错误消息
        skill_name: 发生错误的技能名称
        timestamp: 错误发生时间
        recovery_action: 恢复建议
        metadata: 额外的元数据
    """

    error_id: str
    error_type: str
    severity: str
    message: str
    skill_name: str
    timestamp: datetime
    recovery_action: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
