"""
AutoResearch Tools 测试

测试 AutoResearch LangChain Tool 封装。
"""

import pytest
from unittest.mock import patch, MagicMock
from langchain_core.tools import Tool
from agent_framework.tools.autoresearch_tools import (
    research_single_tool,
    research_deep_tool,
    AutoResearchAdapter,
    AUTORESEARCH_AVAILABLE,
)


class TestResearchSingleTool:
    """research_single_tool 测试"""

    def test_tool_is_valid_tool(self):
        """research_single_tool 应该是有效的 LangChain Tool"""
        # Then: 应该是 Tool 类型或具有 invoke 方法
        assert hasattr(research_single_tool, "invoke")

    def test_tool_metadata(self):
        """Tool 应该有正确的元数据"""
        # Then: 应该有 name 和 description
        assert hasattr(research_single_tool, "name")
        assert hasattr(research_single_tool, "description")
        assert "研究" in research_single_tool.description or "research" in research_single_tool.description.lower()

    @pytest.mark.skipif(not AUTORESEARCH_AVAILABLE, reason="AutoResearch 模块不可用")
    @patch("agent_framework.tools.autoresearch_tools.research_single")
    def test_invoke_with_valid_params(self, mock_research):
        """调用 Tool 时应正确传递参数"""
        # Given: Mock 返回值
        mock_research.return_value = "output/reports/test_20250628.md"

        # When: 调用 Tool
        result = research_single_tool.invoke({
            "topic": "RAG 技术调研",
            "research_type": "技术",
            "depth": "comprehensive"
        })

        # Then: 应调用底层函数并返回结果
        mock_research.assert_called_once_with("RAG 技术调研", "技术", "comprehensive")
        assert result == "output/reports/test_20250628.md"

    @pytest.mark.skipif(not AUTORESEARCH_AVAILABLE, reason="AutoResearch 模块不可用")
    @patch("agent_framework.tools.autoresearch_tools.research_single")
    def test_invoke_with_default_params(self, mock_research):
        """调用 Tool 时应使用默认参数"""
        # Given: Mock 返回值
        mock_research.return_value = "output/reports/default.md"

        # When: 仅传入必需参数
        result = research_single_tool.invoke({"topic": "测试主题"})

        # Then: 应使用默认参数
        mock_research.assert_called_once_with("测试主题", "通用", "comprehensive")
        assert "output/reports/default.md" in result

    @pytest.mark.skipif(not AUTORESEARCH_AVAILABLE, reason="AutoResearch 模块不可用")
    @patch("agent_framework.tools.autoresearch_tools.research_single")
    def test_handles_timeout_error(self, mock_research):
        """应正确处理超时错误"""
        # Given: 模拟超时
        from agent_framework.core.exceptions import ResearchTimeoutError
        mock_research.side_effect = TimeoutError("API 超时")

        # When/Then: 应转换为 ResearchTimeoutError
        with pytest.raises(ResearchTimeoutError):
            research_single_tool.invoke({"topic": "测试"})

    @pytest.mark.skipif(not AUTORESEARCH_AVAILABLE, reason="AutoResearch 模块不可用")
    @patch("agent_framework.tools.autoresearch_tools.research_single")
    def test_handles_insufficient_error(self, mock_research):
        """应正确处理研究内容不足错误"""
        # Given: 模拟内容不足
        from agent_framework.core.exceptions import ResearchInsufficientError
        mock_research.side_effect = ValueError("研究内容不足")

        # When/Then: 应转换为 ResearchInsufficientError
        with pytest.raises(ResearchInsufficientError):
            research_single_tool.invoke({"topic": "测试"})


