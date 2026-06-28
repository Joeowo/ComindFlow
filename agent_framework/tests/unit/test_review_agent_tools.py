"""
review_agent Tools 测试

测试 review_agent LangChain Tool 封装。
"""

import pytest
from unittest.mock import patch, MagicMock
from agent_framework.tools.review_agent_tools import (
    ask_question_tool,
    generate_question_tool,
    ReviewAgentAdapter,
    REVIEW_AGENT_AVAILABLE,
)


class TestAskQuestionTool:
    """ask_question_tool 测试"""

    def test_tool_is_valid_tool(self):
        """ask_question_tool 应该是有效的 LangChain Tool"""
        # Then: 应该有 invoke 方法
        assert hasattr(ask_question_tool, "invoke")

    def test_tool_metadata(self):
        """Tool 应该有正确的元数据"""
        # Then: 应该有 name 和 description
        assert hasattr(ask_question_tool, "name")
        assert hasattr(ask_question_tool, "description")
        assert "问题" in ask_question_tool.description or "question" in ask_question_tool.description.lower()

    @pytest.mark.skipif(not REVIEW_AGENT_AVAILABLE, reason="review_agent 模块不可用")
    @patch("review_agent.services.qa_assistant.QAAssistant.ask")
    def test_invoke_with_valid_question(self, mock_ask):
        """调用 Tool 时应正确传递问题"""
        # Given: Mock 返回值
        mock_ask.return_value = "货币政策是央行调节货币供应量和利率的工具。"

        # When: 调用 Tool
        result = ask_question_tool.invoke({"question": "什么是货币政策？"})

        # Then: 应调用底层函数
        mock_ask.assert_called_once()
        assert "货币政策" in result

    @pytest.mark.skipif(not REVIEW_AGENT_AVAILABLE, reason="review_agent 模块不可用")
    @patch("review_agent.services.qa_assistant.QAAssistant.ask")
    def test_returns_no_result_when_not_found(self, mock_ask):
        """未找到内容时应返回适当消息"""
        # Given: Mock 返回未找到消息
        mock_ask.return_value = "抱歉，在知识点库中没有找到相关内容。"

        # When: 调用 Tool
        result = ask_question_tool.invoke({"question": "未知主题"})

        # Then: 应返回未找到消息
        assert "没有找到" in result


class TestGenerateQuestionTool:
    """generate_question_tool 测试"""

    def test_tool_is_valid_tool(self):
        """generate_question_tool 应该是有效的 LangChain Tool"""
        # Then: 应该有 invoke 方法
        assert hasattr(generate_question_tool, "invoke")

    def test_tool_metadata(self):
        """Tool 应该有正确的元数据"""
        # Then: 应该有 name 和 description
        assert hasattr(generate_question_tool, "name")
        assert hasattr(generate_question_tool, "description")
        assert "生成" in generate_question_tool.description or "generate" in generate_question_tool.description.lower()

    @pytest.mark.skipif(not REVIEW_AGENT_AVAILABLE, reason="review_agent 模块不可用")
    @patch("review_agent.core.question_generator.QuestionGenerator.generate_from_knowledge")
    def test_generates_question_from_knowledge(self, mock_generate):
        """应从知识点生成问题"""
        # Given: Mock 返回问题对象
        mock_question = MagicMock()
        mock_question.content = "什么是货币政策？"
        mock_question.correct_answer = "央行调节货币供应量的工具。"
        mock_generate.return_value = [mock_question]

        # When: 调用 Tool
        result = generate_question_tool.invoke({
            "knowledge": {
                "title": "货币政策",
                "content": "货币政策是指央行调节货币供应量和利率的工具。",
                "type": "概念"
            }
        })

        # Then: 应返回生成的问题
        mock_generate.assert_called_once()
        assert "货币政策" in result

    @pytest.mark.skipif(not REVIEW_AGENT_AVAILABLE, reason="review_agent 模块不可用")
    @patch("review_agent.core.question_generator.QuestionGenerator.generate_from_knowledge")
    def test_handles_empty_generation(self, mock_generate):
        """应处理空生成结果"""
        # Given: Mock 返回空列表
        mock_generate.return_value = []

        # When: 调用 Tool
        result = generate_question_tool.invoke({
            "knowledge": {"title": "无效", "content": "太短"}
        })

        # Then: 应返回空结果或错误消息
        assert result is not None


class TestReviewAgentAdapter:
    """ReviewAgent 适配器测试"""

    def test_adapter_exists(self):
        """ReviewAgentAdapter 类应该存在"""
        # Then: 应该能导入
        assert ReviewAgentAdapter is not None

    def test_adapter_ask_returns_error_when_unavailable(self):
        """review_agent 不可用时适配器应返回错误"""
        # When: 调用适配器
        result = ReviewAgentAdapter.ask("测试问题")

        # Then: 应返回错误状态（如果模块不可用）
        if not REVIEW_AGENT_AVAILABLE:
            assert isinstance(result, dict)
            assert result["status"] == "error"
            assert "不可用" in result.get("error", "")

    @pytest.mark.skipif(not REVIEW_AGENT_AVAILABLE, reason="review_agent 模块不可用")
    @patch("review_agent.services.qa_assistant.QAAssistant.ask")
    def test_adapter_ask_returns_structured_result(self, mock_ask):
        """适配器的 ask 方法应返回结构化结果"""
        # Given: Mock 返回值
        mock_ask.return_value = "这是答案。"

        # When: 调用适配器
        result = ReviewAgentAdapter.ask("测试问题？")

        # Then: 应返回结构化字典
        assert isinstance(result, dict)
        assert result["status"] == "success"
        assert result["answer"] == "这是答案。"

    def test_adapter_generate_handles_unavailable(self):
        """适配器应正确处理模块不可用的情况"""
        # When: 调用适配器
        result = ReviewAgentAdapter.generate_question({"title": "测试"})

        # Then: 应返回错误状态（如果模块不可用）
        if not REVIEW_AGENT_AVAILABLE:
            assert isinstance(result, dict)
            assert result["status"] == "error"
