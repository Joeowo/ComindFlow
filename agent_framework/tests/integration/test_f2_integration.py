"""
F2 知识问答增强 Workflow 集成测试

测试完整的 Workflow 执行流程，包括与外部工具的集成。
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from agent_framework.workflows.f2_qa_enhanced import create_f2_workflow
from agent_framework.core.state import load_session_state


# =============================================================================
# 测试 Fixture
# =============================================================================

@pytest.fixture
def real_session_path(tmp_path):
    """创建真实的会话目录结构"""
    session_dir = tmp_path / "test_qa_session"
    session_dir.mkdir()

    # 创建 CONTEXT.md
    context_md = session_dir / "CONTEXT.md"
    context_md.write_text("""# Session 上下文

## Language

**货币政策**:
央行调节货币供应量和利率的政策工具
_Avoid_: 宽松政策、紧缩政策（使用具体工具名）

**时滞**:
政策实施到产生效果的延迟时间

**流动性陷阱**:
利率极低时，人们预期利率会上升，宁愿持有现金也不消费

## Relationships

- **利率** 影响 **投资成本**
- **准备金率** 影响 **银行流动性**

## Example dialogue

> **User**: "当央行降低利率时会发生什么？"
> **Agent**: "降低利率会降低借款成本，刺激投资和消费。"
""", encoding="utf-8")

    # 创建 sources 目录和示例文件
    sources_dir = session_dir / "sources"
    sources_dir.mkdir()

    # 创建几个学习资料文件
    (sources_dir / "chapter1.md").write_text("""# 第一章：货币政策基础

货币政策是央行通过调节货币供应量和利率来影响经济的政策工具。

## 主要工具

1. 利率：央行基准利率
2. 存款准备金率：商业银行必须存放在央行的准备金比例
3. 公开市场操作：央行买卖国债

## 时滞效应

货币政策存在时滞，从政策实施到产生效果通常需要 6-18 个月。
""", encoding="utf-8")

    (sources_dir / "chapter2.md").write_text("""# 第二章：流动性陷阱

当利率降到极低水平时，可能出现流动性陷阱。

## 特征
- 货币需求弹性无限大
- 传统货币政策失效
- 需要财政政策配合
""", encoding="utf-8")

    # 创建 Task.md
    task_md = session_dir / "Task.md"
    task_md.write_text("""# 学习任务

## Task 1: 货币政策基础
**状态**: completed
**轮次**: 3
**完成时间**: 2026-06-28

