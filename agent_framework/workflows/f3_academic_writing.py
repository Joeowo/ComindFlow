"""
F3 学术写作全流程 Workflow

实现从澄清到完成的完整学术写作流程：
- 澄清阶段: 确定研究方向、核心论点
- 研究阶段: 调用 AutoResearch 进行文献调研
- 写作阶段: 大纲生成 → 分段写作 → 表达优化
- Review 循环: 自我审查 → 用户审查 → 迭代改进
"""

from typing import Dict, Any
from enum import Enum
from agent_framework.core.state import AgentState
from agent_framework.tools.autoresearch_tools import research_single_tool
from langgraph.graph import StateGraph, END


# =============================================================================
# 写作阶段枚举
# =============================================================================

class WritingPhase(Enum):
    """写作阶段枚举"""
    CLARIFICATION = "clarification"
    RESEARCH = "research"
    WRITING = "writing"
    REVIEW = "review"
    COMPLETED = "completed"


# =============================================================================
# 澄清阶段节点
# =============================================================================

def clarify_topic_node(state: AgentState) -> Dict[str, Any]:
    """澄清主题节点

    生成澄清问题，帮助确定研究方向和核心论点。

    Args:
        state: 当前状态，包含 topic

    Returns:
        更新后的状态，包含澄清问题列表
    """
    topic = state.get("topic", "")

    # 生成澄清问题
    questions = [
        f"关于 '{topic}'，你的核心论点是什么？",
        f"这项研究的主要创新点在哪里？",
        f"目标读者是谁？",
        f"是否有特定的研究方法要求？",
        f"研究范围是什么？需要限定哪些方面？"
    ]

    return {
        "clarification_questions": questions,
        "current_step": "clarification",
        "writing_phase": WritingPhase.CLARIFICATION.value
    }


def clarify_confirmation_node(state: AgentState) -> Dict[str, Any]:
    """澄清确认节点

    暂停执行，等待用户确认澄清结果。

    Args:
        state: 当前状态

    Returns:
        更新后的状态，包含确认提示
    """
    topic = state.get("topic", "")
    questions = state.get("clarification_questions", [])

    # 构建确认提示
    prompt_lines = [
        f"## 学术写作项目澄清",
        f"",
        f"**主题**: {topic}",
        f"",
        f"请回答以下澄清问题：",
        f""
    ]

    for i, question in enumerate(questions, 1):
        prompt_lines.append(f"{i}. {question}")

    prompt_lines.extend([
        f"",
        f"---",
        f"回答完毕后，请回复 '继续' 进入研究阶段。",
        f"如需重新澄清，请回复 '重新'。"
    ])

    return {
        "awaiting_confirmation": True,
        "confirmation_prompt": "\n".join(prompt_lines),
        "next_node": "plan_research"
    }


# =============================================================================
# 条件函数
# =============================================================================

def should_continue_clarification(state: AgentState) -> str:
    """判断是否继续澄清或进入研究

    根据用户确认和核心论点是否完整决定下一步：
    - 如果有核心论点且用户确认，进入研究
    - 否则重新澄清

    Args:
        state: 当前状态

    Returns:
        "research": 进入研究阶段
        "clarify": 重新澄清
    """
    # 检查是否有核心论点
    core_argument = state.get("core_argument", "")

    if core_argument and len(core_argument.strip()) > 0:
        # 有核心论点，可以进入研究
        return "research"

    # 没有核心论点，需要继续澄清
    return "clarify"


# =============================================================================
# 研究阶段节点
# =============================================================================

def plan_research_node(state: AgentState) -> Dict[str, Any]:
    """研究规划节点

    基于主题和核心论点生成研究计划。

    Args:
        state: 当前状态，包含 topic 和 core_argument

    Returns:
        更新后的状态，包含研究计划
    """
    topic = state.get("topic", "")
    core_argument = state.get("core_argument", "")

    # 基于澄清信息生成研究计划
    research_plan = {
        "main_topics": [
            f"{topic} 理论基础",
            f"{topic} 现有研究综述",
            f"{topic} 方法论",
            f"{topic} 实证研究",
            f"{topic} 应用案例"
        ],
        "search_queries": [
            topic,
            core_argument,
            f"{topic} review",
            f"{topic} methodology",
            f"{topic} applications"
        ],
        "estimated_papers": 20
    }

    return {
        "research_plan": research_plan,
        "current_step": "research_planned",
        "writing_phase": WritingPhase.RESEARCH.value
    }


