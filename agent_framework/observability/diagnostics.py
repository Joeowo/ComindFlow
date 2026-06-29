"""
S4-T3: 异常诊断器

提供异常类型识别、严重程度判定和恢复建议功能。
"""

import uuid
from datetime import datetime
from typing import Dict, Any, Optional

from agent_framework.observability.models.error import ErrorRecord, Severity


class ErrorDiagnostics:
    """异常诊断器

    识别异常类型、判定严重程度并提供恢复建议。

    异常分类：
    - P0（可用性异常）：工具未找到、状态转换失败、数据验证失败
    - P1（依赖异常）：模块依赖问题、外部服务不可用
    - P2（性能异常）：执行缓慢、资源消耗高
    """

    # 异常类型到严重程度的映射
    _SEVERITY_MAP: Dict[str, str] = {
        # P0 - 可用性异常
        "ToolNotFoundError": Severity.P0.value,
        "StateTransitionError": Severity.P0.value,
        "DataValidationError": Severity.P0.value,
        "SkillExecutionError": Severity.P0.value,
        "ContextError": Severity.P0.value,

        # P1 - 依赖异常
        "DependencyError": Severity.P1.value,
        "ModuleImportError": Severity.P1.value,
        "ServiceUnavailableError": Severity.P1.value,

        # P2 - 性能异常
        "SlowExecutionWarning": Severity.P2.value,
        "HighResourceUsageWarning": Severity.P2.value,
        "MemoryUsageWarning": Severity.P2.value,
    }

    # 恢复建议模板
    _RECOVERY_ACTIONS: Dict[str, str] = {
        "ToolNotFoundError": "检查工具是否已正确注册到工具注册表",
        "StateTransitionError": "验证状态转换规则，检查当前状态是否有效",
        "DataValidationError": "检查输入数据格式，确保符合 schema 要求",
        "SkillExecutionError": "查看技能日志，确认技能代码无异常",
        "ContextError": "检查上下文初始化是否完整",
        "DependencyError": "安装缺失的依赖模块，检查 requirements.txt",
        "ModuleImportError": "确认模块已安装，检查 Python 路径配置",
        "ServiceUnavailableError": "检查外部服务状态，稍后重试",
        "SlowExecutionWarning": "分析性能瓶颈，考虑优化或增加超时时间",
        "HighResourceUsageWarning": "检查资源泄漏，优化代码逻辑",
        "MemoryUsageWarning": "检查内存使用，考虑分批处理或增加内存",
    }

    def diagnose(
        self,
        exception_type: str,
        error_message: str,
        skill_name: str,
        context: Dict[str, Any]
    ) -> ErrorRecord:
        """诊断异常并生成报告

        Args:
            exception_type: 异常类型名称
            error_message: 错误消息
            skill_name: 发生错误的技能名称
            context: 执行上下文

        Returns:
            ErrorRecord: 错误记录，包含严重程度和恢复建议
        """
        # 判定严重程度
        severity = self._SEVERITY_MAP.get(exception_type, Severity.P0.value)

        # 获取恢复建议
        recovery_action = self._RECOVERY_ACTIONS.get(exception_type)

        return ErrorRecord(
            error_id=str(uuid.uuid4()),
            error_type=exception_type,
            severity=severity,
            message=error_message,
            skill_name=skill_name,
            timestamp=datetime.now(),
            recovery_action=recovery_action,
            metadata=context.copy() if context else {},
        )
