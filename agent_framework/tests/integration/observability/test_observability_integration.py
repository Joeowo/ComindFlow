"""
S4-T8: 可观测性集成测试

测试完整的可观测性流程：追踪、诊断、存储。
"""

import pytest
import tempfile
import os
from datetime import datetime


def test_full_observability_workflow():
    """测试完整的可观测性工作流"""
    from agent_framework.observability.tracing import TraceManager
    from agent_framework.observability.diagnostics import ErrorDiagnostics
    from agent_framework.observability.dashboard import ObservabilityDashboard

    # 创建组件
    trace_manager = TraceManager()
    diagnostics = ErrorDiagnostics()
    dashboard = ObservabilityDashboard()

    # 模拟完整的执行流程
    trace_id = trace_manager.start_trace({"session": "test-123"})

    # 创建第一个 span
    span1 = trace_manager.create_span(trace_id, "grill-me")
    trace_manager.end_span(trace_id, span1, {"success": True})

    # 创建嵌套的 span
    span2 = trace_manager.create_span(trace_id, "advance-task", parent_span_id=span1)
    trace_manager.end_span(trace_id, span2, {"success": True})

    # 验证追踪数据
    trace = trace_manager.get_trace(trace_id)
    assert trace is not None
    assert trace.trace_id == trace_id
    assert len(trace.skill_chain) >= 1


def test_error_diagnosis_workflow():
    """测试异常诊断工作流"""
    from agent_framework.observability.diagnostics import ErrorDiagnostics
    from agent_framework.observability.dashboard import ObservabilityDashboard

    diagnostics = ErrorDiagnostics()
    dashboard = ObservabilityDashboard()

    # 模拟错误发生
    error_record = diagnostics.diagnose(
        exception_type="ToolNotFoundError",
        error_message="Tool 'search' not found",
        skill_name="grill-me",
        context={"session": "/tmp/test"}
    )

    # 验证错误记录
    assert error_record.severity == "P0"
    assert error_record.recovery_action is not None

    # 记录到 Dashboard
    dashboard.record_error(error_record)

    # 验证统计
    stats = dashboard.get_error_stats()
    assert stats.total_errors == 1
    assert stats.by_severity.get("P0", 0) == 1


def test_storage_persistence():
    """测试 SQLite 存储持久化"""
    from agent_framework.observability.storage import StorageManager
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_observability.db")

        storage = StorageManager(db_path)
        try:
            storage.initialize()

            # 保存追踪数据
            storage.save_trace("trace-123", {"skill": "test", "success": True})

            # 保存错误记录
            storage.save_error({
                "error_id": "err-001",
                "error_type": "TestError",
                "severity": "P0",
                "message": "Test error",
            })

            # 验证数据可以读取
            trace = storage.get_trace("trace-123")
            assert trace is not None

            errors = storage.get_errors()
            assert len(errors) >= 1
        finally:
            storage.close()  # 显式关闭连接


def test_data_cleanup():
    """测试数据清理机制"""
    from agent_framework.observability.storage import StorageManager
    from datetime import datetime, timedelta
    import time
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_cleanup.db")

        storage = StorageManager(db_path)
        try:
            storage.initialize()

            # 保存新数据
            storage.save_trace("new-trace", {"created_at": datetime.now().isoformat()})

            # 清理 7 天前的数据
            deleted_count = storage.cleanup_old_data(days=7)

            # 验证新数据保留
            new_trace = storage.get_trace("new-trace")
            assert new_trace is not None  # 应该保留
        finally:
            storage.close()  # 显式关闭连接


def test_dashboard_integration_with_storage():
    """测试 Dashboard 与存储的集成"""
    from agent_framework.observability.dashboard import ObservabilityDashboard
    from agent_framework.observability.storage import StorageManager
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_dashboard.db")

        storage = StorageManager(db_path)
        try:
            storage.initialize()

            # 初始化 Dashboard
            dashboard = ObservabilityDashboard()

            # 记录一些技能调用
            dashboard.record_skill_call("grill-me")
            dashboard.record_skill_call("grill-me")
            dashboard.record_skill_call("advance-task")

            # 获取排行
            ranking = dashboard.get_skill_ranking()
            assert len(ranking) == 2
            assert ranking[0].skill_name == "grill-me"
            assert ranking[0].call_count == 2
        finally:
            storage.close()  # 显式关闭连接


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
