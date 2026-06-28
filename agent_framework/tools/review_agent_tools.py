"""
review_agent LangChain Tools

封装 review_agent 模块为 LangChain Tools，提供问答和问题生成功能。
"""

from typing import Dict, Any, List, Union
from langchain_core.tools import tool

# 尝试导入 review_agent 模块
try:
    from review_agent.services.qa_assistant import QAAssistant
    from review_agent.core.question_generator import QuestionGenerator
    REVIEW_AGENT_AVAILABLE = True
except ImportError:
    REVIEW_AGENT_AVAILABLE = False

from agent_framework.core.exceptions import DegradableError


# ==============================================================================
# LangChain Tools
# ==============================================================================

@tool
def ask_question_tool(question: str) -> str:
    """回答学习问题

    基于知识点库回答用户提出的问题。

    Args:
        question: 用户的问题，例如 "什么是货币政策？"

    Returns:
        答案文本。如果知识点库中没有相关内容，返回提示消息。

    Raises:
        DegradableError: 当 review_agent 模块不可用时
    """
    if not REVIEW_AGENT_AVAILABLE:
        raise DegradableError("review_agent 模块不可用", fallback="mock_response")

    try:
        assistant = QAAssistant()
        return assistant.ask(question)
    except Exception as e:
        raise DegradableError(f"问答失败: {e}", fallback="return_error_message")


@tool
def generate_question_tool(knowledge: Dict[str, Any]) -> str:
    """从知识点生成学习问题

    基于给定的知识点内容生成相应的学习问题。

    Args:
        knowledge: 知识点字典，包含:
            - title: 知识点标题
            - content: 知识点内容
            - type: 知识点类型 (概念/分类/关系/流程)
            - id: 知识点 ID (可选)
            - session_id: 会话 ID (可选)

    Returns:
        生成的问题文本，如果没有生成则返回空字符串。
    """
    if not REVIEW_AGENT_AVAILABLE:
        raise DegradableError("review_agent 模块不可用", fallback="mock_response")

    try:
        generator = QuestionGenerator()
        questions = generator.generate_from_knowledge(knowledge)

        if questions and len(questions) > 0:
            # 返回第一个问题
            q = questions[0]
            result = f"问题: {q.content}\n答案: {q.correct_answer}"
            return result
        return "无法从该知识点生成问题（内容可能不足或类型不支持）"
    except Exception as e:
        raise DegradableError(f"问题生成失败: {e}", fallback="return_error_message")


# ==============================================================================
# 适配器层
# ==============================================================================

class ReviewAgentAdapter:
    """review_agent 适配器

    提供结构化接口的适配器层，返回结构化数据。
    """

    @staticmethod
    def ask(question: str) -> Dict[str, Any]:
        """回答问题，返回结构化结果

        Args:
            question: 用户问题

        Returns:
            结构化结果字典:
                - status: success/error
                - answer: 答案文本
                - question: 原问题
                - error: 错误信息（如果失败）
        """
        try:
            if not REVIEW_AGENT_AVAILABLE:
                return {
                    "status": "error",
                    "error": "review_agent 模块不可用",
                    "question": question
                }

            assistant = QAAssistant()
            answer = assistant.ask(question)

            return {
                "status": "success",
                "answer": answer,
                "question": question
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "question": question
            }

    @staticmethod
    def generate_question(knowledge: Dict[str, Any]) -> Dict[str, Any]:
        """从知识点生成问题，返回结构化结果

        Args:
            knowledge: 知识点字典

        Returns:
            结构化结果字典:
                - status: success/error
                - question: 生成的问题
                - answer: 答案
                - error: 错误信息（如果失败）
        """
        try:
            if not REVIEW_AGENT_AVAILABLE:
                return {
                    "status": "error",
                    "error": "review_agent 模块不可用",
                    "knowledge": knowledge
                }

            generator = QuestionGenerator()
            questions = generator.generate_from_knowledge(knowledge)

            if questions and len(questions) > 0:
                q = questions[0]
                return {
                    "status": "success",
                    "question": q.content,
                    "answer": q.correct_answer,
                    "explanation": q.explanation
                }
            else:
                return {
                    "status": "error",
                    "error": "无法生成问题（内容不足或类型不支持）",
                    "knowledge": knowledge
                }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "knowledge": knowledge
            }

    @staticmethod
    def generate_batch(knowledge_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """批量生成问题

        Args:
            knowledge_list: 知识点列表

        Returns:
            结构化结果字典
        """
        try:
            if not REVIEW_AGENT_AVAILABLE:
                return {
                    "status": "error",
                    "error": "review_agent 模块不可用",
                    "count": 0
                }

            generator = QuestionGenerator()
            questions = generator.generate_batch(knowledge_list)

            return {
                "status": "success",
                "count": len(questions),
                "questions": [
                    {
                        "question": q.content,
                        "answer": q.correct_answer,
                        "difficulty": q.difficulty
                    }
                    for q in questions
                ]
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "count": 0
            }
