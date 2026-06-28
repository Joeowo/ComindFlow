"""
Skills Adapter 测试

测试 Skills 适配器基类和具体实现。
"""

import pytest
from pathlib import Path
from agent_framework.tools.skills_adapters import (
    SkillsAdapter,
    GrillMeAdapter,
    GrillYouAdapter,
    AdvanceTaskAdapter,
)


class TestSkillsAdapterInit:
    """SkillsAdapter 初始化测试"""

    def test_init_with_valid_session_path(self, tmp_path):
        """SkillsAdapter 应能用有效路径初始化"""
        # Given: 一个临时目录路径
        session_path = str(tmp_path / "test_session")

        # When: 创建 SkillsAdapter
        adapter = SkillsAdapter(session_path)

        # Then: session_path 属性应正确设置
        assert adapter.session_path == Path(session_path)

    def test_init_creates_session_directory(self, tmp_path):
        """SkillsAdapter 初始化时如目录不存在应自动创建"""
        # Given: 一个不存在的目录路径
        session_path = str(tmp_path / "new_session" / "subdir")

        # When: 创建 SkillsAdapter
        adapter = SkillsAdapter(session_path)

        # Then: 目录应被创建
        assert adapter.session_path.exists()
        assert adapter.session_path.is_dir()


class TestSkillsAdapterLoadContext:
    """SkillsAdapter CONTEXT.md 加载测试"""

    def test_load_context_returns_empty_string_when_no_file(self, tmp_path):
        """当 CONTEXT.md 不存在时，load_context 应返回空字符串"""
        # Given: 一个没有 CONTEXT.md 的会话目录
        adapter = SkillsAdapter(str(tmp_path))

        # When: 调用 load_context
        context = adapter.load_context()

        # Then: 应返回空字符串
        assert context == ""

    def test_load_context_parses_markdown_file(self, tmp_path):
        """load_context 应正确解析 CONTEXT.md 文件"""
        # Given: 一个包含 CONTEXT.md 的会话目录
        context_file = tmp_path / "CONTEXT.md"
        context_file.write_text("""# Session 上下文

## Language

**货币政策**:
央行调节货币供应量和利率的政策工具

## Relationships

- 利率影响投资成本
""", encoding="utf-8")
        adapter = SkillsAdapter(str(tmp_path))

        # When: 调用 load_context
        context = adapter.load_context()

        # Then: 应返回文件内容字符串
        assert "货币政策" in context
        assert "利率影响投资成本" in context
        assert isinstance(context, str)

    def test_load_context_handles_encoding(self, tmp_path):
        """load_context 应正确处理 UTF-8 编码"""
        # Given: 一个包含中文的 CONTEXT.md
        context_file = tmp_path / "CONTEXT.md"
        context_file.write_text("# 测试上下文\n\n中文内容测试", encoding="utf-8")
        adapter = SkillsAdapter(str(tmp_path))

        # When: 调用 load_context
        context = adapter.load_context()

        # Then: 中文应正确读取
        assert "中文内容测试" in context


class TestSkillsAdapterUpdateContext:
    """SkillsAdapter CONTEXT.md 更新测试"""

    def test_update_context_creates_new_file(self, tmp_path):
        """update_context 应在文件不存在时创建新文件"""
        # Given: 一个空的会话目录
        adapter = SkillsAdapter(str(tmp_path))

        # When: 更新 context
        adapter.update_context("test_key", "test_value")

        # Then: CONTEXT.md 应被创建
        context_file = tmp_path / "CONTEXT.md"
        assert context_file.exists()

    def test_update_context_appends_to_existing_file(self, tmp_path):
        """update_context 应追加到现有文件"""
        # Given: 一个包含现有内容的 CONTEXT.md
        context_file = tmp_path / "CONTEXT.md"
        context_file.write_text("# 原有内容\n\n原有段落", encoding="utf-8")
        adapter = SkillsAdapter(str(tmp_path))

        # When: 更新 context
        adapter.update_context("new_section", "新内容")

        # Then: 新内容应被追加，原有内容保留
        content = context_file.read_text(encoding="utf-8")
        assert "原有内容" in content
        assert "新内容" in content

    def test_update_context_proper_format(self, tmp_path):
        """update_context 应使用正确的 Markdown 格式"""
        # Given: SkillsAdapter
        adapter = SkillsAdapter(str(tmp_path))

        # When: 更新 context
        adapter.update_context("货币政策", "央行调节货币供应量的工具")

        # Then: 应使用正确的 Markdown 格式
        content = (tmp_path / "CONTEXT.md").read_text(encoding="utf-8")
        assert "**货币政策**:" in content
        assert "央行调节货币供应量的工具" in content


