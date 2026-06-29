"""
S5-T2: 性能基准测试 - 响应时间测试

测试系统各组件的响应时间，验证性能目标。
"""
import pytest
import time
import tempfile
from pathlib import Path

from agent_framework.skills.registry import SkillRegistry
from agent_framework.skills.loader import SkillLoader
from agent_framework.skills.middleware import SkillMiddleware
from agent_framework.skills.executor import ParallelSkillExecutor
from agent_framework.observability.tracing import TraceManager
from agent_framework.skills.models.context import SkillContext


@pytest.fixture
def test_skills_dir(tmp_path: Path) -> Path:
    """创建测试技能目录"""
    skills = [
        ("grill-me", "grilling"),
        ("grill-you", "qa"),
        ("advance-task", "advance"),
        ("review-session", "review"),
        ("continue-task", "continue")
    ]

    for skill_name, category in skills:
        skill_dir = tmp_path / skill_name
        skill_dir.mkdir(exist_ok=True)
        (skill_dir / "SKILL.md").write_text(
            f"---\nname: {skill_name}\ndescription: Test skill\ncategory: {category}\n---\n# {skill_name}\n\nContent",
            encoding="utf-8"
        )

    return tmp_path


class TestResponseTime:
    """响应时间测试"""

    def test_registry_discovery_time(self, test_skills_dir: Path):
        """
        测试 Registry 发现时间

        Given: 多个技能目录
        When: 执行发现
        Then: 发现时间 < 100ms
        """
        registry = SkillRegistry(skills_dir=test_skills_dir)

        start = time.time()
        registry.discover()
        elapsed = (time.time() - start) * 1000  # 转换为毫秒

        print(f"\nRegistry discovery time: {elapsed:.2f}ms")

        # 发现 5 个技能应该很快（< 100ms）
        assert elapsed < 100, f"Discovery took {elapsed:.2f}ms, exceeds 100ms target"

    def test_skill_loading_time(self, test_skills_dir: Path):
        """
        测试技能加载时间

        Given: 已发现的技能
        When: 加载技能内容
        Then: 加载时间 < 50ms
        """
        registry = SkillRegistry(skills_dir=test_skills_dir)
        registry.discover()

        loader = SkillLoader(registry)

        start = time.time()
        content = loader.load_skill("grill-me")
        elapsed = (time.time() - start) * 1000

        print(f"\nSkill loading time: {elapsed:.2f}ms")

        # 加载单个技能应该很快（< 50ms）
        assert elapsed < 50, f"Loading took {elapsed:.2f}ms, exceeds 50ms target"
        assert content is not None

    def test_middleware_routing_time(self, test_skills_dir: Path):
        """
        测试 Middleware 路由时间

        Given: 已初始化的 Middleware
        When: 执行路由
        Then: 路由时间 < 10ms
        """
        registry = SkillRegistry(skills_dir=test_skills_dir)
        registry.discover()

        middleware = SkillMiddleware(registry)

        state = {"task_type": "grilling"}

        start = time.time()
        skill_name = middleware.route(state)
        elapsed = (time.time() - start) * 1000

        print(f"\nMiddleware routing time: {elapsed:.2f}ms")

        # 路由应该非常快（< 10ms）
        assert elapsed < 10, f"Routing took {elapsed:.2f}ms, exceeds 10ms target"
        assert skill_name is not None

    def test_skill_execution_time(self, test_skills_dir: Path):
        """
        测试技能执行时间

        Given: 已初始化的组件
        When: 执行技能
        Then: 执行时间 < 100ms
        """
        registry = SkillRegistry(skills_dir=test_skills_dir)
        registry.discover()

        loader = SkillLoader(registry)
        middleware = SkillMiddleware(registry)

        context = SkillContext(session_path=test_skills_dir, state={})

        start = time.time()
        result = middleware.execute_skill("grill-me", context, loader)
        elapsed = (time.time() - start) * 1000

        print(f"\nSkill execution time: {elapsed:.2f}ms")

        # 执行技能应该很快（< 100ms）
        assert elapsed < 100, f"Execution took {elapsed:.2f}ms, exceeds 100ms target"
        assert result.success is True

    def test_parallel_execution_time(self, test_skills_dir: Path):
        """
        测试并行执行时间

        Given: 多个技能
        When: 并行执行
        Then: 并行执行时间合理
        """
        registry = SkillRegistry(skills_dir=test_skills_dir)
        registry.discover()

        loader = SkillLoader(registry)
        middleware = SkillMiddleware(registry)
        executor = ParallelSkillExecutor(middleware)

        contexts = [
            SkillContext(session_path=test_skills_dir, state={"id": i})
            for i in range(5)
        ]

        start = time.time()
        results = executor.execute_parallel(
            ["grill-me", "grill-you", "advance-task", "review-session", "continue-task"],
            contexts,
            loader
        )
        elapsed = (time.time() - start) * 1000

        print(f"\nParallel execution time (5 skills): {elapsed:.2f}ms")

        # 并行执行 5 个技能应该 < 500ms
        assert elapsed < 500, f"Parallel execution took {elapsed:.2f}ms, exceeds 500ms target"
        assert len(results) == 5
        assert all(r.success for r in results)


