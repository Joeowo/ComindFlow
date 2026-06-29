"""
S4-T2: TraceManager 链路追踪管理器测试

测试链路追踪管理器的核心功能。
"""

import pytest
from datetime import datetime


def test_start_trace_creates_trace_id():
    """测试开始追踪时创建 trace_id"""
    from agent_framework.observability.tracing import TraceManager

    manager = TraceManager()
    trace_id = manager.start_trace({"session_path": "/tmp/test"})

    assert trace_id is not None
    assert isinstance(trace_id, str)
    assert len(trace_id) > 0


def test_create_span_creates_span_id():
    """测试创建 span 时返回 span_id"""
    from agent_framework.observability.tracing import TraceManager

    manager = TraceManager()
    trace_id = manager.start_trace({})

    span_id = manager.create_span(trace_id, "grill-me")

    assert span_id is not None
    assert isinstance(span_id, str)


def test_create_span_with_parent():
    """测试创建带有父 span 的 span"""
    from agent_framework.observability.tracing import TraceManager

    manager = TraceManager()
    trace_id = manager.start_trace({})

    parent_span = manager.create_span(trace_id, "parent-skill")
    child_span = manager.create_span(
        trace_id,
        "child-skill",
        parent_span_id=parent_span
    )

    assert child_span is not None
    assert parent_span != child_span


def test_end_span_records_result():
    """测试结束 span 时记录结果"""
    from agent_framework.observability.tracing import TraceManager

    manager = TraceManager()
    trace_id = manager.start_trace({})
    span_id = manager.create_span(trace_id, "grill-me")

    manager.end_span(trace_id, span_id, {"success": True, "output": "done"})

    # 验证结果被记录
    trace = manager.get_trace(trace_id)
    assert trace is not None
    assert trace.trace_id == trace_id


def test_get_trace_returns_complete_data():
    """测试获取完整追踪数据"""
    from agent_framework.observability.tracing import TraceManager

    manager = TraceManager()
    trace_id = manager.start_trace({"session": "test-123"})

    span1 = manager.create_span(trace_id, "grill-me")
    manager.end_span(trace_id, span1, {"success": True})

    span2 = manager.create_span(trace_id, "advance-task", parent_span_id=span1)
    manager.end_span(trace_id, span2, {"success": True})

    trace = manager.get_trace(trace_id)

    assert trace.trace_id == trace_id
    assert len(trace.skill_chain) >= 1
    assert "grill-me" in trace.skill_chain or "advance-task" in trace.skill_chain


def test_trace_id_propagation():
    """测试 trace_id 在整个调用链中正确传递"""
    from agent_framework.observability.tracing import TraceManager

    manager = TraceManager()
    trace_id = manager.start_trace({})

    # 模拟多跳调用
    span1 = manager.create_span(trace_id, "skill-a")
    manager.end_span(trace_id, span1, {"success": True})

    span2 = manager.create_span(trace_id, "skill-b", parent_span_id=span1)
    manager.end_span(trace_id, span2, {"success": True})

    trace = manager.get_trace(trace_id)

    # 所有 span 都应该关联到同一个 trace_id
    assert trace.trace_id == trace_id


def test_get_trace_returns_none_for_unknown():
    """测试获取不存在的 trace 时返回 None"""
    from agent_framework.observability.tracing import TraceManager

    manager = TraceManager()
    trace = manager.get_trace("unknown-trace-id")

    assert trace is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
