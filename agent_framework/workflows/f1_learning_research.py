"""
F1 学习研究一体化 Workflow

实现从研究到掌握的完整学习流程：
- 研究阶段: 调用 AutoResearch 生成研究报告
- 确认阶段: 用户确认是否继续
- 概念提取: 从报告中提取关键概念
- 任务分解: 按概念分解学习任务
- Grilling 循环: grill-me + grill-you 交互学习
- 保存进度: 更新 Task.md 和 handoff.md
"""

from typing import Dict, Any, Callable
from langgraph.graph import StateGraph, END

from agent_framework.core.state import AgentState
from agent_framework.tools.autoresearch_tools import research_single_tool
from agent_framework.tools.skills_adapters import GrillMeAdapter, GrillYouAdapter, AdvanceTaskAdapter


# =============================================================================
# 节点定义
# =============================================================================

def research_node(state: AgentState) -> Dict[str, Any]:
    """研究节点

    调用 AutoResearch 执行研究，生成研究报告。

    Args:
        state: 当前状态，包含 topic 等信息

    Returns:
        更新后的状态字典，包含 report_path 和 current_step
    """
    try:
        # 调用 AutoResearch 执行研究
        result = research_single_tool.invoke({
            "topic": state.get("topic", "未知主题"),
            "research_type": "技术",
            "depth": "comprehensive"
        })

        return {
            "report_path": result,
            "current_step": "research_complete",
            "error_message": None
        }
    except Exception as e:
        return {
            "error_message": str(e),
            "current_step": "research_failed",
            "report_path": None
        }


def research_confirmation_node(state: AgentState) -> Dict[str, Any]:
    """研究确认节点

    暂停执行，等待用户确认研究结果。

    Args:
        state: 当前状态

    Returns:
        更新后的状态，包含 awaiting_confirmation 和 confirmation_prompt
    """
    topic = state.get("topic", "未知主题")
    report_path = state.get("report_path", "")

    return {
        "awaiting_confirmation": True,
        "confirmation_prompt": f"""研究已完成！

主题: {topic}
报告: {report_path}

是否继续基于此报告学习？
回复 '继续' 或 '重新研究'
        """,
        "next_node": "extract_concepts"
    }


def extract_concepts_node(state: AgentState) -> Dict[str, Any]:
    """概念提取节点

    解析研究报告，提取关键概念。

    Args:
        state: 当前状态，包含 report_path

    Returns:
        更新后的状态，包含 key_concepts 列表
    """
    report_path = state.get("report_path", "")
    # 调用辅助函数提取概念
    concepts = extract_concepts_from_report(report_path)

    return {
        "key_concepts": concepts,
        "current_step": "concepts_extracted"
    }


def breakdown_tasks_node(state: AgentState) -> Dict[str, Any]:
    """任务分解节点

    按概念分解学习任务，初始化 Task.md。

    Args:
        state: 当前状态，包含 key_concepts 和 session_path

    Returns:
        更新后的状态，包含 tasks 列表和 current_task_id
    """
    concepts = state.get("key_concepts", [])
    session_path = state.get("session_path", "")

    # 按概念分解任务
    tasks = []
    for i, concept in enumerate(concepts, 1):
        tasks.append({
            "id": f"task_{i}",
            "concept": concept,
            "status": "pending",
            "round": 0
        })

    # 初始化 Task.md
    initialize_task_md(session_path, tasks)

    return {
        "tasks": tasks,
        "current_task_id": tasks[0]["id"] if tasks else "",
        "current_step": "tasks_breakdown"
    }


def grill_me_node(state: AgentState) -> Dict[str, Any]:
    """grill-me 节点

    AI 考用户，生成问题检查理解。

    Args:
        state: 当前状态，包含 current_task_id

    Returns:
        更新后的状态，包含 current_questions
    """
    current_task_id = state.get("current_task_id", "")
    session_path = state.get("session_path", "")

    # 使用 GrillMeAdapter 生成问题
    adapter = GrillMeAdapter(session_path)
    questions = adapter.generate_questions(current_task_id, count=3)

    return {
        "current_questions": questions,
        "current_step": "grilling_me"
    }


