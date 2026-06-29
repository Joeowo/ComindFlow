"""
S5-T1: 端到端集成测试 - 完整流程测试

测试完整的技能系统流程：用户请求 → 路由 → 执行 → 返回
"""
import pytest
import tempfile
from pathlib import Path

from agent_framework.skills.registry import SkillRegistry
from agent_framework.skills.loader import SkillLoader
from agent_framework.skills.middleware import SkillMiddleware
from agent_framework.skills.executor import ParallelSkillExecutor
from agent_framework.skills.context_optimizer import ContextOptimizer
from agent_framework.observability.tracing import TraceManager
from agent_framework.observability.diagnostics import ErrorDiagnostics
from agent_framework.observability.dashboard import ObservabilityDashboard
from agent_framework.skills.models.context import SkillContext
from agent_framework.skills.models.result import SkillResult


@pytest.fixture
def sample_skills_dir(tmp_path: Path) -> Path:
    """创建示例技能目录"""
    skills = [
        {
            "name": "grill-me",
            "description": "Interview user with dense questions about a topic",
            "category": "grilling",
            "tags": ["qa", "interview", "test"]
        },
        {
            "name": "grill-you",
            "description": "Answer user's questions with detailed explanations",
            "category": "qa",
            "tags": ["answer", "help", "explain"]
        },
        {
            "name": "advance-task",
            "description": "Update session state after each Q&A round",
            "category": "session",
            "tags": ["advance", "continue", "handoff"]
        }
    ]

    for skill in skills:
        skill_dir = tmp_path / skill["name"]
        skill_dir.mkdir(exist_ok=True)

        skill_md_content = f"""---
name: {skill['name']}
description: {skill['description']}
version: 1.0
category: {skill['category']}
tags: {skill['tags']}
---

# {skill['name']}

{skill['description']}

## Usage

Use this skill when you need to {skill['category']} related tasks.

## Examples

Example 1: Basic usage
Example 2: Advanced usage
"""
        (skill_dir / "SKILL.md").write_text(skill_md_content, encoding="utf-8")

    return tmp_path


