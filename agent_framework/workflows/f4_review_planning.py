"""
F4 复习计划生成 Workflow

实现基于 SM2 算法的复习计划生成：
- 知识提取: 从学习资料中提取知识点
- SM2 调度: 使用 SuperMemo-2 算法计算复习间隔
- 计划输出: 生成复习计划文档
"""

from typing import Dict, Any
from datetime import datetime, timedelta
from pathlib import Path

from agent_framework.core.state import AgentState
from langgraph.graph import StateGraph, END


# =============================================================================
# 知识提取节点
# =============================================================================

def extract_knowledge_node(state: AgentState) -> Dict[str, Any]:
    """知识提取节点

    从学习资料中提取知识点并生成问题池。

    Args:
        state: 当前状态，包含 source_paths

    Returns:
        更新后的状态，包含知识点列表
    """
    source_paths = state.get("source_paths", [])
    knowledge_points = []

    for source_path in source_paths:
        try:
            path = Path(source_path)
            if path.exists():
                content = path.read_text(encoding="utf-8")

                # 简单提取：从加粗文本中提取知识点
                import re
                bold_pattern = r'\*\*([^*]+)\*\*[：:]\s*([^\n]+)'
                matches = re.findall(bold_pattern, content)

                for term, definition in matches:
                    knowledge_points.append({
                        "question": f"什么是 {term}？",
                        "answer": definition.strip(),
                        "created_at": datetime.now().isoformat()
                    })

                # 从二级标题提取
                header_pattern = r'^##\s+(.+)$'
                for match in re.finditer(header_pattern, content, re.MULTILINE):
                    title = match.group(1).strip()
                    if title and len(title) > 1:
                        knowledge_points.append({
                            "question": f"请解释 {title}",
                            "answer": f"{title} 的相关内容...",
                            "created_at": datetime.now().isoformat()
                        })
        except Exception:
            # 跳过无法读取的文件
            continue

    return {
        "knowledge_points": knowledge_points,
        "current_step": "knowledge_extracted"
    }


# =============================================================================
# SM2 调度节点
# =============================================================================

def sm2_schedule_node(state: AgentState) -> Dict[str, Any]:
    """SM2 调度节点

    使用 SM-2 算法计算复习间隔。

    Args:
        state: 当前状态，包含 knowledge_points

    Returns:
        更新后的状态，包含调度项列表
    """
    knowledge_points = state.get("knowledge_points", [])
    schedule_items = []

    for kp in knowledge_points:
        # SM2 初始参数
        ease_factor = 2.5
        interval = 1  # 第1次复习间隔为1天
        repetition = 0

        # 计算第一次复习时间
        next_review = datetime.now() + timedelta(days=interval)

        schedule_items.append({
            "question": kp.get("question", ""),
            "answer": kp.get("answer", ""),
            "ease_factor": ease_factor,
            "interval": interval,
            "repetition": repetition,
            "next_review_date": next_review.isoformat(),
            "created_at": kp.get("created_at", datetime.now().isoformat())
        })

    return {
        "schedule_items": schedule_items,
        "current_step": "sm2_scheduled"
    }


# =============================================================================
# 计划输出节点
# =============================================================================

def generate_plan_node(state: AgentState) -> Dict[str, Any]:
    """计划输出节点

    生成复习计划文档。

    Args:
        state: 当前状态，包含 schedule_items

    Returns:
        更新后的状态，包含计划文件路径
    """
    schedule_items = state.get("schedule_items", [])
    session_path = state.get("session_path", "")

    # 按日期分组
    from collections import defaultdict
    items_by_date = defaultdict(list)

    for item in schedule_items:
        date_str = item["next_review_date"][:10]  # YYYY-MM-DD
        items_by_date[date_str].append(item)

    # 生成计划内容
    lines = [
        "# 复习计划",
        "",
        f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"总知识点数: {len(schedule_items)}",
        "",
        "## 复习日程",
        ""
    ]

    # 按日期排序
    sorted_dates = sorted(items_by_date.keys())

    for date_str in sorted_dates:
        lines.append(f"### {date_str}")
        lines.append("")

        for item in items_by_date[date_str]:
            lines.append(f"- **问题**: {item['question']}")
            lines.append(f"  - **答案**: {item['answer'][:50]}...")

            # 显示 SM2 参数
            lines.append(f"  - 间隔: {item['interval']} 天")
            lines.append(f"  - 难度因子: {item['ease_factor']:.2f}")
            lines.append("")

    lines.extend([
        "## SM2 算法说明",
        "",
        "- **EF (易记因子)**: 表示记忆难易程度，初始值 2.5",
        "- **I (间隔)**: 复习间隔（天）",
        "- 复习评分会影响后续间隔计算",
        ""
    ])

    # 保存文件
    plan_path = Path(session_path) / "review_plan.md"
    plan_path.write_text("\n".join(lines), encoding="utf-8")

    return {
        "review_plan_path": str(plan_path),
        "current_step": "plan_generated"
    }


# =============================================================================
# Workflow 创建
# =============================================================================

def create_f4_workflow() -> StateGraph:
    """创建 F4 复习计划生成 Workflow

    Returns:
        StateGraph 实例
    """
    workflow = StateGraph(AgentState)

    # 添加节点
    workflow.add_node("extract_knowledge", extract_knowledge_node)
    workflow.add_node("sm2_schedule", sm2_schedule_node)
    workflow.add_node("generate_plan", generate_plan_node)

    # 设置入口
    workflow.set_entry_point("extract_knowledge")

    # 添加边
    workflow.add_edge("extract_knowledge", "sm2_schedule")
    workflow.add_edge("sm2_schedule", "generate_plan")
    workflow.add_edge("generate_plan", END)

    return workflow
