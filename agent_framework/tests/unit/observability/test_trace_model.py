"""
S4-T1: TraceData 数据模型测试

测试链路追踪数据模型的基本功能。
"""

import pytest
from datetime import datetime


def test_trace_data_creation():
    """测试创建 TraceData 实例"""
    from agent_framework.observability.models.trace import TraceData

    # 创建一个基本的 TraceData
    trace = TraceData(
        trace_id="test-trace-123",
        parent_span_id=None,
        span_id="span-001",
        skill_chain=["grill-me"],
        timestamps={
            "start": datetime(2026, 6, 29, 10, 0, 0),
        },
        state_transitions=[]
    )

    assert trace.trace_id == "test-trace-123"
    assert trace.parent_span_id is None
    assert trace.span_id == "span-001"
    assert trace.skill_chain == ["grill-me"]
    assert len(trace.state_transitions) == 0


def test_trace_data_with_parent_span():
    """测试带有父 span 的 TraceData"""
    from agent_framework.observability.models.trace import TraceData

    trace = TraceData(
        trace_id="test-trace-456",
        parent_span_id="parent-span-001",
        span_id="child-span-001",
        skill_chain=["grill-me", "advance-task"],
        timestamps={},
        state_transitions=[]
    )

    assert trace.parent_span_id == "parent-span-001"
    assert trace.skill_chain == ["grill-me", "advance-task"]


def test_trace_data_immutability():
    """测试 TraceData 是不可变的（frozen=True）"""
    from agent_framework.observability.models.trace import TraceData

    trace = TraceData(
        trace_id="test-trace-789",
        parent_span_id=None,
        span_id="span-001",
        skill_chain=["grill-me"],
        timestamps={},
        state_transitions=[]
    )

    # frozen=True 的 dataclass 不可修改
    with pytest.raises(Exception):  # FrozenInstanceError
        trace.trace_id = "modified"


def test_state_transition_model():
    """测试 StateTransition 数据模型"""
    from agent_framework.observability.models.trace import StateTransition

    transition = StateTransition(
        from_state="idle",
        to_state="executing",
        timestamp=datetime(2026, 6, 29, 10, 0, 0),
        metadata={"skill": "grill-me"}
    )

    assert transition.from_state == "idle"
    assert transition.to_state == "executing"
    assert transition.metadata["skill"] == "grill-me"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