class TestE2EFullFlow:
    """端到端完整流程测试"""

    def test_complete_skill_flow_from_request_to_execution(self, sample_skills_dir: Path):
        """
        测试完整的技能流程：用户请求 → 路由 → 执行 → 返回

        Given: 一个包含多个技能的系统
        When: 用户发送请求
        Then: 请求被正确路由、执行并返回结果
        """
        # 1. 初始化组件
        registry = SkillRegistry(skills_dir=sample_skills_dir)
        registry.discover()

        loader = SkillLoader(registry)
        middleware = SkillMiddleware(registry)

        # 2. 测试路由
        state = {"task_type": "grilling"}
        skill_name = middleware.route(state)
        assert skill_name == "grill-me"

        # 3. 测试执行
        context = SkillContext(session_path=sample_skills_dir, state=state)
        result = middleware.execute_skill(skill_name, context, loader)

        # 4. 验证结果
        assert result.success is True
        assert result.output is not None
        assert result.metadata["skill_name"] == "grill-me"

    def test_complete_flow_with_context_optimization(self, sample_skills_dir: Path):
        """
        测试包含上下文优化的完整流程

        Given: 一个带有上下文优化器的系统
        When: 执行完整流程
        Then: 元数据被正确注入，按需加载生效
        """
        registry = SkillRegistry(skills_dir=sample_skills_dir)
        registry.discover()

        optimizer = ContextOptimizer(registry=registry)

        # 测试元数据注入
        metadata = optimizer.inject_metadata()
        assert "## Skills Available" in metadata
        assert "grill-me" in metadata
        assert "grill-you" in metadata
        assert "advance-task" in metadata

        # 测试按需加载判断
        state = {"task_type": "grilling"}
        should_load = optimizer.should_load_full_content("grill-me", state)
        assert should_load is True

    def test_complete_flow_with_observability(self, sample_skills_dir: Path):
        """
        测试包含可观测性的完整流程

        Given: 一个带有可观测性系统的完整流程
        When: 执行技能
        Then: 链路追踪正确记录，可观测性数据完整
        """
        registry = SkillRegistry(skills_dir=sample_skills_dir)
        registry.discover()

        loader = SkillLoader(registry)
        middleware = SkillMiddleware(registry)

        trace_manager = TraceManager()

        # 开始追踪
        trace_id = trace_manager.start_trace({"session": "test-e2e"})

        # 执行技能
        context = SkillContext(session_path=sample_skills_dir, state={"task_type": "grilling"})
        skill_name = middleware.route(context.state)
        result = middleware.execute_skill(skill_name, context, loader)

        # 创建 span
        span_id = trace_manager.create_span(trace_id, "grill-me")
        trace_manager.end_span(trace_id, span_id, {"success": result.success})

        # 验证追踪
        trace = trace_manager.get_trace(trace_id)
        assert trace is not None
        assert trace.trace_id == trace_id
        assert len(trace.skill_chain) >= 1

    def test_complete_flow_with_error_handling(self, sample_skills_dir: Path):
        """
        测试错误处理流程

        Given: 一个技能系统
        When: 发生错误（如技能不存在）
        Then: 错误被正确捕获和处理
        """
        registry = SkillRegistry(skills_dir=sample_skills_dir)
        registry.discover()

        loader = SkillLoader(registry)
        middleware = SkillMiddleware(registry)
        diagnostics = ErrorDiagnostics()

        # 测试路由失败
        state = {"task_type": "nonexistent"}
        with pytest.raises(Exception):
            middleware.route(state)

        # 测试诊断 - 使用已知的异常类型
        error_record = diagnostics.diagnose(
            exception_type="ToolNotFoundError",
            error_message="Tool 'search' not found",
            skill_name="grill-me",
            context={"session": "test-e2e"}
        )

        assert error_record is not None
        assert error_record.severity in ["P0", "P1", "P2"]
        assert error_record.recovery_action is not None
        assert error_record.error_type == "ToolNotFoundError"


class TestE2EParallelExecution:
    """端到端并行执行测试"""

    def test_parallel_skills_execution(self, sample_skills_dir: Path):
        """
        测试多技能并行执行

        Given: 多个技能
        When: 并行执行它们
        Then: 所有技能正确执行，状态隔离
        """
        registry = SkillRegistry(skills_dir=sample_skills_dir)
        registry.discover()

        loader = SkillLoader(registry)
        middleware = SkillMiddleware(registry)
        executor = ParallelSkillExecutor(middleware)

        # 并行执行多个技能
        contexts = [
            SkillContext(session_path=sample_skills_dir, state={"id": i})
            for i in range(3)
        ]

        skill_names = ["grill-me", "grill-you", "advance-task"]
        results = executor.execute_parallel(skill_names, contexts, loader)

        # 验证结果
        assert len(results) == 3
        assert all(r.success for r in results)


class TestE2EIntegration:
    """端到端集成测试"""

    def test_all_components_integration(self, sample_skills_dir: Path):
        """
        测试所有组件的集成

        Given: 所有组件都已初始化
        When: 执行完整流程
        Then: 所有组件协同工作
        """
        # 初始化所有组件
        registry = SkillRegistry(skills_dir=sample_skills_dir)
        registry.discover()

        loader = SkillLoader(registry)
        middleware = SkillMiddleware(registry)
        optimizer = ContextOptimizer(registry=registry)
        trace_manager = TraceManager()
        executor = ParallelSkillExecutor(middleware)

        # 验证组件可以协同工作
        skills = registry.list_all()
        assert len(skills) == 3

        metadata = optimizer.inject_metadata()
        assert "grill-me" in metadata

        trace_id = trace_manager.start_trace({})
        assert trace_id is not None

        context = SkillContext(session_path=sample_skills_dir, state={})
        result = middleware.execute_skill("grill-me", context, loader)
        assert result.success is True

        results = executor.execute_parallel(["grill-me"], [context], loader)
        assert len(results) == 1
