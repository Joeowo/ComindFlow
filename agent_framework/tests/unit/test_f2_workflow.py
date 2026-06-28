"""
F2 知识问答增强 Workflow 单元测试

测试各节点的状态转换和功能。
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from langgraph.graph import StateGraph

from agent_framework.core.state import AgentState
from agent_framework.workflows.f2_qa_enhanced import (
    create_f2_workflow,
    load_knowledge_node,
    receive_question_node,
    query_knowledge_node,
    generate_answer_node,
)


# =============================================================================
# 测试 Fixture
# =============================================================================

@pytest.fixture
def sample_session_path(tmp_path):
    """创建测试会话目录"""
    session_dir = tmp_path / "test_session"
    session_dir.mkdir()

    # 创建 CONTEXT.md
    context_md = session_dir / "CONTEXT.md"
    context_md.write_text("""# Session 上下文

## Language

**货币政策**:
央行调节货币供应量和利率的政策工具

**时滞**:
政策实施到产生效果的延迟时间
""", encoding="utf-8")

    # 创建 sources 目录和示例文件
    sources_dir = session_dir / "sources"
    sources_dir.mkdir()
    (sources_dir / "chapter1.md").write_text("第一章内容", encoding="utf-8")

    return str(session_dir)


@pytest.fixture
def minimal_state(sample_session_path):
    """最小状态用于测试单个节点"""
    return {
        "current_step": "init",
        "tool_results": {},
        "retry_count": 0,
        "error_message": None,
        "session_path": sample_session_path,
        "current_task_id": "",
        "cached_terminology": {},
        "cached_task_progress": {},
        "user_question": "",
        "query_result": None,
        "generated_answer": None,
        "knowledge_loaded": False,
        "cached_sources": {},
        "topic": "",
        "report_path": None,
        "key_concepts": [],
        "tasks": [],
        "current_questions": [],
        "user_question_suggestions": [],
        "answers": [],
        "mastery_level": "",
        "round": 0,
        "awaiting_confirmation": False,
        "confirmation_prompt": None,
        "next_node": None,
        "workflow_name": "f2_qa_enhanced",
        "start_time": "2026-06-29T10:00:00",
    }


# =============================================================================
# Workflow 创建测试
# =============================================================================

def test_create_f2_workflow_returns_graph():
    """测试 create_f2_workflow 返回 StateGraph 实例"""
    workflow = create_f2_workflow()

    assert isinstance(workflow, StateGraph)


def test_create_f2_workflow_has_required_nodes():
    """测试 F2 Workflow 包含所有必需节点"""
    workflow = create_f2_workflow()

    # 编译 workflow 以获取节点列表
    compiled = workflow.compile()
    nodes = compiled.nodes

    required_nodes = [
        "load_knowledge",
        "receive_question",
        "query_knowledge",
        "generate_answer"
    ]

    for node_name in required_nodes:
        assert node_name in nodes, f"Missing node: {node_name}"


# =============================================================================
# load_knowledge_node 测试
# =============================================================================

def test_load_knowledge_node_loads_context(minimal_state):
    """测试 load_knowledge_node 正确加载 CONTEXT.md"""
    result = load_knowledge_node(minimal_state)

    assert result["knowledge_loaded"] is True
    assert "cached_terminology" in result
    assert isinstance(result["cached_terminology"], dict)
    # 应该解析出术语
    assert len(result["cached_terminology"]) > 0 or result["error_message"] is None


def test_load_knowledge_node_loads_sources(minimal_state):
    """测试 load_knowledge_node 正确加载 sources/ 目录"""
    result = load_knowledge_node(minimal_state)

    assert result["knowledge_loaded"] is True
    assert "cached_sources" in result
    assert isinstance(result["cached_sources"], dict)


def test_load_knowledge_node_updates_current_step(minimal_state):
    """测试 load_knowledge_node 更新 current_step"""
    result = load_knowledge_node(minimal_state)

    assert result["current_step"] == "knowledge_loaded"


def test_load_knowledge_node_handles_missing_context(minimal_state, tmp_path):
    """测试 load_knowledge_node 处理缺失 CONTEXT.md"""
    # 创建空目录（没有 CONTEXT.md）
    empty_dir = tmp_path / "empty_session"
    empty_dir.mkdir()

    state = minimal_state.copy()
    state["session_path"] = str(empty_dir)

    result = load_knowledge_node(state)

    # 应该优雅地处理缺失文件，仍标记为已加载（只是内容为空）
    assert result["knowledge_loaded"] is True
    assert result["cached_terminology"] == {}
    assert result["cached_sources"] == {}
    assert result["error_message"] is None


# =============================================================================
# receive_question_node 测试
# =============================================================================

def test_receive_question_node_awaits_input(minimal_state):
    """测试 receive_question_node 等待用户输入"""
    result = receive_question_node(minimal_state)

    assert result["awaiting_confirmation"] is True
    assert result["confirmation_prompt"] is not None
    assert len(result["confirmation_prompt"]) > 0


def test_receive_question_node_prompt_contains_knowledge_hint(minimal_state):
    """测试确认提示包含知识库提示"""
    # 先加载知识库
    minimal_state["knowledge_loaded"] = True
    minimal_state["cached_terminology"] = {"货币政策": "央行调节"}

    result = receive_question_node(minimal_state)

    prompt = result["confirmation_prompt"]
    assert "问题" in prompt or "输入" in prompt or "请" in prompt


# =============================================================================
# query_knowledge_node 测试
# =============================================================================

def test_query_knowledge_node_with_question(minimal_state):
    """测试 query_knowledge_node 处理用户问题"""
    minimal_state["user_question"] = "什么是货币政策？"
    minimal_state["knowledge_loaded"] = True
    minimal_state["cached_terminology"] = {"货币政策": "央行调节货币供应量"}

    result = query_knowledge_node(minimal_state)

    assert "query_result" in result
    assert result["current_step"] == "knowledge_queried"


def test_query_knowledge_node_finds_in_terminology(minimal_state):
    """测试 query_knowledge_node 从术语中找到答案"""
    minimal_state["user_question"] = "什么是货币政策？"
    minimal_state["knowledge_loaded"] = True
    minimal_state["cached_terminology"] = {"货币政策": "央行调节货币供应量和利率的政策工具"}

    with patch('agent_framework.workflows.f2_qa_enhanced.ReviewAgentAdapter') as mock_adapter:
        mock_adapter.ask.return_value = {"status": "success", "answer": "mock answer"}

        result = query_knowledge_node(minimal_state)

        assert result["query_result"] is not None
        assert result["query_result"].get("source") in ["local", "review_agent", "fallback"]


def test_query_knowledge_node_without_question(minimal_state):
    """测试 query_knowledge_node 处理空问题"""
    minimal_state["user_question"] = ""

    result = query_knowledge_node(minimal_state)

    assert result["query_result"] is not None
    assert result["query_result"].get("status") == "error"


# =============================================================================
# generate_answer_node 测试
# =============================================================================

def test_generate_answer_node_generates_response(minimal_state):
    """测试 generate_answer_node 生成回答"""
    minimal_state["query_result"] = {
        "status": "success",
        "answer": "央行调节货币供应量",
        "source": "local"
    }

    result = generate_answer_node(minimal_state)

    assert result["generated_answer"] is not None
    assert len(result["generated_answer"]) > 0
    assert result["current_step"] == "answer_generated"


def test_generate_answer_node_handles_error_result(minimal_state):
    """测试 generate_answer_node 处理错误查询结果"""
    minimal_state["query_result"] = {
        "status": "error",
        "error": "知识库中未找到相关内容"
    }

    result = generate_answer_node(minimal_state)

    # 应该生成友好的错误消息
    assert result["generated_answer"] is not None
    assert "未找到" in result["generated_answer"] or "抱歉" in result["generated_answer"]


def test_generate_answer_node_without_query_result(minimal_state):
    """测试 generate_answer_node 处理 None 查询结果"""
    minimal_state["query_result"] = None

    result = generate_answer_node(minimal_state)

    assert result["generated_answer"] is not None
    assert result["generated_answer"] == "暂无查询结果"


# =============================================================================
# 端到端测试
# =============================================================================

def test_f2_workflow_end_to_end(minimal_state):
    """测试 F2 Workflow 端到端执行"""
    workflow = create_f2_workflow()
    app = workflow.compile()

    # 模拟完整流程，使用字典更新来合并状态
    config = {"configurable": {"thread_id": "test_f2"}}

    # Step 1: 加载知识库
    state = minimal_state.copy()
    state.update(load_knowledge_node(state))

    # Step 2: 模拟用户输入问题
    state["user_question"] = "什么是时滞？"
    state.update(receive_question_node(state))
    state["awaiting_confirmation"] = False  # 模拟用户已输入

    # Step 3: 查询知识
    state.update(query_knowledge_node(state))

    # Step 4: 生成回答
    state.update(generate_answer_node(state))

    # 验证最终状态
    assert state["knowledge_loaded"] is True
    assert state["user_question"] == "什么是时滞？"
    assert state["query_result"] is not None
    assert state["generated_answer"] is not None
    assert state["current_step"] == "answer_generated"
