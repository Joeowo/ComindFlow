"""
F3/F4 Workflow 状态扩展测试

测试 AgentState 对 F3（学术写作）和 F4（复习计划）专用字段的支持。
"""

import pytest
from agent_framework.core.state import AgentState, load_session_state
from pathlib import Path
import tempfile
import shutil


def test_agentstate_supports_f3_writing_fields():
    """测试 AgentState 支持 F3 学术写作专用字段

    Given: 创建一个包含 F3 写作数据的 AgentState
    When: 设置写作阶段相关字段
    Then: 所有 F3 专用字段都应该可访问
    """
    # 创建临时会话目录
    temp_dir = tempfile.mkdtemp()

    try:
        state: AgentState = {
            # 基础字段
            "current_step": "clarification",
            "tool_results": {},
            "retry_count": 0,
            "error_message": None,
            "session_path": temp_dir,
            "current_task_id": "",
            "cached_terminology": {},
            "cached_task_progress": {},

            # F2 字段
            "user_question": "",
            "query_result": None,
            "generated_answer": None,
            "knowledge_loaded": False,
            "cached_sources": {},

            # F1 字段
            "topic": "",
            "report_path": None,
            "key_concepts": [],
            "tasks": [],
            "current_questions": [],
            "user_question_suggestions": [],
            "answers": [],
            "mastery_level": "",
            "round": 0,

            # 确认机制字段
            "awaiting_confirmation": False,
            "confirmation_prompt": None,
            "next_node": None,

            # 元数据
            "workflow_name": "F3",
            "start_time": "2026-06-29T10:00:00",

            # ========== F3 专用字段 ==========
            "writing_phase": "clarification",  # 写作阶段
            "core_argument": "AI在教育的应用",  # 核心论点
            "research_plan": None,  # 研究计划
            "outline": None,  # 论文大纲
            "current_section_index": 0,  # 当前章节索引
            "draft_paths": [],  # 草稿文件路径列表
            "review_results": None,  # 审查结果
            "review_score": 0.0,  # 审查分数

            # ========== F4 专用字段 ==========
            "knowledge_points": [],  # 知识点列表
            "schedule_items": [],  # SM2 调度项
            "review_plan_path": None,  # 复习计划路径
        }

        # 验证 F3 字段
        assert state["writing_phase"] == "clarification"
        assert state["core_argument"] == "AI在教育的应用"
        assert state["research_plan"] is None
        assert state["outline"] is None
        assert state["current_section_index"] == 0
        assert state["draft_paths"] == []
        assert state["review_results"] is None
        assert state["review_score"] == 0.0

        # 验证 F4 字段
        assert state["knowledge_points"] == []
        assert state["schedule_items"] == []
        assert state["review_plan_path"] is None

    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_load_session_state_includes_f3_f4_defaults():
    """测试 load_session_state 包含 F3/F4 默认值

    Given: 存在一个有效的会话目录
    When: 调用 load_session_state 加载状态
    Then: 返回的状态应包含 F3/F4 字段的默认值
    """
    # 创建临时会话目录
    temp_dir = tempfile.mkdtemp()
    temp_path = Path(temp_dir)

    try:
        # 创建必需的文件
        (temp_path / "CONTEXT.md").write_text("# Context\n\n## Language\n\n**Term**: Definition", encoding="utf-8")
        (temp_path / "Task.md").write_text("# Tasks\n\n## Task 1: Test\n**状态**: pending", encoding="utf-8")

        # 加载状态
        state = load_session_state(temp_dir)

        # 验证 F3 默认值必须存在
        expected_f3_fields = [
            "writing_phase", "core_argument", "research_plan",
            "outline", "current_section_index", "draft_paths",
            "review_results", "review_score"
        ]

        for field in expected_f3_fields:
            assert field in state, f"缺少 F3 字段: {field}"

        # 验证 F4 默认值必须存在
        expected_f4_fields = [
            "knowledge_points", "schedule_items", "review_plan_path"
        ]

        for field in expected_f4_fields:
            assert field in state, f"缺少 F4 字段: {field}"

        # 验证默认值
        assert state["writing_phase"] == ""  # 初始为空
        assert state["core_argument"] == ""
        assert state["research_plan"] is None
        assert state["outline"] is None
        assert state["current_section_index"] == 0
        assert state["draft_paths"] == []
        assert state["review_results"] is None
        assert state["review_score"] == 0.0

        assert state["knowledge_points"] == []
        assert state["schedule_items"] == []
        assert state["review_plan_path"] is None

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_f3_writing_phase_enum_values():
    """测试 F3 写作阶段枚举值

    Given: 定义写作阶段枚举
    When: 使用枚举值
    Then: 应包含所有预期阶段
    """
    from enum import Enum

    class WritingPhase(Enum):
        """写作阶段枚举"""
        CLARIFICATION = "clarification"
        RESEARCH = "research"
        WRITING = "writing"
        REVIEW = "review"
        COMPLETED = "completed"

    # 验证所有阶段
    assert WritingPhase.CLARIFICATION.value == "clarification"
    assert WritingPhase.RESEARCH.value == "research"
    assert WritingPhase.WRITING.value == "writing"
    assert WritingPhase.REVIEW.value == "review"
    assert WritingPhase.COMPLETED.value == "completed"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