class TestEndToEndResponseTime:
    """端到端响应时间测试"""

    def test_full_flow_response_time(self, test_skills_dir: Path):
        """
        测试完整流程响应时间

        Given: 完整的系统
        When: 执行完整流程（发现 → 路由 → 执行）
        Then: 端到端时间 < 2s
        """
        start = time.time()

        # 1. 发现
        registry = SkillRegistry(skills_dir=test_skills_dir)
        registry.discover()

        # 2. 路由
        loader = SkillLoader(registry)
        middleware = SkillMiddleware(registry)
        state = {"task_type": "grilling"}
        skill_name = middleware.route(state)

        # 3. 执行
        context = SkillContext(session_path=test_skills_dir, state={})
        result = middleware.execute_skill(skill_name, context, loader)

        elapsed = time.time() - start

        print(f"\nFull flow response time: {elapsed:.3f}s ({elapsed * 1000:.2f}ms)")

        # 完整流程应该 < 2s（根据规范目标）
        assert elapsed < 2.0, f"Full flow took {elapsed:.3f}s, exceeds 2s target"
        assert result.success is True

    def test_end_to_end_with_tracing_time(self, test_skills_dir: Path):
        """
        测试带追踪的端到端响应时间

        Given: 完整的系统加追踪
        When: 执行完整流程
        Then: 端到端时间 < 2.1s（允许 5% 追踪开销）
        """
        trace_manager = TraceManager()

        start = time.time()

        # 开始追踪
        trace_id = trace_manager.start_trace({})

        # 发现
        registry = SkillRegistry(skills_dir=test_skills_dir)
        registry.discover()

        # 路由和执行
        loader = SkillLoader(registry)
        middleware = SkillMiddleware(registry)
        context = SkillContext(session_path=test_skills_dir, state={})
        result = middleware.execute_skill("grill-me", context, loader)

        # 记录追踪
        span_id = trace_manager.create_span(trace_id, "grill-me")
        trace_manager.end_span(trace_id, span_id, {"success": result.success})

        elapsed = time.time() - start

        print(f"\nE2E with tracing time: {elapsed:.3f}s ({elapsed * 1000:.2f}ms)")

        # 带追踪的完整流程应该 < 2.1s
        assert elapsed < 2.1, f"E2E with tracing took {elapsed:.3f}s, exceeds 2.1s target"
        assert result.success is True


class TestTraceOverhead:
    """追踪开销测试"""

    def test_trace_overhead_ratio(self, test_skills_dir: Path):
        """
        测试追踪开销比例

        Given: 相同的流程
        When: 对比有无可观测性
        Then: 追踪开销 < 5%
        """
        # 无追踪的基准时间
        start = time.time()
        registry = SkillRegistry(skills_dir=test_skills_dir)
        registry.discover()
        loader = SkillLoader(registry)
        middleware = SkillMiddleware(registry)
        context = SkillContext(session_path=test_skills_dir, state={})
        result = middleware.execute_skill("grill-me", context, loader)
        baseline_time = time.time() - start

        # 有追踪的时间
        trace_manager = TraceManager()
        start = time.time()
        trace_id = trace_manager.start_trace({})
        registry2 = SkillRegistry(skills_dir=test_skills_dir)
        registry2.discover()
        loader2 = SkillLoader(registry2)
        middleware2 = SkillMiddleware(registry2)
        result2 = middleware2.execute_skill("grill-me", context, loader2)
        span_id = trace_manager.create_span(trace_id, "grill-me")
        trace_manager.end_span(trace_id, span_id, {"success": result2.success})
        traced_time = time.time() - start

        # 计算开销比例
        if baseline_time > 0:
            overhead_ratio = (traced_time - baseline_time) / baseline_time
            print(f"\nTrace overhead ratio: {overhead_ratio:.1%}")
            print(f"Baseline: {baseline_time:.3f}s, Traced: {traced_time:.3f}s")

            # 追踪开销应该 < 5%（根据规范目标）
            assert overhead_ratio < 0.05, f"Trace overhead {overhead_ratio:.1%} exceeds 5% target"

    def test_trace_manager_performance(self):
        """
        测试 TraceManager 性能

        Given: TraceManager
        When: 创建多个 span
        Then: 创建和结束 span 的开销 < 1ms
        """
        trace_manager = TraceManager()
        trace_id = trace_manager.start_trace({})

        # 测试创建 span 的时间
        start = time.time()
        for i in range(10):
            span_id = trace_manager.create_span(trace_id, f"grill-me-operation-{i}")
            trace_manager.end_span(trace_id, span_id, {"success": True})
        elapsed = (time.time() - start) * 1000

        print(f"\n10 spans creation/end time: {elapsed:.2f}ms (avg {elapsed/10:.2f}ms per span)")

        # 每个 span 平均 < 1ms
        assert elapsed / 10 < 1, f"Span operations took {elapsed/10:.2f}ms per span, exceeds 1ms target"


class TestResponseTimeBaseline:
    """响应时间基准测试"""

    def test_baseline_response_times(self, test_skills_dir: Path):
        """
        基准测试：记录各组件响应时间

        用于性能监控和回归检测
        """
        times = {}

        # Registry 发现
        start = time.time()
        registry = SkillRegistry(skills_dir=test_skills_dir)
        registry.discover()
        times["discovery"] = (time.time() - start) * 1000

        # 加载技能
        loader = SkillLoader(registry)
        start = time.time()
        loader.load_skill("grill-me")
        times["loading"] = (time.time() - start) * 1000

        # 路由
        middleware = SkillMiddleware(registry)
        start = time.time()
        middleware.route({"task_type": "grilling"})
        times["routing"] = (time.time() - start) * 1000

        # 执行
        context = SkillContext(session_path=test_skills_dir, state={})
        start = time.time()
        middleware.execute_skill("grill-me", context, loader)
        times["execution"] = (time.time() - start) * 1000

        print(f"\n=== Response Time Baseline ===")
        for operation, elapsed in times.items():
            print(f"{operation}: {elapsed:.2f}ms")

        # 验证所有操作在合理范围内
        assert times["discovery"] < 100
        assert times["loading"] < 50
        assert times["routing"] < 10
        assert times["execution"] < 100
