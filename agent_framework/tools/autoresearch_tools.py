"""
AutoResearch LangChain Tools

封装 AutoResearch 模块为 LangChain Tools，提供研究功能调用接口。
"""

from typing import Dict, Any
from langchain_core.tools import tool

# 尝试导入 AutoResearch 模块
try:
    from AutoResearch.autoresearch.main import research_single, research_deep
    AUTORESEARCH_AVAILABLE = True
except ImportError:
    AUTORESEARCH_AVAILABLE = False

from agent_framework.core.exceptions import (
    ResearchTimeoutError,
    ResearchInsufficientError,
    DegradableError,
)


# ==============================================================================
# LangChain Tools
# ==============================================================================

@tool
def research_single_tool(
    topic: str,
    research_type: str = "通用",
    depth: str = "comprehensive"
) -> str:
    """单次研究模式

    执行针对指定主题的综合研究，生成结构化报告。

    Args:
        topic: 研究主题，例如 "RAG 技术调研"
        research_type: 研究类型（技术/学术/通用）
        depth: 研究深度
            - comprehensive: 综合研究，覆盖多个维度
            - deep: 深度研究，聚焦核心问题
            - survey: 快速调研，概览性质

    Returns:
        报告文件路径，例如 "output/reports/topic_20250628.md"

    Raises:
        ResearchTimeoutError: 研究超时
        ResearchInsufficientError: 研究内容不足
    """
    if not AUTORESEARCH_AVAILABLE:
        raise DegradableError("AutoResearch 模块不可用", fallback="mock_response")

    try:
        return research_single(topic, research_type, depth)
    except TimeoutError as e:
        raise ResearchTimeoutError(f"研究超时: {e}")
    except ValueError as e:
        raise ResearchInsufficientError(f"研究内容不足: {e}")


@tool
def research_deep_tool(topic: str, research_type: str = "通用") -> str:
    """深度研究模式

    执行多维度深度研究，自动生成研究计划并执行。

    Args:
        topic: 研究主题
        research_type: 研究类型（技术/学术/通用）

    Returns:
        报告文件路径
    """
    if not AUTORESEARCH_AVAILABLE:
        raise DegradableError("AutoResearch 模块不可用", fallback="mock_response")

    try:
        return research_deep(topic, research_type)
    except Exception as e:
        raise DegradableError(f"深度研究失败，降级到单次研究: {e}", fallback="single_research")


# ==============================================================================
# 适配器层
# ==============================================================================

class AutoResearchAdapter:
    """AutoResearch 适配器

    提供结构化接口的适配器层，返回结构化数据而非原始路径。
    """

    @staticmethod
    def single(topic: str, research_type: str = "通用", depth: str = "comprehensive") -> Dict[str, Any]:
        """单次研究，返回结构化结果

        Args:
            topic: 研究主题
            research_type: 研究类型
            depth: 研究深度

        Returns:
            结构化结果字典:
                - status: success/error
                - filepath: 报告文件路径
                - topic: 研究主题
                - type: 研究类型
                - error: 错误信息（如果失败）
        """
        try:
            if not AUTORESEARCH_AVAILABLE:
                return {
                    "status": "error",
                    "error": "AutoResearch 模块不可用",
                    "topic": topic,
                    "type": research_type
                }

            filepath = research_single(topic, research_type, depth)

            return {
                "status": "success",
                "filepath": filepath,
                "topic": topic,
                "type": research_type
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "topic": topic,
                "type": research_type
            }

    @staticmethod
    def deep(topic: str, research_type: str = "通用") -> Dict[str, Any]:
        """深度研究，返回结构化结果

        Args:
            topic: 研究主题
            research_type: 研究类型

        Returns:
            结构化结果字典
        """
        try:
            if not AUTORESEARCH_AVAILABLE:
                return {
                    "status": "error",
                    "error": "AutoResearch 模块不可用",
                    "topic": topic,
                    "type": research_type
                }

            filepath = research_deep(topic, research_type)

            return {
                "status": "success",
                "filepath": filepath,
                "topic": topic,
                "type": research_type,
                "mode": "deep"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "topic": topic,
                "type": research_type
            }