class TestResearchDeepTool:
    """research_deep_tool 测试"""

    def test_tool_is_valid_tool(self):
        """research_deep_tool 应该是有效的 LangChain Tool"""
        # Then: 应该有 invoke 方法
        assert hasattr(research_deep_tool, "invoke")

    def test_tool_metadata(self):
        """Tool 应该有正确的元数据"""
        # Then: 应该有 name 和 description
        assert hasattr(research_deep_tool, "name")
        assert hasattr(research_deep_tool, "description")
        assert "深度" in research_deep_tool.description or "deep" in research_deep_tool.description.lower()

    @pytest.mark.skipif(not AUTORESEARCH_AVAILABLE, reason="AutoResearch 模块不可用")
    @patch("agent_framework.tools.autoresearch_tools.research_deep")
    def test_invoke_with_valid_params(self, mock_research):
        """调用 Tool 时应正确传递参数"""
        # Given: Mock 返回值
        mock_research.return_value = "output/reports/deep_test.md"

        # When: 调用 Tool
        result = research_deep_tool.invoke({
            "topic": "大模型微调",
            "research_type": "技术"
        })

        # Then: 应调用底层函数
        mock_research.assert_called_once_with("大模型微调", "技术")
        assert "deep_test.md" in result

    @pytest.mark.skipif(not AUTORESEARCH_AVAILABLE, reason="AutoResearch 模块不可用")
    @patch("agent_framework.tools.autoresearch_tools.research_deep")
    def test_invoke_with_default_params(self, mock_research):
        """调用 Tool 时应使用默认参数"""
        # Given: Mock 返回值
        mock_research.return_value = "output/reports/deep_default.md"

        # When: 仅传入必需参数
        result = research_deep_tool.invoke({"topic": "测试"})

        # Then: 应使用默认参数
        mock_research.assert_called_once_with("测试", "通用")

    @pytest.mark.skipif(not AUTORESEARCH_AVAILABLE, reason="AutoResearch 模块不可用")
    @patch("agent_framework.tools.autoresearch_tools.research_deep")
    def test_handles_general_error_with_degradation(self, mock_research):
        """应将一般错误转换为可降级错误"""
        # Given: 模拟一般错误
        from agent_framework.core.exceptions import DegradableError
        mock_research.side_effect = Exception("网络错误")

        # When/Then: 应转换为 DegradableError
        with pytest.raises(DegradableError) as exc_info:
            research_deep_tool.invoke({"topic": "测试"})
        assert "降级到单次研究" in str(exc_info.value)


class TestAutoResearchAdapter:
    """AutoResearch 适配器测试"""

    def test_adapter_exists(self):
        """AutoResearchAdapter 类应该存在"""
        # Then: 应该能导入
        assert AutoResearchAdapter is not None

    def test_adapter_single_returns_error_when_unavailable(self):
        """AutoResearch 不可用时适配器应返回错误"""
        # Given: AutoResearch 不可用
        # When: 调用适配器
        result = AutoResearchAdapter.single("测试", "通用", "comprehensive")

        # Then: 应返回错误状态（如果模块不可用）
        if not AUTORESEARCH_AVAILABLE:
            assert result["status"] == "error"
            assert "不可用" in result["error"]

    @pytest.mark.skipif(not AUTORESEARCH_AVAILABLE, reason="AutoResearch 模块不可用")
    @patch("agent_framework.tools.autoresearch_tools.research_single")
    def test_adapter_single_returns_structured_result(self, mock_research):
        """适配器的 single 方法应返回结构化结果"""
        # Given: Mock 返回值
        mock_research.return_value = "output/reports/structured.md"

        # When: 调用适配器
        result = AutoResearchAdapter.single("RAG 技术", "技术", "comprehensive")

        # Then: 应返回结构化字典
        assert isinstance(result, dict)
        assert result["status"] == "success"
        assert result["filepath"] == "output/reports/structured.md"
        assert result["topic"] == "RAG 技术"
        assert result["type"] == "技术"

    @pytest.mark.skipif(not AUTORESEARCH_AVAILABLE, reason="AutoResearch 模块不可用")
    @patch("agent_framework.tools.autoresearch_tools.research_single")
    def test_adapter_single_handles_error(self, mock_research):
        """适配器应正确处理错误"""
        # Given: 模拟错误
        mock_research.side_effect = Exception("测试错误")

        # When: 调用适配器
        result = AutoResearchAdapter.single("测试", "通用", "comprehensive")

        # Then: 应返回错误状态
        assert isinstance(result, dict)
        assert result["status"] == "error"
        assert "测试错误" in result.get("error", "")
