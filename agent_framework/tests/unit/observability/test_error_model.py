"""
S4-T1: ErrorRecord 数据模型测试

测试错误记录和工具调用的数据模型。
"""

import pytest
from datetime import datetime
from typing import Optional


def test_error_record_creation():
    """测试创建 ErrorRecord 实例"""
    from agent_framework.observability.models.error import ErrorRecord

    error = ErrorRecord(
        error_id="err-001",
        error_type="ToolNotFoundError",
        severity="P0",
        message="Tool 'not-found' not found",
        skill_name="grill-me",
        timestamp=datetime(2026, 6, 29, 10, 0, 0),
        recovery_action="Check tool registration"
    )

    assert error.error_id == "err-001"
    assert error.error_type == "ToolNotFoundError"
    assert error.severity == "P0"
    assert error.recovery_action == "Check tool registration"


def test_error_record_with_metadata():
    """测试带有元数据的 ErrorRecord"""
    from agent_framework.observability.models.error import ErrorRecord

    error = ErrorRecord(
        error_id="err-002",
        error_type="StateTransitionError",
        severity="P0",
        message="Invalid state transition",
        skill_name="advance-task",
        timestamp=datetime(2026, 6, 29, 10, 0, 0),
        recovery_action=None,
        metadata={"from": "idle", "to": "executing"}
    )

    assert error.metadata["from"] == "idle"
    assert error.recovery_action is None


def test_tool_call_record_creation():
    """测试创建 ToolCallRecord 实例"""
    from agent_framework.observability.models.trace import ToolCallRecord

    record = ToolCallRecord(
        tool_name="search",
        arguments={"query": "test"},
        result="Success",
        duration_ms=150,
        timestamp=datetime(2026, 6, 29, 10, 0, 0),
        error=None
    )

    assert record.tool_name == "search"
    assert record.arguments["query"] == "test"
    assert record.duration_ms == 150
    assert record.error is None


def test_tool_call_record_with_error():
    """测试带有错误的 ToolCallRecord"""
    from agent_framework.observability.models.trace import ToolCallRecord

    record = ToolCallRecord(
        tool_name="invalid_tool",
        arguments={},
        result="Failed",
        duration_ms=50,
        timestamp=datetime(2026, 6, 29, 10, 0, 0),
        error="Tool not found"
    )

    assert record.error == "Tool not found"
    assert record.result == "Failed"


def test_error_record_immutability():
    """测试 ErrorRecord 是不可变的"""
    from agent_framework.observability.models.error import ErrorRecord

    error = ErrorRecord(
        error_id="err-003",
        error_type="DataError",
        severity="P0",
        message="Data validation failed",
        skill_name="grill-me",
        timestamp=datetime(2026, 6, 29, 10, 0, 0),
        recovery_action="Fix data format"
    )

    with pytest.raises(Exception):  # FrozenInstanceError
        error.severity = "P1"


def test_severity_validation():
    """测试严重程度的有效值"""
    from agent_framework.observability.models.error import ErrorRecord, Severity

    # P0 - 可用性异常（最高优先级）
    error_p0 = ErrorRecord(
        error_id="err-p0",
        error_type="ToolNotFoundError",
        severity=Severity.P0.value,
        message="Critical error",
        skill_name="grill-me",
        timestamp=datetime(2026, 6, 29, 10, 0, 0),
        recovery_action="Immediate fix required"
    )
    assert error_p0.severity == "P0"

    # P1 - 依赖异常
    error_p1 = ErrorRecord(
        error_id="err-p1",
        error_type="DependencyError",
        severity=Severity.P1.value,
        message="Dependency issue",
        skill_name="advance-task",
        timestamp=datetime(2026, 6, 29, 10, 0, 0),
        recovery_action="Check dependencies"
    )
    assert error_p1.severity == "P1"

    # P2 - 性能异常
    error_p2 = ErrorRecord(
        error_id="err-p2",
        error_type="SlowExecutionWarning",
        severity=Severity.P2.value,
        message="Performance issue",
        skill_name="grill-me",
        timestamp=datetime(2026, 6, 29, 10, 0, 0),
        recovery_action="Optimize code"
    )
    assert error_p2.severity == "P2"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