class TestSkillsAdapterLoadTaskProgress:
    """SkillsAdapter Task.md 加载测试"""

    def test_load_task_progress_returns_empty_string_when_no_file(self, tmp_path):
        """当 Task.md 不存在时，应返回空字符串"""
        # Given: 空会话目录
        adapter = SkillsAdapter(str(tmp_path))

        # When: 加载任务进度
        tasks = adapter.load_task_progress()

        # Then: 应返回空字符串
        assert tasks == ""

    def test_load_task_progress_parses_markdown_tasks(self, tmp_path):
        """load_task_progress 应正确解析 Task.md"""
        # Given: 包含 Task.md 的会话
        task_file = tmp_path / "Task.md"
        task_file.write_text("""# 学习任务

## Task 1: 货币政策基础
- 状态: in_progress
- 轮次: 2

## Task 2: 财政政策
- 状态: pending
""", encoding="utf-8")
        adapter = SkillsAdapter(str(tmp_path))

        # When: 加载任务进度
        tasks = adapter.load_task_progress()

        # Then: 应返回文件内容字符串供进一步解析
        assert "Task 1" in tasks
        assert "in_progress" in tasks
        assert isinstance(tasks, str)


class TestSkillsAdapterUpdateTaskProgress:
    """SkillsAdapter Task.md 更新测试"""

    def test_update_task_creates_new_file(self, tmp_path):
        """update_task_progress 应在文件不存在时创建新文件"""
        # Given: 空会话目录
        adapter = SkillsAdapter(str(tmp_path))

        # When: 更新任务
        adapter.update_task_progress("task_1", "in_progress")

        # Then: Task.md 应被创建
        task_file = tmp_path / "Task.md"
        assert task_file.exists()

    def test_update_task_modifies_existing_task(self, tmp_path):
        """update_task_progress 应正确修改现有任务状态"""
        # Given: 包含现有 Task.md
        task_file = tmp_path / "Task.md"
        task_file.write_text("""# 学习任务

## Task 1: 货币政策
- 状态: pending
- 轮次: 0
""", encoding="utf-8")
        adapter = SkillsAdapter(str(tmp_path))

        # When: 更新任务状态
        adapter.update_task_progress("Task 1", "in_progress")

        # Then: 状态应被更新
        content = task_file.read_text(encoding="utf-8")
        assert "in_progress" in content


class TestSkillsAdapterHandoff:
    """SkillsAdapter handoff.md 测试"""

    def test_save_handoff_creates_file(self, tmp_path):
        """save_handoff 应创建 handoff.md 文件"""
        # Given: SkillsAdapter
        adapter = SkillsAdapter(str(tmp_path))

        # When: 保存 handoff
        handoff_data = {
            "current_task": "Task 1",
            "next_task": "Task 2",
            "notes": "进度良好"
        }
        adapter.save_handoff(handoff_data)

        # Then: handoff.md 应被创建
        handoff_file = tmp_path / "handoff.md"
        assert handoff_file.exists()

    def test_save_handoff_correct_format(self, tmp_path):
        """save_handoff 应使用正确的 Markdown 格式"""
        # Given: SkillsAdapter
        adapter = SkillsAdapter(str(tmp_path))

        # When: 保存 handoff
        handoff_data = {
            "current_task": "Task 1",
            "next_task": "Task 2",
            "notes": "理解良好"
        }
        adapter.save_handoff(handoff_data)

        # Then: 应包含正确的格式和内容
        content = (tmp_path / "handoff.md").read_text(encoding="utf-8")
        assert "# 会话交接" in content
        assert "Task 1" in content
        assert "Task 2" in content
        assert "理解良好" in content

    def test_load_handoff_returns_empty_string_when_no_file(self, tmp_path):
        """load_handoff 在文件不存在时应返回空字符串"""
        # Given: 空会话目录
        adapter = SkillsAdapter(str(tmp_path))

        # When: 加载 handoff
        handoff = adapter.load_handoff()

        # Then: 应返回空字符串
        assert handoff == ""

    def test_load_handoff_parses_existing_file(self, tmp_path):
        """load_handoff 应正确解析 handoff.md"""
        # Given: 包含 handoff.md
        handoff_file = tmp_path / "handoff.md"
        handoff_file.write_text("""# 会话交接

## 当前状态
- 当前任务: Task 1
- 下一任务: Task 2

## 备注
用户理解良好

## 下一步
继续 Task 1
""", encoding="utf-8")
        adapter = SkillsAdapter(str(tmp_path))

        # When: 加载 handoff
        handoff = adapter.load_handoff()

        # Then: 应返回解析后的内容
        assert "Task 1" in handoff
        assert isinstance(handoff, str)