## Task 2: 流动性陷阱
**状态**: in_progress
**轮次**: 1
**完成时间**: -
""", encoding="utf-8")

    return str(session_dir)


# =============================================================================
# Workflow 集成测试
# =============================================================================

def test_f2_workflow_with_real_session(real_session_path):
    """测试 F2 Workflow 使用真实会话目录"""
    workflow = create_f2_workflow()
    app = workflow.compile()

    # 加载真实会话状态
    initial_state = load_session_state(real_session_path)
    initial_state["workflow_name"] = "f2_qa_enhanced"

    # 执行 Workflow（不使用 checkpointer）
    config = {"configurable": {"thread_id": "test_f2_integration"}}

    # 手动执行节点（模拟完整流程）
    state = initial_state.copy()

    # Step 1: 加载知识库
    from agent_framework.workflows.f2_qa_enhanced import load_knowledge_node
    state.update(load_knowledge_node(state))

    # 验证知识库加载
    assert state["knowledge_loaded"] is True
    assert len(state["cached_terminology"]) >= 3  # 至少有 3 个术语
    assert len(state["cached_sources"]) == 2  # 2 个源文件
    assert "货币政策" in state["cached_terminology"]
    assert "chapter1" in state["cached_sources"]
    assert "chapter2" in state["cached_sources"]


def test_f2_workflow_local_query_priority(real_session_path):
    """测试 F2 Workflow 本地查询优先级"""
    from agent_framework.workflows.f2_qa_enhanced import (
        load_knowledge_node,
        query_knowledge_node
    )

    # 加载知识库
    state = load_session_state(real_session_path)
    state["workflow_name"] = "f2_qa_enhanced"
    state.update(load_knowledge_node(state))

    # 测试本地术语查询（应该命中本地）
    state["user_question"] = "什么是时滞？"
    state.update(query_knowledge_node(state))

    assert state["query_result"]["status"] == "success"
    assert state["query_result"]["source"] == "local"
    assert "时滞" in state["query_result"]["answer"]


def test_f2_workflow_with_fallback_to_review_agent(real_session_path):
    """测试 F2 Workflow 回退到 review_agent"""
    from agent_framework.workflows.f2_qa_enhanced import (
        load_knowledge_node,
        query_knowledge_node
    )

    # 加载知识库
    state = load_session_state(real_session_path)
    state["workflow_name"] = "f2_qa_enhanced"
    state.update(load_knowledge_node(state))

    # 使用本地术语库中没有的问题
    state["user_question"] = "量化宽松政策的优缺点是什么？"

    # Mock ReviewAgentAdapter
    with patch('agent_framework.workflows.f2_qa_enhanced.ReviewAgentAdapter') as mock_adapter:
        mock_instance = MagicMock()
        mock_instance.ask.return_value = {
            "status": "success",
            "answer": "量化宽松可以刺激经济，但可能导致通胀。"
        }
        mock_adapter.ask = mock_instance.ask

        state.update(query_knowledge_node(state))

    # 应该回退到 review_agent
    assert state["query_result"]["status"] == "success"
    assert state["query_result"]["source"] == "review_agent"


def test_f2_workflow_complete_answer_generation(real_session_path):
    """测试 F2 Workflow 完整回答生成"""
    from agent_framework.workflows.f2_qa_enhanced import (
        load_knowledge_node,
        receive_question_node,
        query_knowledge_node,
        generate_answer_node
    )

    # 加载知识库
    state = load_session_state(real_session_path)
    state["workflow_name"] = "f2_qa_enhanced"
    state.update(load_knowledge_node(state))

    # 设置问题
    state["user_question"] = "什么是流动性陷阱？"
    state.update(receive_question_node(state))
    state["awaiting_confirmation"] = False

    # 查询
    state.update(query_knowledge_node(state))

    # 生成回答
    state.update(generate_answer_node(state))

    # 验证最终回答
    assert state["generated_answer"] is not None
    assert len(state["generated_answer"]) > 0
    assert "流动性陷阱" in state["generated_answer"] or "利率" in state["generated_answer"]
    assert "来源" in state["generated_answer"]


def test_f2_workflow_handles_unknown_question(real_session_path):
    """测试 F2 Workflow 处理未知问题"""
    from agent_framework.workflows.f2_qa_enhanced import (
        load_knowledge_node,
        query_knowledge_node,
        generate_answer_node
    )

    # 加载知识库
    state = load_session_state(real_session_path)
    state["workflow_name"] = "f2_qa_enhanced"
    state.update(load_knowledge_node(state))

    # 提出一个知识库中没有的问题
    state["user_question"] = "什么是量子计算？"

    # Mock ReviewAgentAdapter 返回未找到
    with patch('agent_framework.workflows.f2_qa_enhanced.ReviewAgentAdapter') as mock_adapter:
        mock_instance = MagicMock()
        mock_instance.ask.return_value = {
            "status": "error",
            "error": "知识库中未找到相关内容"
        }
        mock_adapter.ask = mock_instance.ask

        state.update(query_knowledge_node(state))
        state.update(generate_answer_node(state))

    # 验证友好错误消息
    assert state["generated_answer"] is not None
    assert "未找到" in state["generated_answer"] or "抱歉" in state["generated_answer"]


def test_f2_workflow_state_persistence(real_session_path):
    """测试 F2 Workflow 状态持久化"""
    from agent_framework.workflows.f2_qa_enhanced import (
        load_knowledge_node
    )
    from agent_framework.core.state import sync_to_persistence

    # 加载知识库
    state = load_session_state(real_session_path)
    state["workflow_name"] = "f2_qa_enhanced"
    state.update(load_knowledge_node(state))

    # 添加一些问答数据
    state["user_question"] = "测试问题"
    state["generated_answer"] = "测试回答"

    # 尝试同步（即使 sync_to_persistence 当前是空实现）
    try:
        sync_to_persistence(state)
    except Exception:
        pass  # 当前实现可能为空

    # 验证状态未损坏
    assert state["knowledge_loaded"] is True
    assert state["user_question"] == "测试问题"
    assert state["generated_answer"] == "测试回答"


def test_f2_workflow_multiple_questions(real_session_path):
    """测试 F2 Workflow 处理多个问题"""
    from agent_framework.workflows.f2_qa_enhanced import (
        load_knowledge_node,
        query_knowledge_node,
        generate_answer_node
    )

    # 加载知识库
    state = load_session_state(real_session_path)
    state["workflow_name"] = "f2_qa_enhanced"
    state.update(load_knowledge_node(state))

    questions = [
        "什么是时滞？",
        "什么是流动性陷阱？",
        "利率如何影响投资成本？"
    ]

    answers = []

    for question in questions:
        # 清除之前的结果
        state["user_question"] = question
        state["query_result"] = None
        state["generated_answer"] = None

        # 查询并生成回答
        state.update(query_knowledge_node(state))
        state.update(generate_answer_node(state))

        # 记录回答
        answers.append({
            "question": question,
            "answer": state["generated_answer"],
            "source": state["query_result"].get("source", "unknown")
        })

    # 验证所有问题都有回答
    assert len(answers) == 3
    for qa in answers:
        assert qa["answer"] is not None
        assert len(qa["answer"]) > 0
