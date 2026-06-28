"""
F2 知识问答增强 Workflow

深度集成 review_agent，提供增强的知识问答功能：
- 加载知识库: CONTEXT.md + sources/ 目录
- 接收问题: 等待用户输入问题
- 知识查询: 本地 → review_agent → 网络搜索（按优先级）
- 生成回答: 综合查询结果生成结构化回答
"""

from typing import Dict, Any, Optional
from pathlib import Path
from langgraph.graph import StateGraph, END

from agent_framework.core.state import AgentState, parse_context_md
from agent_framework.tools.review_agent_tools import ReviewAgentAdapter


# =============================================================================
# 节点定义
# =============================================================================

def load_knowledge_node(state: AgentState) -> Dict[str, Any]:
    """加载知识库节点

    从会话目录加载 CONTEXT.md 和 sources/ 目录到缓存。

    Args:
        state: 当前状态，包含 session_path

    Returns:
        更新后的状态，包含 cached_terminology, cached_sources, knowledge_loaded
    """
    session_path = Path(state.get("session_path", ""))

    try:
        # 加载 CONTEXT.md
        context_path = session_path / "CONTEXT.md"
        cached_terminology = {}

        if context_path.exists():
            try:
                cached_terminology = parse_context_md(context_path)
            except Exception as e:
                # CONTEXT.md 解析失败，继续执行但记录错误
                cached_terminology = {}

        # 加载 sources/ 目录
        cached_sources = {}
        sources_dir = session_path / "sources"

        if sources_dir.exists() and sources_dir.is_dir():
            for source_file in sources_dir.glob("*.md"):
                try:
                    content = source_file.read_text(encoding="utf-8")
                    cached_sources[source_file.stem] = content
                except Exception:
                    # 跳过读取失败的文件
                    continue

        return {
            "cached_terminology": cached_terminology,
            "cached_sources": cached_sources,
            "knowledge_loaded": True,
            "current_step": "knowledge_loaded",
            "error_message": None
        }

    except Exception as e:
        return {
            "knowledge_loaded": False,
            "current_step": "knowledge_load_failed",
            "error_message": f"知识库加载失败: {str(e)}",
            "cached_terminology": {},
            "cached_sources": {}
        }


def receive_question_node(state: AgentState) -> Dict[str, Any]:
    """接收问题节点

    等待用户输入问题。这是一个确认节点，暂停执行等待用户输入。

    Args:
        state: 当前状态

    Returns:
        更新后的状态，包含 awaiting_confirmation 和 confirmation_prompt
    """
    # 获取已加载的术语数量作为提示
    term_count = len(state.get("cached_terminology", {}))
    source_count = len(state.get("cached_sources", {}))

    prompt = f"""知识库已加载完成！

📚 已加载内容:
- 术语定义: {term_count} 条
- 学习资料: {source_count} 个文件

请输入你的问题，我将基于知识库为你解答。
    """

    return {
        "awaiting_confirmation": True,
        "confirmation_prompt": prompt,
        "next_node": "query_knowledge",
        "current_step": "awaiting_question"
    }


def query_knowledge_node(state: AgentState) -> Dict[str, Any]:
    """知识查询节点

    按优先级查询知识：本地术语 → review_agent → fallback。

    Args:
        state: 当前状态，包含 user_question 和 cached_terminology

    Returns:
        更新后的状态，包含 query_result
    """
    user_question = state.get("user_question", "").strip()
    cached_terminology = state.get("cached_terminology", {})

    # 检查是否有问题
    if not user_question:
        return {
            "query_result": {
                "status": "error",
                "error": "未提供问题"
            },
            "current_step": "query_failed"
        }

    # 优先级 1: 查询本地术语库
    local_answer = query_local_terminology(user_question, cached_terminology)
    if local_answer:
        return {
            "query_result": {
                "status": "success",
                "answer": local_answer,
                "source": "local"
            },
            "current_step": "knowledge_queried"
        }

    # 优先级 2: 调用 review_agent
    try:
        agent_result = ReviewAgentAdapter.ask(user_question)
        if agent_result.get("status") == "success":
            return {
                "query_result": {
                    "status": "success",
                    "answer": agent_result.get("answer", ""),
                    "source": "review_agent"
                },
                "current_step": "knowledge_queried"
            }
    except Exception as e:
        # 继续到 fallback
        pass

    # 优先级 3: Fallback
    return {
        "query_result": {
            "status": "not_found",
            "answer": "知识库中未找到相关内容，请尝试其他问题或补充学习资料。"
        },
        "current_step": "knowledge_queried"
    }


def generate_answer_node(state: AgentState) -> Dict[str, Any]:
    """生成回答节点

    基于查询结果生成结构化回答。

    Args:
        state: 当前状态，包含 query_result

    Returns:
        更新后的状态，包含 generated_answer
    """
    query_result = state.get("query_result")

    if not query_result:
        return {
            "generated_answer": "暂无查询结果",
            "current_step": "answer_generated"
        }

    status = query_result.get("status")

    if status == "success":
        answer = query_result.get("answer", "")
        source = query_result.get("source", "unknown")

        # 添加来源标注
        source_label = {
            "local": "来自本地术语库",
            "review_agent": "来自智能问答系统",
            "web": "来自网络搜索"
        }.get(source, "未知来源")

        generated_answer = f"""{answer}

---
📖 来源: {source_label}
        """
    elif status == "not_found":
        generated_answer = query_result.get("answer", "知识库中未找到相关内容")
    else:
        # error 状态
        error_msg = query_result.get("error", "查询失败")
        generated_answer = f"抱歉，查询出现问题：{error_msg}"

    return {
        "generated_answer": generated_answer.strip(),
        "current_step": "answer_generated"
    }


# =============================================================================
# 条件函数
# =============================================================================

def has_question(state: AgentState) -> str:
    """检查是否有问题输入

    Args:
        state: 当前状态

    Returns:
        "proceed": 有问题，继续查询
        "wait": 无问题，等待输入
    """
    user_question = state.get("user_question", "").strip()
    return "proceed" if user_question else "wait"


# =============================================================================
# Workflow 创建
# =============================================================================

def create_f2_workflow() -> StateGraph:
    """创建 F2 知识问答增强 Workflow

    Returns:
        StateGraph 实例，包含所有节点和边的定义
    """
    workflow = StateGraph(AgentState)

    # 添加节点
    workflow.add_node("load_knowledge", load_knowledge_node)
    workflow.add_node("receive_question", receive_question_node)
    workflow.add_node("query_knowledge", query_knowledge_node)
    workflow.add_node("generate_answer", generate_answer_node)

    # 设置入口点
    workflow.set_entry_point("load_knowledge")

    # 添加边
    workflow.add_edge("load_knowledge", "receive_question")
    workflow.add_edge("receive_question", "query_knowledge")
    workflow.add_edge("query_knowledge", "generate_answer")
    workflow.add_edge("generate_answer", END)

    return workflow


# =============================================================================
# 辅助函数
# =============================================================================

def query_local_terminology(question: str, terminology: Dict[str, str]) -> Optional[str]:
    """从本地术语库查询答案

    Args:
        question: 用户问题
        terminology: 术语字典

    Returns:
        找到的答案，未找到返回 None
    """
    # 简单匹配：检查问题是否包含术语关键词
    for term, definition in terminology.items():
        if term in question:
            return f"**{term}**: {definition}"

    # 尝试模糊匹配（去除标点符号和空格）
    question_clean = question.replace("？", "").replace("?", "").replace("是", "").strip()
    for term, definition in terminology.items():
        if question_clean == term:
            return f"**{term}**: {definition}"

    return None
