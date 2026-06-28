"""
F1 学习研究一体化 Workflow 测试

测试 F1 Workflow 的创建、编译和基本执行流程。

测试策略：
- 单元测试：使用 mock 验证节点行为
- 集成测试：真实调用 AutoResearch
"""

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

# 导入目标模块
from agent_framework.workflows.f1_learning_research import create_f1_workflow


class TestF1WorkflowCreation:
    """F1 Workflow 创建测试 - Tracer Bullet"""

    def test_f1_workflow_can_be_created(self):
        """F1 workflow 应该可以被创建和编译

        这是 tracer bullet 测试，验证整个流程可以端到端运行。
        """
        # When: 创建 workflow
        workflow = create_f1_workflow()

        # Then: workflow 应该被创建
        assert workflow is not None
        assert hasattr(workflow, "compile")

    def test_f1_workflow_has_entry_point(self):
        """F1 workflow 应该有正确的入口点"""
        # Given: workflow 被创建
        # workflow = create_f1_workflow()

        # When: 编译它
        # app = workflow.compile()

        # Then: 应该可以获取入口点信息
        # assert app is not None
        pytest.skip("等待实现")

    def test_f1_workflow_has_all_nodes(self):
        """F1 workflow 应该包含所有必需的节点"""
        # 预期的节点列表
        expected_nodes = [
            "research",
            "research_confirmation",
            "extract_concepts",
            "breakdown_tasks",
            "grill_me",
            "grill_you",
            "evaluate_mastery",
            "save_progress",
        ]

        # Given: workflow 被创建
        # workflow = create_f1_workflow()

        # When: 获取所有节点
        # nodes = workflow.nodes

        # Then: 应该包含所有预期节点
        # for node in expected_nodes:
        #     assert node in nodes
        pytest.skip("等待实现")


class TestResearchNode:
    """研究节点测试"""

    def test_research_node_updates_state_on_success(self):
        """研究节点成功时应该正确更新状态"""
        from agent_framework.workflows.f1_learning_research import research_node

        # Given: 初始状态和 mock 的 tool
        state = {
            "topic": "RAG 技术调研",
            "current_step": "start",
            "error_message": None,
        }

        with patch("agent_framework.workflows.f1_learning_research.research_single_tool") as mock_tool:
            mock_tool.invoke.return_value = "output/reports/rag_20250628.md"

            # When: 执行研究节点
            result = research_node(state)

            # Then: 状态应该被正确更新
            assert result["current_step"] == "research_complete"
            assert result["report_path"] == "output/reports/rag_20250628.md"
            assert result["error_message"] is None

    def test_research_node_handles_error(self):
        """研究节点应该正确处理错误"""
        # Given: 状态和模拟错误
        # state = {"topic": "测试主题", "current_step": "start"}

        # with patch("agent_framework.tools.autoresearch_tools.research_single_tool") as mock_tool:
        #     mock_tool.invoke.side_effect = Exception("网络错误")

        #     # When: 执行研究节点
        #     result = research_node(state)

        #     # Then: 错误应该被捕获
        #     assert result["current_step"] == "research_failed"
        #     assert result["error_message"] is not None

        pytest.skip("等待实现 research_node")


class TestResearchConfirmationNode:
    """研究确认节点测试"""

    def test_confirmation_node_sets_awaiting_flag(self):
        """确认节点应该设置等待确认标志"""
        from agent_framework.workflows.f1_learning_research import research_confirmation_node

        # Given: 研究完成的状态
        state = {
            "topic": "测试主题",
            "report_path": "output/reports/test.md",
        }

        # When: 执行确认节点
        result = research_confirmation_node(state)

        # Then: 应该设置等待确认
        assert result["awaiting_confirmation"] is True
        assert "是否继续" in result["confirmation_prompt"]
        assert result["next_node"] == "extract_concepts"


