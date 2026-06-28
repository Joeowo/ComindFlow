"""
S2 工具适配层集成测试

测试各组件之间的集成和端到端流程。
"""

import pytest
from pathlib import Path
from agent_framework.tools import (
    SkillsAdapter,
    GrillMeAdapter,
    GrillYouAdapter,
    AdvanceTaskAdapter,
    AutoResearchAdapter,
    ReviewAgentAdapter,
    research_single_tool,
    research_deep_tool,
    ask_question_tool,
    generate_question_tool,
)
from agent_framework.tools.autoresearch_tools import AUTORESEARCH_AVAILABLE
from agent_framework.tools.review_agent_tools import REVIEW_AGENT_AVAILABLE


class TestSkillsAdapterIntegration:
    """Skills 适配器集成测试"""

    def test_full_session_workflow(self, tmp_path):
        """测试完整的会话工作流"""
        # Given: 一个新的会话目录
        session_path = str(tmp_path / "test_session")

        # When: 创建适配器并执行完整工作流
        adapter = SkillsAdapter(session_path)

        # Step 1: 更新 CONTEXT.md
        adapter.update_context("货币政策", "央行调节货币供应量的工具")
        context = adapter.load_context()
        assert "货币政策" in context

        # Step 2: 更新任务进度
        adapter.update_task_progress("Task 1", "in_progress")
        tasks = adapter.load_task_progress()
        assert "Task 1" in tasks
        assert "in_progress" in tasks

        # Step 3: 保存 handoff
        handoff_data = {
            "current_task": "Task 1",
            "next_task": "Task 2",
            "notes": "进度良好"
        }
        adapter.save_handoff(handoff_data)
        handoff = adapter.load_handoff()
        assert "Task 1" in handoff

        # Then: 所有文件应正确创建
        assert (tmp_path / "test_session" / "CONTEXT.md").exists()
        assert (tmp_path / "test_session" / "Task.md").exists()
        assert (tmp_path / "test_session" / "handoff.md").exists()

    def test_grill_me_adapter_integration(self, tmp_path):
        """测试 GrillMeAdapter 完整流程"""
        # Given: 包含上下文的会话
        adapter = GrillMeAdapter(str(tmp_path))
        adapter.update_context("术语", "定义")

        # When: 生成问题并评估答案
        adapter.generate_questions("task_1", count=3)
        adapter.evaluate_answers({"q1": "回答内容"})

        # Then: 上下文应被更新
        context = adapter.load_context()
        assert "last_grill_results" in context

    def test_advance_task_adapter_integration(self, tmp_path):
        """测试 AdvanceTaskAdapter 完整流程"""
        # Given: 会话目录
        adapter = AdvanceTaskAdapter(str(tmp_path))

        # When: 完成任务
        adapter.complete_task("Task 1", "理解良好")

        # Then: Task.md 和 handoff.md 应正确更新
        tasks = adapter.load_task_progress()
        handoff = adapter.load_handoff()
        assert "completed" in tasks
        assert "Task 1" in handoff


class TestAutoResearchIntegration:
    """AutoResearch 集成测试"""

    def test_adapter_exists_and_has_methods(self):
        """AutoResearchAdapter 应存在并有正确的方法"""
        # Then: 应有 single 和 deep 方法
        assert hasattr(AutoResearchAdapter, "single")
        assert hasattr(AutoResearchAdapter, "deep")

    def test_tool_interfaces(self):
        """AutoResearch Tools 应有正确的接口"""
        # Then: Tools 应有 invoke 方法
        assert hasattr(research_single_tool, "invoke")
        assert hasattr(research_deep_tool, "invoke")
        assert research_single_tool.name is not None
        assert research_deep_tool.name is not None

    @pytest.mark.skipif(not AUTORESEARCH_AVAILABLE, reason="AutoResearch 模块不可用")
    def test_adapter_returns_structure(self):
        """适配器应返回结构化数据"""
        # This test would only run when AutoResearch is available
        # For now, we test the structure exists
        result = AutoResearchAdapter.single("测试", "通用", "comprehensive")
        assert isinstance(result, dict)
        assert "status" in result


class TestReviewAgentIntegration:
    """review_agent 集成测试"""

    def test_adapter_exists_and_has_methods(self):
        """ReviewAgentAdapter 应存在并有正确的方法"""
        # Then: 应有 ask, generate_question, generate_batch 方法
        assert hasattr(ReviewAgentAdapter, "ask")
        assert hasattr(ReviewAgentAdapter, "generate_question")
        assert hasattr(ReviewAgentAdapter, "generate_batch")

    def test_tool_interfaces(self):
        """review_agent Tools 应有正确的接口"""
        # Then: Tools 应有 invoke 方法
        assert hasattr(ask_question_tool, "invoke")
        assert hasattr(generate_question_tool, "invoke")
        assert ask_question_tool.name is not None
        assert generate_question_tool.name is not None

    @pytest.mark.skipif(not REVIEW_AGENT_AVAILABLE, reason="review_agent 模块不可用")
    def test_adapter_returns_structure(self):
        """适配器应返回结构化数据"""
        # This test would only run when review_agent is available
        result = ReviewAgentAdapter.ask("测试问题")
        assert isinstance(result, dict)
        assert "status" in result


class TestCrossModuleIntegration:
    """跨模块集成测试"""

    def test_all_tools_have_consistent_interface(self):
        """所有 Tools 应有一致的接口"""
        # Given: 所有 Tool
        tools = [
            research_single_tool,
            research_deep_tool,
            ask_question_tool,
            generate_question_tool,
        ]

        # Then: 所有 Tool 应有 invoke 方法和元数据
        for tool in tools:
            assert hasattr(tool, "invoke"), f"{tool} missing invoke method"
            assert hasattr(tool, "name"), f"{tool} missing name attribute"
            assert hasattr(tool, "description"), f"{tool} missing description attribute"

    def test_all_adapters_have_consistent_interface(self):
        """所有适配器应有一致的接口"""
        # Given: 所有适配器
        adapters = [
            AutoResearchAdapter,
            ReviewAgentAdapter,
        ]

        # Then: 所有适配器应有静态方法返回 dict
        for adapter in adapters:
            # 检查主要方法存在
            assert len([m for m in dir(adapter) if not m.startswith("_")]) > 0

    def test_tools_module_exports(self):
        """tools 模块应正确导出所有组件"""
        # When: 从 tools 导入
        from agent_framework.tools import (
            # Skills Adapters
            SkillsAdapter,
            GrillMeAdapter,
            GrillYouAdapter,
            AdvanceTaskAdapter,
            # AutoResearch
            research_single_tool,
            research_deep_tool,
            AutoResearchAdapter,
            # review_agent
            ask_question_tool,
            generate_question_tool,
            ReviewAgentAdapter,
        )

        # Then: 所有导入应成功
        assert SkillsAdapter is not None
        assert GrillMeAdapter is not None
        assert GrillYouAdapter is not None
        assert AdvanceTaskAdapter is not None
        assert research_single_tool is not None
        assert research_deep_tool is not None
        assert AutoResearchAdapter is not None
        assert ask_question_tool is not None
        assert generate_question_tool is not None
        assert ReviewAgentAdapter is not None