# ==============================================================================
# 具体适配器测试
# ==============================================================================

class TestGrillMeAdapter:
    """GrillMeAdapter 测试"""

    def test_init(self, tmp_path):
        """GrillMeAdapter 应能初始化"""
        # Given: 会话路径
        adapter = GrillMeAdapter(str(tmp_path))

        # Then: 应继承自 SkillsAdapter
        assert isinstance(adapter, SkillsAdapter)
        assert adapter.session_path == tmp_path

    def test_generate_questions_loads_context(self, tmp_path):
        """generate_questions 应加载上下文"""
        # Given: 包含 CONTEXT.md 的会话
        context_file = tmp_path / "CONTEXT.md"
        context_file.write_text("**货币政策**: 央行调节工具", encoding="utf-8")
        adapter = GrillMeAdapter(str(tmp_path))

        # When: 生成问题
        result = adapter.generate_questions("task_1", count=5)

        # Then: 应返回列表
        assert isinstance(result, list)

    def test_evaluate_answers_updates_context(self, tmp_path):
        """evaluate_answers 应更新 CONTEXT.md"""
        # Given: GrillMeAdapter
        adapter = GrillMeAdapter(str(tmp_path))

        # When: 评估答案
        answers = {"q1": "回答1", "q2": "回答2"}
        result = adapter.evaluate_answers(answers)

        # Then: 应更新 CONTEXT.md
        context = adapter.load_context()
        assert "last_grill_results" in context
        assert result["status"] == "saved"


class TestGrillYouAdapter:
    """GrillYouAdapter 测试"""

    def test_init(self, tmp_path):
        """GrillYouAdapter 应能初始化"""
        # Given: 会话路径
        adapter = GrillYouAdapter(str(tmp_path))

        # Then: 应继承自 SkillsAdapter
        assert isinstance(adapter, SkillsAdapter)

    def test_suggest_questions_loads_context(self, tmp_path):
        """suggest_questions 应加载上下文"""
        # Given: 包含 CONTEXT.md 的会话
        context_file = tmp_path / "CONTEXT.md"
        context_file.write_text("**术语**: 定义", encoding="utf-8")
        adapter = GrillYouAdapter(str(tmp_path))

        # When: 建议问题
        result = adapter.suggest_questions("货币政策", count=3)

        # Then: 应返回列表
        assert isinstance(result, list)


class TestAdvanceTaskAdapter:
    """AdvanceTaskAdapter 测试"""

    def test_init(self, tmp_path):
        """AdvanceTaskAdapter 应能初始化"""
        # Given: 会话路径
        adapter = AdvanceTaskAdapter(str(tmp_path))

        # Then: 应继承自 SkillsAdapter
        assert isinstance(adapter, SkillsAdapter)

    def test_complete_task_updates_status(self, tmp_path):
        """complete_task 应更新任务状态为 completed"""
        # Given: AdvanceTaskAdapter
        adapter = AdvanceTaskAdapter(str(tmp_path))

        # When: 完成任务
        adapter.complete_task("Task 1", "理解良好")

        # Then: Task.md 应包含 completed 状态
        task_content = adapter.load_task_progress()
        assert "completed" in task_content
        assert "Task 1" in task_content

    def test_complete_task_creates_handoff(self, tmp_path):
        """complete_task 应创建 handoff.md"""
        # Given: AdvanceTaskAdapter
        adapter = AdvanceTaskAdapter(str(tmp_path))

        # When: 完成任务
        adapter.complete_task("Task 1", "已完成")

        # Then: handoff.md 应被创建
        handoff_content = adapter.load_handoff()
        assert "Task 1" in handoff_content
        assert "已完成" in handoff_content