class TestExtractConceptsNode:
    """概念提取节点测试"""

    def test_extract_concepts_parses_report(self):
        """概念提取节点应该解析报告文件"""
        from agent_framework.workflows.f1_learning_research import extract_concepts_node

        # Given: 有报告路径的状态
        state = {"report_path": "output/reports/test.md"}

        with patch("agent_framework.workflows.f1_learning_research.extract_concepts_from_report") as mock_extract:
            mock_extract.return_value = ["概念1", "概念2", "概念3"]

            # When: 执行概念提取
            result = extract_concepts_node(state)

            # Then: 概念应该被提取
            assert result["key_concepts"] == ["概念1", "概念2", "概念3"]
            assert result["current_step"] == "concepts_extracted"


class TestBreakdownTasksNode:
    """任务分解节点测试"""

    def test_breakdown_tasks_creates_task_list(self):
        """任务分解节点应该创建任务列表"""
        from agent_framework.workflows.f1_learning_research import breakdown_tasks_node

        # Given: 有概念列表的状态
        state = {
            "key_concepts": ["概念1", "概念2"],
            "session_path": "/tmp/test_session"
        }

        with patch("agent_framework.workflows.f1_learning_research.initialize_task_md") as mock_init:
            # When: 执行任务分解
            result = breakdown_tasks_node(state)

            # Then: 任务应该被创建
            assert len(result["tasks"]) == 2
            assert result["current_task_id"] == "task_1"
            assert result["current_step"] == "tasks_breakdown"
            mock_init.assert_called_once()


class TestGrillingLoop:
    """Grilling 循环测试"""

    def test_grill_me_node_generates_questions(self):
        """grill-me 节点应该生成问题"""
        from agent_framework.workflows.f1_learning_research import grill_me_node

        # Given: 有当前任务的状态
        state = {
            "current_task_id": "task_1",
            "session_path": "/tmp/test_session"
        }

        with patch("agent_framework.workflows.f1_learning_research.GrillMeAdapter") as mock_adapter_class:
            mock_adapter = mock_adapter_class.return_value
            mock_adapter.generate_questions.return_value = ["问题1", "问题2"]

            # When: 执行 grill-me
            result = grill_me_node(state)

            # Then: 问题应该被生成
            assert len(result["current_questions"]) == 2
            assert result["current_step"] == "grilling_me"

    def test_evaluate_mastery_checks_completion(self):
        """评估节点应该检查掌握程度"""
        from agent_framework.workflows.f1_learning_research import evaluate_mastery_node

        # Given: 有答案的状态
        state = {"answers": ["答案1", "答案2", "答案3"]}

        # When: 评估掌握程度
        result = evaluate_mastery_node(state)

        # Then: 应该设置掌握级别
        assert result["mastery_level"] in ["completed", "continuing"]
        assert result["current_step"] == "mastery_evaluated"

    def test_grilling_loop_exits_when_mastered(self):
        """Grilling 循环应该在掌握时退出"""
        from agent_framework.workflows.f1_learning_research import check_mastery

        # Given: 掌握的状态
        state = {"mastery_level": "completed"}

        # When: 检查是否应该继续
        should_continue = check_mastery(state)

        # Then: 应该退出到保存进度
        assert should_continue == "completed"


class TestSaveProgressNode:
    """保存进度节点测试"""

    def test_save_progress_updates_task_md(self):
        """保存进度节点应该更新 Task.md"""
        from agent_framework.workflows.f1_learning_research import save_progress_node

        # Given: 要完成的任务
        state = {
            "current_task_id": "task_1",
            "round": 2,
            "session_path": "/tmp/test_session"
        }

        with patch("agent_framework.workflows.f1_learning_research.AdvanceTaskAdapter") as mock_adapter_class:
            mock_adapter = mock_adapter_class.return_value

            # When: 保存进度
            result = save_progress_node(state)

            # Then: 任务应该被标记完成
            mock_adapter.complete_task.assert_called_once_with("task_1", notes="完成 2 轮学习")
            assert result["current_step"] == "progress_saved"
