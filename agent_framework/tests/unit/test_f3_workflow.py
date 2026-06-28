"""
F3 学术写作全流程 Workflow 测试

测试从澄清到完成的完整学术写作流程。
"""

import pytest
from agent_framework.core.state import AgentState
from pathlib import Path
import tempfile
import shutil


def test_clarify_topic_node_generates_questions():
    """测试 clarify_topic_node 生成澄清问题

    Given: 一个研究主题
    When: 调用 clarify_topic_node
    Then: 应生成相关的澄清问题列表
    """
    from agent_framework.workflows.f3_academic_writing import clarify_topic_node

    # 准备状态
    state: AgentState = {
        "current_step": "init",
        "tool_results": {},
        "retry_count": 0,
        "error_message": None,
        "session_path": tempfile.mkdtemp(),
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

    # 执行节点
    result = clarify_topic_node(state)

    # 验证
    assert "clarification_questions" in result
    assert isinstance(result["clarification_questions"], list)
    assert len(result["clarification_questions"]) > 0

    # 验证问题内容
    questions = result["clarification_questions"]
    assert any("核心论点" in q or "论点" in q for q in questions)
    assert any("创新点" in q or "创新" in q for q in questions)

    # 验证状态更新
    assert result["writing_phase"] == "clarification"
    assert result["current_step"] == "clarification"


def test_clarify_confirmation_node_sets_awaiting():
    """测试 clarify_confirmation_node 设置等待确认

    Given: 澄清问题已生成
    When: 调用 clarify_confirmation_node
    Then: 应设置 awaiting_confirmation 和确认提示
    """
    from agent_framework.workflows.f3_academic_writing import clarify_confirmation_node

    # 准备状态 - 已有澄清问题
    state: AgentState = {
        "current_step": "clarification",
        "tool_results": {},
        "retry_count": 0,
        "error_message": None,
        "session_path": tempfile.mkdtemp(),
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
        "writing_phase": "clarification",
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
        # 添加工具结果中的澄清问题
        "tool_results": {
            "clarification_questions": [
                "关于 'AI在教育中的应用'，你的核心论点是什么？",
                "这项研究的主要创新点在哪里？"
            ]
        }
    }

    # 执行节点
    result = clarify_confirmation_node(state)

    # 验证确认机制
    assert result["awaiting_confirmation"] is True
    assert result["confirmation_prompt"] is not None
    assert isinstance(result["confirmation_prompt"], str)
    assert len(result["confirmation_prompt"]) > 0

    # 验证提示内容包含关键信息
    prompt = result["confirmation_prompt"]
    assert "AI在教育中的应用" in prompt or "澄清" in prompt


def test_should_continue_clarification():
    """测试 should_continue_clarification 条件函数

    Given: 不同的用户确认状态
    When: 调用 should_continue_clarification
    Then: 应根据用户输入返回正确的路由
    """
    from agent_framework.workflows.f3_academic_writing import should_continue_clarification

    # 场景 1: 用户确认，有核心论点
    state_approved: AgentState = {
        "core_argument": "AI可以个性化学习路径",
        "awaiting_confirmation": False,
        # ... 其他字段
        "current_step": "",
        "tool_results": {},
        "retry_count": 0,
        "error_message": None,
        "session_path": "",
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
        "confirmation_prompt": None,
        "next_node": None,
        "workflow_name": "",
        "start_time": "",
        "writing_phase": "",
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

    result = should_continue_clarification(state_approved)
    assert result == "research", f"期望 'research', 实际 '{result}'"

    # 场景 2: 用户未确认，需要重新澄清
    state_retry: AgentState = state_approved.copy()
    state_retry["core_argument"] = ""
    state_retry["awaiting_confirmation"] = True

    result = should_continue_clarification(state_retry)
    assert result == "clarify", f"期望 'clarify', 实际 '{result}'"


def test_plan_research_node_generates_plan():
    """测试 plan_research_node 生成研究计划

    Given: 主题和核心论点
    When: 调用 plan_research_node
    Then: 应生成包含搜索查询和研究主题的计划
    """
    from agent_framework.workflows.f3_academic_writing import plan_research_node

    state: AgentState = {
        "current_step": "clarification",
        "tool_results": {},
        "retry_count": 0,
        "error_message": None,
        "session_path": tempfile.mkdtemp(),
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
        "writing_phase": "research",
        "core_argument": "AI可以个性化学习路径",
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

    result = plan_research_node(state)

    # 验证研究计划
    assert "research_plan" in result
    assert result["research_plan"] is not None
    assert "main_topics" in result["research_plan"]
    assert "search_queries" in result["research_plan"]
    assert len(result["research_plan"]["main_topics"]) > 0
    assert len(result["research_plan"]["search_queries"]) > 0

    # 验证状态更新
    assert result["writing_phase"] == "research"
    assert result["current_step"] == "research_planned"


def test_execute_research_node_calls_autoresearch():
    """测试 execute_research_node 调用 AutoResearch

    Given: 研究计划
    When: 调用 execute_research_node
    Then: 应调用 AutoResearch 并返回报告路径
    """
    from unittest.mock import patch, MagicMock
    from agent_framework.workflows.f3_academic_writing import execute_research_node

    state: AgentState = {
        "current_step": "research_planned",
        "tool_results": {},
        "retry_count": 0,
        "error_message": None,
        "session_path": tempfile.mkdtemp(),
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
        "writing_phase": "research",
        "core_argument": "AI可以个性化学习路径",
        "research_plan": {
            "main_topics": ["AI教育理论"],
            "search_queries": ["AI education", "personalized learning"]
        },
        "outline": None,
        "current_section_index": 0,
        "draft_paths": [],
        "review_results": None,
        "review_score": 0.0,
        "knowledge_points": [],
        "schedule_items": [],
        "review_plan_path": None,
    }

    # Mock AutoResearch 工具
    with patch('agent_framework.workflows.f3_academic_writing.research_single_tool') as mock_research:
        mock_research.invoke.return_value = "/tmp/test_report.md"

        result = execute_research_node(state)

        # 验证调用了 AutoResearch
        mock_research.invoke.assert_called_once()

        # 验证返回
        assert "report_path" in result
        assert result["report_path"] == "/tmp/test_report.md"
        assert result["current_step"] == "research_complete"


def test_research_confirmation_node_sets_awaiting():
    """测试 research_confirmation_node 设置等待确认

    Given: 研究已完成
    When: 调用 research_confirmation_node
    Then: 应设置确认提示等待用户确认
    """
    from agent_framework.workflows.f3_academic_writing import research_confirmation_node

    state: AgentState = {
        "current_step": "research_complete",
        "tool_results": {},
        "retry_count": 0,
        "error_message": None,
        "session_path": tempfile.mkdtemp(),
        "current_task_id": "",
        "cached_terminology": {},
        "cached_task_progress": {},
        "user_question": "",
        "query_result": None,
        "generated_answer": None,
        "knowledge_loaded": False,
        "cached_sources": {},
        "topic": "AI在教育中的应用",
        "report_path": "/tmp/test_report.md",
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
        "writing_phase": "research",
        "core_argument": "AI可以个性化学习路径",
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

    result = research_confirmation_node(state)

    # 验证确认机制
    assert result["awaiting_confirmation"] is True
    assert result["confirmation_prompt"] is not None
    assert "AI在教育中的应用" in result["confirmation_prompt"] or "研究" in result["confirmation_prompt"]
    assert result["next_node"] == "generate_outline"


def test_should_supplement_research():
    """测试 should_supplement_research 条件函数

    Given: 不同的用户确认状态
    When: 调用 should_supplement_research
    Then: 应根据用户输入返回正确的路由
    """
    from agent_framework.workflows.f3_academic_writing import should_supplement_research

    # 场景 1: 用户确认，继续写作
    state_continue: AgentState = {
        "research_approved": True,
        "awaiting_confirmation": False,
        "report_path": "/tmp/report.md",
        # 最小必需字段
        "current_step": "",
        "tool_results": {},
        "retry_count": 0,
        "error_message": None,
        "session_path": "",
        "current_task_id": "",
        "cached_terminology": {},
        "cached_task_progress": {},
        "user_question": "",
        "query_result": None,
        "generated_answer": None,
        "knowledge_loaded": False,
        "cached_sources": {},
        "topic": "",
        "key_concepts": [],
        "tasks": [],
        "current_questions": [],
        "user_question_suggestions": [],
        "answers": [],
        "mastery_level": "",
        "round": 0,
        "confirmation_prompt": None,
        "next_node": None,
        "workflow_name": "",
        "start_time": "",
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

    result = should_supplement_research(state_continue)
    assert result == "writing", f"期望 'writing', 实际 '{result}'"

    # 场景 2: 用户要求补充研究
    state_supplement: AgentState = state_continue.copy()
    state_supplement["research_approved"] = False
    state_supplement["awaiting_confirmation"] = False

    result = should_supplement_research(state_supplement)
    assert result == "supplement", f"期望 'supplement', 实际 '{result}'"


def test_generate_outline_node_creates_structure():
    """测试 generate_outline_node 创建大纲结构

    Given: 研究主题和核心论点
    When: 调用 generate_outline_node
    Then: 应生成包含标准学术章节的大纲
    """
    from agent_framework.workflows.f3_academic_writing import generate_outline_node

    state: AgentState = {
        "current_step": "research_complete",
        "tool_results": {},
        "retry_count": 0,
        "error_message": None,
        "session_path": tempfile.mkdtemp(),
        "current_task_id": "",
        "cached_terminology": {},
        "cached_task_progress": {},
        "user_question": "",
        "query_result": None,
        "generated_answer": None,
        "knowledge_loaded": False,
        "cached_sources": {},
        "topic": "AI在教育中的应用",
        "report_path": "/tmp/report.md",
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
        "writing_phase": "writing",
        "core_argument": "AI可以个性化学习路径",
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

    result = generate_outline_node(state)

    # 验证大纲结构
    assert "outline" in result
    assert result["outline"] is not None
    assert "title" in result["outline"]
    assert "sections" in result["outline"]
    assert len(result["outline"]["sections"]) == 6  # 标准学术论文结构

    # 验证章节名称
    section_names = [s["name"] for s in result["outline"]["sections"]]
    assert "Introduction" in section_names
    assert "Literature Review" in section_names
    assert "Methods" in section_names
    assert "Results" in section_names
    assert "Discussion" in section_names
    assert "Conclusion" in section_names


def test_draft_section_node_creates_draft_file():
    """测试 draft_section_node 创建草稿文件

    Given: 大纲和章节索引
    When: 调用 draft_section_node
    Then: 应创建章节草稿文件
    """
    from agent_framework.workflows.f3_academic_writing import draft_section_node
    from pathlib import Path

    temp_dir = tempfile.mkdtemp()

    state: AgentState = {
        "current_step": "outline_confirmed",
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
        "report_path": "/tmp/report.md",
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
        "writing_phase": "writing",
        "core_argument": "AI可以个性化学习路径",
        "research_plan": None,
        "outline": {
            "title": "AI在教育中的应用",
            "sections": [
                {"name": "Introduction", "subsections": ["背景"]},
                {"name": "Literature Review", "subsections": ["理论"]}
            ]
        },
        "current_section_index": 0,
        "draft_paths": [],
        "review_results": None,
        "review_score": 0.0,
        "knowledge_points": [],
        "schedule_items": [],
        "review_plan_path": None,
    }

    result = draft_section_node(state)

    # 验证草稿文件创建
    assert "current_section_index" in result
    assert result["current_section_index"] == 1
    assert "draft_paths" in result
    assert len(result["draft_paths"]) == 1

    # 验证文件存在
    draft_file = Path(result["draft_paths"][0])
    assert draft_file.exists()

    # 清理
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_self_review_node_performs_checks():
    """测试 self_review_node 执行审查检查

    Given: 草稿文件列表
    When: 调用 self_review_node
    Then: 应执行各项检查并返回评分
    """
    from agent_framework.workflows.f3_academic_writing import self_review_node

    # 创建临时草稿文件
    temp_dir = tempfile.mkdtemp()
    draft_file = Path(temp_dir) / "test_draft.md"
    draft_file.write_text("# Test Draft\n\nContent here...", encoding="utf-8")

    state: AgentState = {
        "current_step": "writing_complete",
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
        "workflow_name": "F3",
        "start_time": "2026-06-29T10:00:00",
        "writing_phase": "review",
        "core_argument": "",
        "research_plan": None,
        "outline": None,
        "current_section_index": 0,
        "draft_paths": [str(draft_file)],
        "review_results": None,
        "review_score": 0.0,
        "knowledge_points": [],
        "schedule_items": [],
        "review_plan_path": None,
    }

    result = self_review_node(state)

    # 验证审查结果
    assert "review_results" in result
    assert len(result["review_results"]) > 0
    assert "review_score" in result
    assert 0 <= result["review_score"] <= 1

    # 验证检查项
    checks = result["review_results"][0]["checks"]
    assert "argument_consistency" in checks
    assert "evidence_adequacy" in checks
    assert "logical_flow" in checks
    assert "academic_tone" in checks

    # 清理
    shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
