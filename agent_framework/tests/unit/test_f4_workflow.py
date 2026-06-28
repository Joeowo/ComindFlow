"""
F4 复习计划生成 Workflow 测试

测试基于 SM2 算法的复习计划生成流程。
"""

import pytest
from agent_framework.core.state import AgentState
from pathlib import Path
import tempfile
import shutil


def test_extract_knowledge_node_extracts_concepts():
    """测试 extract_knowledge_node 提取知识点

    Given: 学习资料路径
    When: 调用 extract_knowledge_node
    Then: 应提取知识点并生成问题池
    """
    from agent_framework.workflows.f4_review_planning import extract_knowledge_node

    # 创建临时学习资料
    temp_dir = tempfile.mkdtemp()
    source_file = Path(temp_dir) / "source.md"
    source_file.write_text("# 学习资料\n\n## 核心概念\n\n- **知识点1**: 定义1\n- **知识点2**: 定义2\n", encoding="utf-8")

    state: AgentState = {
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

    result = extract_knowledge_node(state)

    # 验证知识点提取
    assert "knowledge_points" in result
    assert len(result["knowledge_points"]) > 0

    # 验证知识点结构
    kp = result["knowledge_points"][0]
    assert "question" in kp
    assert "answer" in kp

    # 清理
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_sm2_schedule_node_calculates_intervals():
    """测试 sm2_schedule_node 计算 SM2 间隔

    Given: 知识点列表
    When: 调用 sm2_schedule_node
    Then: 应使用 SM2 算法计算复习间隔
    """
    from agent_framework.workflows.f4_review_planning import sm2_schedule_node

    knowledge_points = [
        {"question": "什么是机会成本？", "answer": "放弃的最高价值"},
        {"question": "什么是需求定律？", "answer": "价格上升需求下降"}
    ]

    state: AgentState = {
        "current_step": "knowledge_extracted",
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
        "knowledge_points": knowledge_points,
        "schedule_items": [],
        "review_plan_path": None,
    }

    result = sm2_schedule_node(state)

    # 验证调度项
    assert "schedule_items" in result
    assert len(result["schedule_items"]) == len(knowledge_points)

    # 验证调度项结构
    item = result["schedule_items"][0]
    assert "question" in item
    assert "ease_factor" in item
    assert "interval" in item
    assert item["ease_factor"] == 2.5  # 默认值
    assert item["interval"] >= 0


def test_generate_plan_node_creates_plan_file():
    """测试 generate_plan_node 创建计划文件

    Given: 调度项列表
    When: 调用 generate_plan_node
    Then: 应创建复习计划文件
    """
    from agent_framework.workflows.f4_review_planning import generate_plan_node
    from datetime import datetime, timedelta

    temp_dir = tempfile.mkdtemp()

    # 创建测试调度项
    tomorrow = datetime.now() + timedelta(days=1)
    schedule_items = [
        {
            "question": "测试问题1",
            "answer": "测试答案1",
            "ease_factor": 2.5,
            "interval": 1,
            "next_review_date": tomorrow.isoformat()
        }
    ]

    state: AgentState = {
        "current_step": "sm2_scheduled",
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
        "schedule_items": schedule_items,
        "review_plan_path": None,
    }

    result = generate_plan_node(state)

    # 验证计划文件创建
    assert "review_plan_path" in result
    assert result["review_plan_path"] is not None

    # 验证文件存在
    plan_file = Path(result["review_plan_path"])
    assert plan_file.exists()

    # 验证文件内容
    content = plan_file.read_text(encoding="utf-8")
    assert "复习计划" in content
    assert "测试问题1" in content

    # 清理
    shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