def grill_you_node(state: AgentState) -> Dict[str, Any]:
    """grill-you 节点

    用户考 AI，建议用户可以问的问题。

    Args:
        state: 当前状态

    Returns:
        更新后的状态，包含 user_question_suggestions
    """
    topic = state.get("topic", "")
    session_path = state.get("session_path", "")

    # 使用 GrillYouAdapter 建议问题
    adapter = GrillYouAdapter(session_path)
    suggestions = adapter.suggest_questions(topic, count=3)

    return {
        "user_question_suggestions": suggestions,
        "current_step": "grilling_you"
    }


def evaluate_mastery_node(state: AgentState) -> Dict[str, Any]:
    """评估掌握程度节点

    基于问答结果评估用户是否掌握当前任务。

    Args:
        state: 当前状态，包含 answers

    Returns:
        更新后的状态，包含 mastery_level (completed/continuing)
    """
    # 简化实现：基于答案数量评估
    answers = state.get("answers", [])
    mastered = len(answers) >= 2

    return {
        "mastery_level": "completed" if mastered else "continuing",
        "current_step": "mastery_evaluated"
    }


def save_progress_node(state: AgentState) -> Dict[str, Any]:
    """保存进度节点

    更新 Task.md 并生成 handoff.md。

    Args:
        state: 当前状态，包含 current_task_id

    Returns:
        更新后的状态
    """
    current_task_id = state.get("current_task_id", "")
    round = state.get("round", 0)
    session_path = state.get("session_path", "")

    # 使用 AdvanceTaskAdapter 保存进度
    adapter = AdvanceTaskAdapter(session_path)
    adapter.complete_task(current_task_id, notes=f"完成 {round} 轮学习")

    return {
        "current_step": "progress_saved"
    }


# =============================================================================
# 条件函数
# =============================================================================

def should_continue_research(state: AgentState) -> str:
    """判断是否继续基于研究学习

    Args:
        state: 当前状态

    Returns:
        "continue": 继续，进入概念提取
        "rethink": 重新研究
    """
    # TODO: 实现 should_continue_research 逻辑
    return "continue"


def check_mastery(state: AgentState) -> str:
    """检查是否掌握当前任务

    Args:
        state: 当前状态，包含 mastery_level

    Returns:
        "continue": 继续学习，进入 grill-you
        "completed": 已掌握，进入保存进度
    """
    # TODO: 实现 check_mastery 逻辑
    return "completed"


# =============================================================================
# Workflow 创建
# =============================================================================

def create_f1_workflow() -> StateGraph:
    """创建 F1 学习研究一体化 Workflow

    Returns:
        StateGraph 实例，包含所有节点和边的定义
    """
    workflow = StateGraph(AgentState)

    # 添加节点
    workflow.add_node("research", research_node)
    workflow.add_node("research_confirmation", research_confirmation_node)
    workflow.add_node("extract_concepts", extract_concepts_node)
    workflow.add_node("breakdown_tasks", breakdown_tasks_node)
    workflow.add_node("grill_me", grill_me_node)
    workflow.add_node("grill_you", grill_you_node)
    workflow.add_node("evaluate_mastery", evaluate_mastery_node)
    workflow.add_node("save_progress", save_progress_node)

    # 设置入口点
    workflow.set_entry_point("research")

    # 添加边
    workflow.add_edge("research", "research_confirmation")

    # 确认后的条件边
    workflow.add_conditional_edges(
        "research_confirmation",
        should_continue_research,
        {
            "continue": "extract_concepts",
            "rethink": "research"
        }
    )

    workflow.add_edge("extract_concepts", "breakdown_tasks")
    workflow.add_edge("breakdown_tasks", "grill_me")

    # Grilling 循环
    workflow.add_edge("grill_me", "evaluate_mastery")
    workflow.add_conditional_edges(
        "evaluate_mastery",
        check_mastery,
        {
            "continue": "grill_you",
            "completed": "save_progress"
        }
    )
    workflow.add_edge("grill_you", "grill_me")

    # 退出
    workflow.add_edge("save_progress", END)

    return workflow


# =============================================================================
# 辅助函数
# =============================================================================

def extract_concepts_from_report(report_path: str) -> list:
    """从报告中提取概念

    Args:
        report_path: 报告文件路径

    Returns:
        概念列表
    """
    # TODO: 实现 extract_concepts_from_report 逻辑
    return []


def initialize_task_md(session_path: str, tasks: list) -> None:
    """初始化 Task.md

    Args:
        session_path: 会话目录路径
        tasks: 任务列表
    """
    # TODO: 实现 initialize_task_md 逻辑
    pass
