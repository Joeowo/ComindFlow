"""
S4-T3: ErrorDiagnostics 异常诊断器测试

测试异常诊断和恢复建议功能。
"""

import pytest
from datetime import datetime


def test_diagnose_tool_not_found_error():
    """测试诊断工具未找到异常（P0）"""
    from agent_framework.observability.diagnostics import ErrorDiagnostics
    from agent_framework.observability.models.error import Severity

    diagnostics = ErrorDiagnostics()

    # 模拟上下文
    context = {
        "session_path": "/tmp/test",
        "state": {"current": "executing"},
    }

    report = diagnostics.diagnose(
        exception_type="ToolNotFoundError",
        error_message="Tool 'search' not found",
        skill_name="grill-me",
        context=context
    )

    assert report.severity == Severity.P0.value
    assert report.recovery_action is not None
    assert "Tool" in report.error_type or "NotFound" in report.error_type


def test_diagnose_dependency_error():
    """测试诊断依赖异常（P1）"""
    from agent_framework.observability.diagnostics import ErrorDiagnostics
    from agent_framework.observability.models.error import Severity

    diagnostics = ErrorDiagnostics()

    context = {
        "session_path": "/tmp/test",
        "state": {"current": "loading"},
    }

    report = diagnostics.diagnose(
        exception_type="DependencyError",
        error_message="Required module 'requests' not available",
        skill_name="advance-task",
        context=context
    )

    assert report.severity == Severity.P1.value
    assert report.recovery_action is not None


def test_diagnose_performance_warning():
    """测试诊断性能异常（P2）"""
    from agent_framework.observability.diagnostics import ErrorDiagnostics
    from agent_framework.observability.models.error import Severity

    diagnostics = ErrorDiagnostics()

    context = {
        "session_path": "/tmp/test",
        "execution_time_ms": 5000,  # 5秒，超出阈值
    }

    report = diagnostics.diagnose(
        exception_type="SlowExecutionWarning",
        error_message="Skill execution took 5000ms",
        skill_name="grill-me",
        context=context
    )

    assert report.severity == Severity.P2.value


def test_diagnose_unknown_error_defaults_to_p0():
    """测试未知异常默认为 P0"""
    from agent_framework.observability.diagnostics import ErrorDiagnostics
    from agent_framework.observability.models.error import Severity

    diagnostics = ErrorDiagnostics()

    context = {"session_path": "/tmp/test"}

    report = diagnostics.diagnose(
        exception_type="UnknownError",
        error_message="Something went wrong",
        skill_name="grill-me",
        context=context
    )

    assert report.severity == Severity.P0.value


def test_diagnosis_report_contains_all_fields():
    """测试诊断报告包含所有必需字段"""
    from agent_framework.observability.diagnostics import ErrorDiagnostics

    diagnostics = ErrorDiagnostics()

    context = {"session_path": "/tmp/test"}

    report = diagnostics.diagnose(
        exception_type="TestError",
        error_message="Test error message",
        skill_name="test-skill",
        context=context
    )

    assert hasattr(report, "error_id")
    assert hasattr(report, "error_type")
    assert hasattr(report, "severity")
    assert hasattr(report, "message")
    assert hasattr(report, "skill_name")
    assert hasattr(report, "timestamp")
    assert len(report.error_id) > 0
    assert isinstance(report.timestamp, datetime)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
