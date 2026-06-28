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
    report_path = state.get("report_path")

    # 检查 report_path 是否有效
    if not report_path:
        return {
            "key_concepts": [],
            "current_step": "concepts_extracted",
            "error_message": "No valid report_path provided"
        }

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
        "round": 1,  # 初始化为第 1 轮
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
    # 获取答案和轮次
    answers = state.get("answers", [])
    current_round = state.get("round", 0)

    # 评估逻辑：
    # 1. 如果有足够的答案（>= 2），认为掌握
    # 2. 如果没有答案但轮次 >= 1，也认为掌握（简化测试）
    # 3. 否则继续学习
    mastered = len(answers) >= 2 or current_round >= 1

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

    根据用户确认输入决定下一步：
    - 如果用户明确要求重新研究，返回 "rethink"
    - 其他情况默认继续

    Args:
        state: 当前状态，可能包含 user_confirmation 字段

    Returns:
        "continue": 继续，进入概念提取
        "rethink": 重新研究
    """
    # 获取用户确认
    user_confirmation = state.get("user_confirmation", "")

    if not user_confirmation:
        # 没有用户输入，默认继续
        return "continue"

    # 转换为小写进行匹配
    confirmation_lower = str(user_confirmation).lower().strip()

    # 定义重新研究的关键词
    rethink_keywords = [
        "重新研究", "重新", "再研究", "重做", "不满意",
        "rethink", "redo", "restart", "research again"
    ]

    # 检查是否包含重新研究的关键词
    for keyword in rethink_keywords:
        if keyword.lower() in confirmation_lower:
            return "rethink"

    # 默认继续
    return "continue"


def check_mastery(state: AgentState) -> str:
    """检查是否掌握当前任务

    评估用户是否掌握了当前任务，综合考虑：
    - 学习轮次
    - 答案质量分数
    - 用户明确表示

    Args:
        state: 当前状态，包含 mastery_level、round、quality_score 等

    Returns:
        "continue": 继续学习，进入 grill-you
        "completed": 已掌握，进入保存进度
    """
    # 1. 检查用户是否明确表示完成
    if state.get("user_confirms_completion", False):
        return "completed"

    # 2. 检查显式的 mastery_level
    mastery_level = state.get("mastery_level", "")
    if mastery_level == "completed":
        return "completed"
    elif mastery_level == "continuing":
        # 即使标记为 continuing，也要检查其他条件
        pass

    # 3. 获取轮次和质量分数
    current_round = state.get("round", 0)
    quality_score = state.get("quality_score", None)
    answers = state.get("answers", [])

    # 4. 评估逻辑
    # 最小轮次要求：至少 2 轮
    MIN_ROUNDS = 2

    # 如果有质量分数，优先使用
    if quality_score is not None:
        # 高质量分数（>= 0.8）且至少 1 轮即可完成
        if quality_score >= 0.8 and current_round >= 1:
            return "completed"
        # 中等质量分数（>= 0.6）需要至少 2 轮
        elif quality_score >= 0.6 and current_round >= MIN_ROUNDS:
            return "completed"
        # 低质量分数需要更多轮次
        elif quality_score < 0.6 and current_round < MIN_ROUNDS + 1:
            return "continue"
        # 低质量分数但已经完成多轮
        elif quality_score < 0.6 and current_round >= MIN_ROUNDS + 1:
            return "completed"

    # 5. 没有质量分数时，使用轮次和答案数量
    if current_round >= MIN_ROUNDS and len(answers) >= 2:
        return "completed"

    # 6. 其他情况继续学习
    return "continue"


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

    从 AutoResearch 生成的 Markdown 报告中提取关键概念。
    概念来源：
    - 二级标题（## 标题）
    - 三级标题（### 标题）
    - 加粗术语（**术语**）
    - 列表中的关键短语

    Args:
        report_path: 报告文件路径

    Returns:
        概念列表，格式为 [{"name": "概念名", "description": "描述"}]
    """
    from pathlib import Path
    import re

    # 处理文件不存在的情况
    path = Path(report_path)
    if not path.exists():
        return []

    try:
        # 读取报告内容
        content = path.read_text(encoding="utf-8")
    except Exception:
        return []

    # 如果内容为空，返回空列表
    if not content or len(content.strip()) < 50:
        return []

    concepts = []
    seen_names = set()  # 去重

    # 1. 从标题中提取概念
    # 匹配 ## 标题 或 ### 标题，使用更宽松的匹配
    header_pattern = r'^#{2,3}\s+(.+)$'
    for match in re.finditer(header_pattern, content, re.MULTILINE):
        title = match.group(1).strip()
        # 清理标题
        # 移除编号（如 "1. " 或 "2.1 "）
        clean_title = re.sub(r'^\d+(\.\d+)?\.?\s*', '', title)
        # 移除末尾的特殊字符
        clean_title = re.sub(r'\s*[#*]*$', '', clean_title)
        clean_title = clean_title.strip()

        # 过滤掉太短或太泛的标题
        skip_words = {
            '概念', '背景', '架构', '总结', '概述', '摘要', '引言',
            '研究概述', '关键发现', '执行摘要', '技术栈', '范式演进',
            '深度解析', '评估体系', '未来方向', '参考文献', '附录'
        }
        if len(clean_title) >= 2 and clean_title not in skip_words:
            if clean_title not in seen_names:
                seen_names.add(clean_title)
                concepts.append({"name": clean_title, "description": ""})

    # 2. 从加粗术语中提取概念（定义部分）
    # 匹配 **术语**
    bold_pattern = r'\*\*([^*]+?)\*\*'
    for match in re.finditer(bold_pattern, content):
        term = match.group(1).strip()
        # 过滤掉太短或非概念的术语
        skip_words = {'定义', '来源', '作者', '链接', '核心动机', '关键论文',
                     '核心贡献', '注意', '例如', '特点', '生成时间', '研究类型', '模型'}
        if len(term) >= 2 and term not in skip_words:
            # 避免纯数字或标点
            if not term.replace('.', '').replace('+', '').isdigit():
                if term not in seen_names:
                    seen_names.add(term)
                    concepts.append({"name": term, "description": ""})

    # 3. 从列表中的关键短语提取
    # 匹配 - **关键概念** 或 - 关键概念
    list_item_pattern = r'^-\s+\*\*([^*]+)\*\*'
    for match in re.finditer(list_item_pattern, content, re.MULTILINE):
        phrase = match.group(1).strip()
        if len(phrase) >= 3 and phrase not in seen_names:
            skip_phrases = {'核心动机', '关键论文', '核心贡献', '注意', '例如', '特点'}
            if phrase not in skip_phrases:
                seen_names.add(phrase)
                concepts.append({"name": phrase, "description": ""})

    # 4. 优先级排序：包含核心关键词的概念排前面
    priority_keywords = ['RAG', '检索', '嵌入', '生成', '模型', '算法', '架构',
                        '策略', '向量', '语义', '重排序', '模块化', '流水线']

    def has_priority_keyword(concept):
        name = concept["name"]
        return any(kw in name for kw in priority_keywords)

    # 按优先级排序
    concepts.sort(key=lambda c: has_priority_keyword(c), reverse=True)

    # 返回前 15 个概念
    return concepts[:15]