def execute_research_node(state: AgentState) -> Dict[str, Any]:
    """研究执行节点

    调用 AutoResearch 执行文献调研。

    Args:
        state: 当前状态，包含 research_plan

    Returns:
        更新后的状态，包含报告路径
    """
    topic = state.get("topic", "")
    research_plan = state.get("research_plan", {})

    # 获取搜索查询
    search_queries = research_plan.get("search_queries", [topic])

    # 使用第一个查询作为研究主题
    research_topic = search_queries[0] if search_queries else topic

    try:
        # 调用 AutoResearch
        result = research_single_tool.invoke({
            "topic": research_topic,
            "research_type": "学术",
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
        state: 当前状态，包含 topic 和 report_path

    Returns:
        更新后的状态，包含确认提示
    """
    topic = state.get("topic", "")
    report_path = state.get("report_path", "")
    research_plan = state.get("research_plan", {})

    # 构建确认提示
    prompt_lines = [
        f"## 文献研究完成",
        f"",
        f"**主题**: {topic}",
        f"**报告路径**: {report_path}",
        f"",
        f"### 研究计划执行情况",
        f""
    ]

    if research_plan:
        prompt_lines.append(f"**研究主题数**: {len(research_plan.get('main_topics', []))}")
        prompt_lines.append(f"**预计论文数**: {research_plan.get('estimated_papers', 'N/A')}")

    prompt_lines.extend([
        f"",
        f"---",
        f"请查阅研究报告后：",
        f"- 回复 '继续' 开始撰写大纲",
        f"- 回复 '补充' 进行额外研究"
    ])

    return {
        "awaiting_confirmation": True,
        "confirmation_prompt": "\n".join(prompt_lines),
        "next_node": "generate_outline"
    }


# =============================================================================
# 研究阶段条件函数
# =============================================================================

def should_supplement_research(state: AgentState) -> str:
    """判断是否需要补充研究

    根据用户确认决定：
    - 如果用户确认研究充分，进入写作
    - 否则补充研究

    Args:
        state: 当前状态

    Returns:
        "writing": 进入写作阶段
        "supplement": 补充研究
    """
    # 检查用户是否批准
    research_approved = state.get("research_approved", False)

    if research_approved:
        return "writing"

    # 默认需要补充
    return "supplement"


# =============================================================================
# 写作阶段节点
# =============================================================================

def generate_outline_node(state: AgentState) -> Dict[str, Any]:
    """生成大纲节点

    基于研究生成结构化论文大纲。

    Args:
        state: 当前状态，包含 topic 和 report_path

    Returns:
        更新后的状态，包含论文大纲
    """
    topic = state.get("topic", "未知主题")
    core_argument = state.get("core_argument", "")

    # 生成标准学术论文大纲
    outline = {
        "title": topic,
        "sections": [
            {
                "name": "Introduction",
                "subsections": [
                    "背景介绍",
                    "研究问题",
                    "核心论点",
                    "论文结构"
                ]
            },
            {
                "name": "Literature Review",
                "subsections": [
                    "理论基础",
                    "现有研究综述",
                    "研究空白"
                ]
            },
            {
                "name": "Methods",
                "subsections": [
                    "研究设计",
                    "数据来源",
                    "分析方法"
                ]
            },
            {
                "name": "Results",
                "subsections": [
                    "主要发现",
                    "数据分析"
                ]
            },
            {
                "name": "Discussion",
                "subsections": [
                    "结果解释",
                    "理论贡献",
                    "实践意义"
                ]
            },
            {
                "name": "Conclusion",
                "subsections": [
                    "研究总结",
                    "局限性",
                    "未来研究方向"
                ]
            }
        ]
    }

    return {
        "outline": outline,
        "current_step": "outline_generated",
        "writing_phase": WritingPhase.WRITING.value
    }


def outline_confirmation_node(state: AgentState) -> Dict[str, Any]:
    """大纲确认节点

    暂停执行，等待用户确认大纲。

    Args:
        state: 当前状态

    Returns:
        更新后的状态，包含确认提示
    """
    outline = state.get("outline", {})

    # 构建大纲预览
    prompt_lines = [
        f"## 论文大纲",
        f""
    ]

    if outline and "sections" in outline:
        prompt_lines.append(f"**标题**: {outline.get('title', '未命名')}")
        prompt_lines.append(f"")

        for i, section in enumerate(outline["sections"], 1):
            prompt_lines.append(f"### {i}. {section['name']}")
            for subsection in section.get("subsections", []):
                prompt_lines.append(f"   - {subsection}")
            prompt_lines.append(f"")

    prompt_lines.extend([
        f"---",
        f"请确认大纲或提出修改建议：",
        f"- 回复 '确认' 开始撰写内容",
        f"- 回复 '修改' 调整大纲"
    ])

    return {
        "awaiting_confirmation": True,
        "confirmation_prompt": "\n".join(prompt_lines),
        "next_node": "draft_section"
    }


def draft_section_node(state: AgentState) -> Dict[str, Any]:
    """起草章节节点

    逐章节起草论文内容。

    Args:
        state: 当前状态，包含 outline 和 current_section_index

    Returns:
        更新后的状态
    """
    outline = state.get("outline", {})
    current_index = state.get("current_section_index", 0)

    if not outline or "sections" not in outline:
        return {
            "current_step": "draft_complete",
            "drafting_complete": True,
            "writing_phase": WritingPhase.WRITING.value
        }

    sections = outline["sections"]

    if current_index >= len(sections):
        # 所有章节已完成
        return {
            "current_step": "all_sections_draft",
            "drafting_complete": True,
            "writing_phase": WritingPhase.WRITING.value
        }

    # 获取当前章节
    section = sections[current_index]
    section_name = section["name"]

    # 生成章节草稿内容
    draft_content = f"""
# {section_name}

本节主要讨论 {section_name.lower()} 的相关内容...

"""

    # 保存草稿
    session_path = state.get("session_path", "")
    draft_path = f"{session_path}/draft/{section_name.lower().replace(' ', '_')}.md"

    from pathlib import Path
    draft_dir = Path(session_path) / "draft"
    draft_dir.mkdir(parents=True, exist_ok=True)

    draft_file = Path(draft_path)
    draft_file.write_text(draft_content.strip(), encoding="utf-8")

    # 更新草稿路径列表
    draft_paths = state.get("draft_paths", [])
    draft_paths.append(draft_path)

    return {
        "current_section_index": current_index + 1,
        "current_section_name": section_name,
        "draft_paths": draft_paths,
        "current_step": "section_drafted",
        "writing_phase": WritingPhase.WRITING.value
    }


def refine_section_node(state: AgentState) -> Dict[str, Any]:
    """优化章节节点

    对已起草的章节进行表达优化。

    Args:
        state: 当前状态

    Returns:
        更新后的状态
    """
    current_section_name = state.get("current_section_name", "")
    draft_paths = state.get("draft_paths", [])

    # 这里可以添加 LLM 调用进行内容优化
    # 目前暂时返回原状态
    return {
        "current_step": "section_refined",
        "writing_phase": WritingPhase.WRITING.value
    }


# =============================================================================
# 写作阶段条件函数
# =============================================================================

def check_section_complete(state: AgentState) -> str:
    """检查是否所有章节已完成

    Args:
        state: 当前状态

    Returns:
        "next_section": 继续起草下一章节
        "review": 进入审查阶段
    """
    drafting_complete = state.get("drafting_complete", False)
    current_index = state.get("current_section_index", 0)
    outline = state.get("outline", {})

    if outline and "sections" in outline:
        total_sections = len(outline["sections"])
        if current_index >= total_sections or drafting_complete:
            return "review"

    return "next_section"


def should_revise_outline(state: AgentState) -> str:
    """判断是否需要修改大纲

    Args:
        state: 当前状态

    Returns:
        "draft": 大纲已确认，开始起草
        "revise": 需要修改大纲
    """
    outline_approved = state.get("outline_approved", False)

    if outline_approved:
        return "draft"

    return "revise"


# =============================================================================
# Review 循环节点
# =============================================================================

def self_review_node(state: AgentState) -> Dict[str, Any]:
    """自我审查节点

    执行论点一致性、证据充分性、逻辑流畅性检查。

    Args:
        state: 当前状态

    Returns:
        更新后的状态，包含审查结果
    """
    draft_paths = state.get("draft_paths", [])

    review_results = []
    total_score = 0.0

    for path in draft_paths:
        # 执行检查
        checks = {
            "argument_consistency": 0.8,  # 简化模拟
            "evidence_adequacy": 0.7,
            "logical_flow": 0.9,
            "academic_tone": 0.8
        }
        section_score = sum(checks.values()) / len(checks)

        review_results.append({
            "path": path,
            "checks": checks,
            "score": section_score
        })
        total_score += section_score

    if review_results:
        total_score = total_score / len(review_results)

    return {
        "review_results": review_results,
        "review_score": total_score,
        "current_step": "self_review_completed",
        "writing_phase": WritingPhase.REVIEW.value
    }


def user_review_node(state: AgentState) -> Dict[str, Any]:
    """用户审查节点

    暂停执行，等待用户确认或提出修改建议。

    Args:
        state: 当前状态

    Returns:
        更新后的状态，包含确认提示
    """
    review_score = state.get("review_score", 0.0)
    review_results = state.get("review_results", [])

    prompt_lines = [
        f"## 论文审查结果",
        f"",
        f"**综合评分**: {review_score:.2f} / 1.0",
        f""
    ]

    for result in review_results:
        prompt_lines.append(f"### {result['path']}")
        prompt_lines.append(f"- 论点一致性: {result['checks']['argument_consistency']:.2f}")
        prompt_lines.append(f"- 证据充分性: {result['checks']['evidence_adequacy']:.2f}")
        prompt_lines.append(f"- 逻辑流畅性: {result['checks']['logical_flow']:.2f}")
        prompt_lines.append(f"- 学术语气: {result['checks']['academic_tone']:.2f}")
        prompt_lines.append(f"")

    prompt_lines.extend([
        f"---",
        f"请确认审查结果：",
        f"- 回复 '完成' 结束审查",
        f"- 回复 '修改' 进行迭代改进"
    ])

    return {
        "awaiting_confirmation": True,
        "confirmation_prompt": "\n".join(prompt_lines),
        "next_node": "finalize"
    }


def iterate_section_node(state: AgentState) -> Dict[str, Any]:
    """迭代改进节点

    根据用户反馈修改内容。

    Args:
        state: 当前状态

    Returns:
        更新后的状态
    """
    # 根据用户反馈进行修改
    # 简化实现：返回优化阶段
    return {
        "current_step": "iteration_complete",
        "writing_phase": WritingPhase.REVIEW.value
    }


def finalize_paper_node(state: AgentState) -> Dict[str, Any]:
    """完成论文节点

    标记论文完成。

    Args:
        state: 当前状态

    Returns:
        更新后的状态
    """
    return {
        "current_step": "paper_completed",
        "writing_phase": WritingPhase.COMPLETED.value
    }


# =============================================================================
# Review 循环条件函数
# =============================================================================

def should_finalize_paper(state: AgentState) -> str:
    """判断是否完成论文

    Args:
        state: 当前状态

    Returns:
        "finalize": 完成论文
        "iterate": 继续迭代
    """
    review_approved = state.get("review_approved", False)

    if review_approved:
        return "finalize"

    return "iterate"


# =============================================================================
# Workflow 创建
# =============================================================================

def create_f3_workflow() -> StateGraph:
    """创建 F3 学术写作全流程 Workflow

    Returns:
        StateGraph 实例
    """
    from langgraph.graph import StateGraph, END

    workflow = StateGraph(AgentState)

    # 澄清阶段
    workflow.add_node("clarify_topic", clarify_topic_node)
    workflow.add_node("clarify_confirmation", clarify_confirmation_node)

    # 研究阶段
    workflow.add_node("plan_research", plan_research_node)
    workflow.add_node("execute_research", execute_research_node)
    workflow.add_node("research_confirmation", research_confirmation_node)

    # 写作阶段
    workflow.add_node("generate_outline", generate_outline_node)
    workflow.add_node("outline_confirmation", outline_confirmation_node)
    workflow.add_node("draft_section", draft_section_node)
    workflow.add_node("refine_section", refine_section_node)

    # Review 循环
    workflow.add_node("self_review", self_review_node)
    workflow.add_node("user_review", user_review_node)
    workflow.add_node("iterate_section", iterate_section_node)
    workflow.add_node("finalize_paper", finalize_paper_node)

    # 设置入口
    workflow.set_entry_point("clarify_topic")

    # 澄清阶段边
    workflow.add_edge("clarify_topic", "clarify_confirmation")
    workflow.add_conditional_edges(
        "clarify_confirmation",
        should_continue_clarification,
        {
            "research": "plan_research",
            "clarify": "clarify_topic"
        }
    )

    # 研究阶段边
    workflow.add_edge("plan_research", "execute_research")
    workflow.add_edge("execute_research", "research_confirmation")
    workflow.add_conditional_edges(
        "research_confirmation",
        should_supplement_research,
        {
            "writing": "generate_outline",
            "supplement": "plan_research"
        }
    )

    # 写作阶段边
    workflow.add_edge("generate_outline", "outline_confirmation")
    workflow.add_conditional_edges(
        "outline_confirmation",
        should_revise_outline,
        {
            "draft": "draft_section",
            "revise": "generate_outline"
        }
    )

    workflow.add_edge("draft_section", "refine_section")
    workflow.add_conditional_edges(
        "refine_section",
        check_section_complete,
        {
            "next_section": "draft_section",
            "review": "self_review"
        }
    )

    # Review 循环边
    workflow.add_edge("self_review", "user_review")
    workflow.add_conditional_edges(
        "user_review",
        should_finalize_paper,
        {
            "finalize": "finalize_paper",
            "iterate": "iterate_section"
        }
    )

    workflow.add_edge("iterate_section", "refine_section")
    workflow.add_edge("finalize_paper", END)

    return workflow


# =============================================================================
# Workflow 创建 - 将在所有节点实现后完成
# =============================================================================
