"""
Skills 适配器

为现有 Claude Skills 提供文件接口适配，实现 CONTEXT.md、Task.md、handoff.md 的读写。
"""

from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime


class SkillsAdapter:
    """Skills 适配器基类

    提供会话文件（CONTEXT.md、Task.md、handoff.md）的统一读写接口。

    Args:
        session_path: 会话目录路径

    Attributes:
        session_path: 会话目录的 Path 对象
    """

    def __init__(self, session_path: str):
        """初始化适配器

        Args:
            session_path: 会话目录路径，如不存在将自动创建
        """
        self.session_path = Path(session_path)
        self.session_path.mkdir(parents=True, exist_ok=True)

    # ==============================================================================
    # CONTEXT.md 操作
    # ==============================================================================

    def load_context(self) -> str:
        """加载 CONTEXT.md 内容

        Returns:
            CONTEXT.md 的完整内容字符串，文件不存在时返回空字符串
        """
        context_file = self.session_path / "CONTEXT.md"
        if not context_file.exists():
            return ""
        return context_file.read_text(encoding="utf-8")

    def update_context(self, key: str, value: str) -> None:
        """更新 CONTEXT.md

        将新的键值对追加到 CONTEXT.md 文件中。

        Args:
            key: 术语键名
            value: 术语定义或说明
        """
        context_file = self.session_path / "CONTEXT.md"

        # 读取现有内容
        if context_file.exists():
            content = context_file.read_text(encoding="utf-8")
        else:
            # 创建新文件，添加基础结构
            content = "# Session 上下文\n\n## Language\n\n"

        # 追加新内容
        new_entry = f"\n**{key}**:\n{value}\n"
        content += new_entry

        # 写入文件
        context_file.write_text(content, encoding="utf-8")

    # ==============================================================================
    # Task.md 操作
    # ==============================================================================

    def load_task_progress(self) -> str:
        """加载 Task.md 内容

        Returns:
            Task.md 的完整内容字符串，文件不存在时返回空字符串
        """
        task_file = self.session_path / "Task.md"
        if not task_file.exists():
            return ""
        return task_file.read_text(encoding="utf-8")

    def update_task_progress(self, task_id: str, status: str) -> None:
        """更新任务进度

        修改或添加任务状态到 Task.md。

        Args:
            task_id: 任务标识符
            status: 任务状态 (pending/in_progress/completed)
        """
        task_file = self.session_path / "Task.md"

        # 读取现有内容
        if task_file.exists():
            content = task_file.read_text(encoding="utf-8")
        else:
            content = "# 学习任务\n\n"

        # 简单追加新的任务条目（实际实现需要更复杂的解析和替换）
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        new_entry = f"## {task_id}\n- 状态: {status}\n- 更新时间: {timestamp}\n\n"
        content += new_entry

        task_file.write_text(content, encoding="utf-8")

    # ==============================================================================
    # handoff.md 操作
    # ==============================================================================

    def save_handoff(self, handoff_data: Dict[str, Any]) -> None:
        """保存会话交接信息到 handoff.md

        Args:
            handoff_data: 交接信息字典，包含:
                - current_task: 当前任务
                - next_task: 下一任务
                - notes: 备注信息
        """
        handoff_file = self.session_path / "handoff.md"

        current_task = handoff_data.get("current_task", "")
        next_task = handoff_data.get("next_task", "")
        notes = handoff_data.get("notes", "")
        timestamp = datetime.now().isoformat()

        content = f"""# 会话交接

## 当前状态
- 当前任务: {current_task}
- 下一任务: {next_task}
- 时间: {timestamp}

## 备注
{notes}

## 下一步
"""

        handoff_file.write_text(content, encoding="utf-8")

    def load_handoff(self) -> str:
        """加载 handoff.md 内容

        Returns:
            handoff.md 的完整内容字符串，文件不存在时返回空字符串
        """
        handoff_file = self.session_path / "handoff.md"
        if not handoff_file.exists():
            return ""
        return handoff_file.read_text(encoding="utf-8")


# ==============================================================================
# 具体 Skills 适配器
# ==============================================================================

class GrillMeAdapter(SkillsAdapter):
    """grill-me skill 适配器

    提供 AI 考用户功能的文件接口适配。
    """

    def generate_questions(self, task_id: str, count: int = 5) -> list:
        """生成 grill-me 问题

        注意: 实际问题生成由 LLM 在上层处理，此方法提供文件数据支持。

        Args:
            task_id: 任务 ID
            count: 问题数量

        Returns:
            空列表，实际由 LLM 生成问题
        """
        # 加载上下文和任务信息
        context = self.load_context()
        task_info = self.load_task_progress()

        # 返回上下文信息供上层使用
        return []

    def evaluate_answers(self, answers: Dict[str, str]) -> Dict[str, Any]:
        """评估答案并更新 CONTEXT.md

        注意: 实际评估由 LLM 处理，此方法保存结果。

        Args:
            answers: 答案字典

        Returns:
            评估结果字典
        """
        # 更新 CONTEXT.md 记录评估结果
        self.update_context("last_grill_results", str(answers))
        return {"status": "saved"}


class GrillYouAdapter(SkillsAdapter):
    """grill-you skill 适配器

    提供用户考 AI 功能的文件接口适配。
    """

    def suggest_questions(self, topic: str, count: int = 3) -> list:
        """建议用户可以问的问题

        注意: 实际问题建议由 LLM 生成，此方法提供接口。

        Args:
            topic: 主题
            count: 建议问题数量

        Returns:
            空列表，实际由 LLM 生成
        """
        # 加载上下文
        self.load_context()
        return []


class AdvanceTaskAdapter(SkillsAdapter):
    """advance-task skill 适配器

    提供任务进度保存和会话交接功能的文件接口适配。
    """

    def complete_task(self, task_id: str, notes: str = "") -> None:
        """完成任务，更新状态并生成 handoff.md

        Args:
            task_id: 任务 ID
            notes: 完成备注
        """
        # 更新任务状态为完成
        self.update_task_progress(task_id, "completed")

        # 生成 handoff.md
        handoff_data = {
            "current_task": task_id,
            "next_task": "",  # 由上层填充
            "notes": notes
        }
        self.save_handoff(handoff_data)