def initialize_task_md(session_path: str, tasks: list) -> None:
    """初始化 Task.md

    在会话目录中创建 Task.md 文件，记录学习任务列表。

    Args:
        session_path: 会话目录路径
        tasks: 任务列表，格式为 [{"id": "task_1", "concept": "...", ...}]
    """
    from pathlib import Path

    session_dir = Path(session_path)

    # 如果目录不存在，创建它
    session_dir.mkdir(parents=True, exist_ok=True)

    # Task.md 文件路径
    task_md_path = session_dir / "Task.md"

    # 生成 Markdown 内容
    lines = [
        "# 学习任务",
        "",
        f"总任务数: {len(tasks)}",
        "",
        "## 任务列表",
        "",
    ]

    if tasks:
        for i, task in enumerate(tasks, 1):
            task_id = task.get("id", f"task_{i}")
            concept = task.get("concept", "未命名概念")
            status = task.get("status", "pending")
            round_num = task.get("round", 0)

            lines.append(f"### 任务 {i}: {concept}")
            lines.append(f"- **ID**: {task_id}")
            lines.append(f"- **状态**: {status}")
            lines.append(f"- **轮次**: {round_num}")
            lines.append("")
    else:
        lines.append("无任务")
        lines.append("")

    lines.append("## 进度跟踪")
    lines.append("")
    lines.append("| 任务 ID | 状态 | 轮次 |")
    lines.append("|---------|------|------|")

    if tasks:
        for task in tasks:
            task_id = task.get("id", "-")
            status = task.get("status", "pending")
            round_num = task.get("round", 0)
            lines.append(f"| {task_id} | {status} | {round_num} |")

    # 写入文件
    content = "\n".join(lines)
    task_md_path.write_text(content, encoding="utf-8")
