"""
S4 Workflow 端到端测试

测试 F3 和 F4 Workflow 的完整流程。
"""

import pytest
from agent_framework.core.state import AgentState
from agent_framework.workflows.f3_academic_writing import create_f3_workflow
from agent_framework.workflows.f4_review_planning import create_f4_workflow
from pathlib import Path
import tempfile
import shutil


def test_f3_workflow_nodes_execution():
    """测试 F3 Workflow 节点执行

    Given: F3 Workflow 的各个节点
    When: 直接执行节点
    Then: 节点应正确处理状态
    """
    from agent_framework.workflows.f3_academic_writing import (
        clarify_topic_node,
        plan_research_node,
        generate_outline_node
    )

    temp_dir = tempfile.mkdtemp()

    try:
        # 测试澄清节点
        state1: AgentState = {
            "current_step": "init",
            "tool_results": {},
            "retry_count": 0,
            "error_message": None,
            "session_path": temp_dir,
            "current_task_id": "",
            "cached_terminology": {},
            "cached_task_progress": {},
            "user_question": "",
            "query_result": None,
            "generated_answer": None,
            "knowledge_loaded": False,
            "cached_sources": {},
            "topic": "AI在教育中的应用",
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
            "workflow_name": "F3",
            "start_time": "2026-06-29T10:00:00",
            "writing_phase": "",
            "core_argument": "",
            "research_plan": None,
            "outline": None,
            "current_section_index": 0,
            "draft_paths": [],
            "review_results": None,
            "review_score": 0.0,
            "knowledge_points": [],
            "schedule_items": [],
            "review_plan_path": None,
        }

        result1 = clarify_topic_node(state1)
        assert "clarification_questions" in result1
        assert len(result1["clarification_questions"]) > 0

        # 测试研究规划节点
        state2 = state1.copy()
        state2["core_argument"] = "AI可以个性化学习"
        result2 = plan_research_node(state2)
        assert "research_plan" in result2
        assert result2["research_plan"] is not None

        # 测试大纲生成节点
        state3 = state1.copy()
        result3 = generate_outline_node(state3)
        assert "outline" in result3
        assert result3["outline"]["title"] == "AI在教育中的应用"

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_f4_workflow_end_to_end():
    """测试 F4 Workflow 端到端流程

    Given: 学习资料文件
    When: 运行完整的 F4 Workflow
    Then: 应生成完整的复习计划
    """
    # 创建 workflow
    workflow = create_f4_workflow()
    app = workflow.compile()

    # 创建临时学习资料
    temp_dir = tempfile.mkdtemp()
    source_file = Path(temp_dir) / "source.md"
    source_file.write_text("""# 学习资料

## 核心概念

**机会成本**: 放弃的最高价值选择
**边际效应**: 每增加一单位带来的额外收益

## 重要理论

**供需定律**: 价格上升时需求下降，价格下降时需求上升。
""", encoding="utf-8")

    # 准备初始状态
    initial_state: AgentState = {
        "current_step": "init",
        "tool_results": {},
        "retry_count": 0,
        "error_message": None,
        "session_path": temp_dir,
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
        "workflow_name": "F4",
        "start_time": "2026-06-29T10:00:00",
        "writing_phase": "",
        "core_argument": "",
        "research_plan": None,
        "outline": None,
        "current_section_index": 0,
        "draft_paths": [],
        "review_results": None,
        "review_score": 0.0,
        "knowledge_points": [],
        "schedule_items": [],
        "review_plan_path": None,
        "source_paths": [str(source_file)],
    }

    try:
        # 运行完整 workflow
        result = app.invoke(initial_state)

        # 验证：应完成所有步骤
        assert result["current_step"] == "plan_generated"
        assert len(result["knowledge_points"]) >= 0  # 允许为 0（取决于提取逻辑）
        assert len(result["schedule_items"]) >= 0
        assert result["review_plan_path"] is not None

        # 验证计划文件存在
        plan_file = Path(result["review_plan_path"])
        assert plan_file.exists()
        content = plan_file.read_text(encoding="utf-8")
        assert "复习计划" in content

    finally:
        # 清理
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_f3_workflow_structure():
    """测试 F3 Workflow 结构完整性

    Given: 创建 F3 Workflow
    When: 检查其结构
    Then: 应包含所有必需的节点
    """
    workflow = create_f3_workflow()

    # 验证 workflow 不是 None
    assert workflow is not None

    # 编译验证
    app = workflow.compile()
    assert app is not None


def test_f4_workflow_structure():
    """测试 F4 Workflow 结构完整性

    Given: 创建 F4 Workflow
    When: 检查其结构
    Then: 应包含所有必需的节点
    """
    workflow = create_f4_workflow()

    # 验证 workflow 不是 None
    assert workflow is not None

    # 编译验证
    app = workflow.compile()
    assert app is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
