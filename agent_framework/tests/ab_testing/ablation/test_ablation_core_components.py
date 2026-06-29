"""
S5-EXT: 消融实验 - 核心优化组件

测试 ContextOptimizer、BudgetManager 等核心优化组件的独立贡献。
通过逐个禁用组件，量化每个组件对 Token 节省的影响。
"""
import pytest
import tempfile
from pathlib import Path
from typing import Dict, Any
from dataclasses import dataclass, field

from agent_framework.skills.registry import SkillRegistry
from agent_framework.skills.context_optimizer import ContextOptimizer
from agent_framework.skills.budget_manager import BudgetManager
from agent_framework.skills.loader import SkillLoader
from agent_framework.tests.performance.utils.token_tracker import (
    TokenTracker,
    TokenUsage,
    get_usage_stats,
    record_estimated_usage
)


@dataclass
class AblationResult:
    """消融实验结果"""
    component_name: str
    enabled_tokens: int
    disabled_tokens: int
    savings: int
    savings_ratio: float
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "component": self.component_name,
            "enabled_tokens": self.enabled_tokens,
            "disabled_tokens": self.disabled_tokens,
            "savings": self.savings,
            "savings_ratio": f"{self.savings_ratio:.1%}",
            "description": self.description
        }


class AblationTestRunner:
    """消融实验运行器"""

    def __init__(self):
        self.results: list[AblationResult] = []
        self.token_tracker = TokenTracker()

    def run_ablation_test(
        self,
        component_name: str,
        setup_with_component,
        setup_without_component,
        description: str = ""
    ) -> AblationResult:
        """运行单个消融测试"""
        # 测试启用组件
        with_component_tokens = setup_with_component()

        # 测试禁用组件
        without_component_tokens = setup_without_component()

        # 计算节省
        savings = without_component_tokens - with_component_tokens
        savings_ratio = savings / without_component_tokens if without_component_tokens > 0 else 0

        result = AblationResult(
            component_name=component_name,
            enabled_tokens=with_component_tokens,
            disabled_tokens=without_component_tokens,
            savings=savings,
            savings_ratio=savings_ratio,
            description=description
        )

        self.results.append(result)
        return result

    def get_report(self) -> str:
        """生成消融实验报告"""
        if not self.results:
            return "No ablation results available."

        lines = [
            "\n" + "=" * 70,
            "消融实验报告 (Ablation Study Report)",
            "=" * 70,
            ""
        ]

        total_savings = 0
        for result in self.results:
            total_savings += result.savings
            lines.extend([
                f"组件: {result.component_name}",
                f"  描述: {result.description}",
                f"  启用时 tokens: {result.enabled_tokens}",
                f"  禁用时 tokens: {result.disabled_tokens}",
                f"  节省: {result.savings} tokens ({result.savings_ratio:.1%})",
                ""
            ])

        lines.extend([
            "-" * 70,
            f"总节省: {total_savings} tokens",
            "=" * 70
        ])

        return "\n".join(lines)


@pytest.fixture
def ablation_runner():
    """消融实验运行器 fixture"""
    return AblationTestRunner()


@pytest.fixture
def multi_skill_dir(tmp_path: Path) -> Path:
    """创建多个技能目录用于消融测试"""
    skills = [
        {
            "name": "grill-me",
            "description": "Interview user with dense questions",
            "category": "grilling",
            "content": "# Grill-Me\n\n" + "Question content " * 50
        },
        {
            "name": "grill-you",
            "description": "Answer user's questions",
            "category": "qa",
            "content": "# Grill-You\n\n" + "Answer content " * 50
        },
        {
            "name": "advance-task",
            "description": "Update session state",
            "category": "session",
            "content": "# Advance-Task\n\n" + "Task content " * 50
        },
        {
            "name": "review-session",
            "description": "Review session progress",
            "category": "review",
            "content": "# Review-Session\n\n" + "Review content " * 50
        },
        {
            "name": "handoff",
            "description": "Handoff between sessions",
            "category": "session",
            "content": "# Handoff\n\n" + "Handoff content " * 50
        }
    ]

    for skill in skills:
        skill_dir = tmp_path / skill["name"]
        skill_dir.mkdir(exist_ok=True)

        frontmatter = f"""---
name: {skill['name']}
description: {skill['description']}
version: 1.0
category: {skill['category']}
tags: [{skill['category']}]
---

"""
        (skill_dir / "SKILL.md").write_text(frontmatter + skill["content"], encoding="utf-8")

    return tmp_path


class TestContextOptimizerAblation:
    """ContextOptimizer 消融测试"""

    def test_metadata_injection_ablation(
        self,
        multi_skill_dir: Path,
        ablation_runner: AblationTestRunner
    ):
        """
        消融测试：元数据注入功能

        Given: 多个技能
        When: 对比启用/禁用元数据注入
        Then: 量化元数据注入的 token 节省
        """
        registry = SkillRegistry(skills_dir=multi_skill_dir)
        registry.discover()

        def with_optimizer():
            """启用 ContextOptimizer：只注入元数据"""
            optimizer = ContextOptimizer(registry=registry)
            metadata = optimizer.inject_metadata()
            return len(metadata) // 4  # 估算 tokens

        def without_optimizer():
            """禁用 ContextOptimizer：加载完整内容"""
            from agent_framework.skills.loader import SkillLoader
            loader = SkillLoader(registry)

            total_tokens = 0
            for skill in registry.list_all():
                content = loader.load_skill(skill.name)
                total_tokens += len(content) // 4

            return total_tokens

        result = ablation_runner.run_ablation_test(
            component_name="ContextOptimizer (元数据注入)",
            setup_with_component=with_optimizer,
            setup_without_component=without_optimizer,
            description="通过只注入 YAML frontmatter 和目录，而不是完整内容"
        )

        # 验证元数据注入确实节省了 tokens
        assert result.savings > 0, "元数据注入应该节省 tokens"
        assert result.savings_ratio > 0.5, f"元数据注入节省比例应该 > 50%, 实际: {result.savings_ratio:.1%}"

        print(f"\n{result.to_dict()}")

    def test_on_demand_loading_ablation(
        self,
        multi_skill_dir: Path,
        ablation_runner: AblationTestRunner
    ):
        """
        消融测试：按需加载功能

        Given: 多个技能和特定任务类型
        When: 对比按需加载 vs 全量加载
        Then: 量化按需加载的 token 节省
        """
        registry = SkillRegistry(skills_dir=multi_skill_dir)
        registry.discover()

        from agent_framework.skills.loader import SkillLoader
        loader = SkillLoader(registry)

        def with_on_demand():
            """启用按需加载：只加载 grilling 相关技能"""
            optimizer = ContextOptimizer(registry=registry)
            state = {"task_type": "grilling"}

            # 元数据注入
            metadata_tokens = len(optimizer.inject_metadata()) // 4

            # 按需加载
            loaded_tokens = 0
            for skill in registry.list_all():
                if optimizer.should_load_full_content(skill.name, state):
                    content = loader.load_skill(skill.name)
                    loaded_tokens += len(content) // 4

            return metadata_tokens + loaded_tokens

        def without_on_demand():
            """禁用按需加载：加载所有技能"""
            optimizer = ContextOptimizer(registry=registry)

            # 元数据注入
            metadata_tokens = len(optimizer.inject_metadata()) // 4

            # 加载所有技能
            total_tokens = 0
            for skill in registry.list_all():
                content = loader.load_skill(skill.name)
                total_tokens += len(content) // 4

            return metadata_tokens + total_tokens

        result = ablation_runner.run_ablation_test(
            component_name="按需加载 (On-Demand Loading)",
            setup_with_component=with_on_demand,
            setup_without_component=without_on_demand,
            description="根据任务类型只加载相关技能，而不是加载所有技能"
        )

        # 验证按需加载确实节省了 tokens
        assert result.savings >= 0, "按需加载应该节省或持平 tokens"

        print(f"\n{result.to_dict()}")


class TestBudgetManagerAblation:
    """BudgetManager 消融测试"""

    def test_budget_enforcement_ablation(
        self,
        multi_skill_dir: Path,
        ablation_runner: AblationTestRunner
    ):
        """
        消融测试：预算管理器的强制执行

        Given: 固定预算
        When: 对比启用/禁用预算管理
        Then: 量化预算管理的影响
        """
        registry = SkillRegistry(skills_dir=multi_skill_dir)
        registry.discover()

        from agent_framework.skills.loader import SkillLoader
        loader = SkillLoader(registry)

        total_budget = 2000
        metadata_reserve = 500

        def with_budget_manager():
            """启用预算管理：严格限制加载"""
            budget = BudgetManager(
                total_budget=total_budget,
                metadata_reserve=metadata_reserve
            )

            loaded_tokens = 0
            for skill in registry.list_all():
                # 估算技能大小
                content = loader.load_skill(skill.name)
                skill_size = len(content) // 4

                if budget.can_load(skill.name, skill_size):
                    budget.record_load(skill.name, skill_size)
                    loaded_tokens += skill_size

            return loaded_tokens

        def without_budget_manager():
            """禁用预算管理：加载所有技能"""
            total_tokens = 0
            for skill in registry.list_all():
                content = loader.load_skill(skill.name)
                total_tokens += len(content) // 4

            return total_tokens

        result = ablation_runner.run_ablation_test(
            component_name="BudgetManager (预算管理)",
            setup_with_component=with_budget_manager,
            setup_without_component=without_budget_manager,
            description=f"通过 LRU 驱逐策略控制加载，总预算 {total_budget} tokens"
        )

        # 预算管理应该限制加载
        assert result.enabled_tokens <= total_budget - metadata_reserve

        print(f"\n{result.to_dict()}")


class TestCombinedOptimizationAblation:
    """组合优化消融测试"""

    def test_full_optimization_stack_ablation(
        self,
        multi_skill_dir: Path,
        ablation_runner: AblationTestRunner
    ):
        """
        消融测试：完整优化堆栈

        Given: 所有优化组件
        When: 逐步禁用组件
        Then: 量化每个组件的独立贡献
        """
        registry = SkillRegistry(skills_dir=multi_skill_dir)
        registry.discover()

        from agent_framework.skills.loader import SkillLoader
        loader = SkillLoader(registry)

        def baseline_full_content():
            """基线：加载所有完整内容（无优化）"""
            total_tokens = 0
            for skill in registry.list_all():
                content = loader.load_skill(skill.name)
                total_tokens += len(content) // 4
            return total_tokens

        def with_metadata_only():
            """仅元数据注入"""
            optimizer = ContextOptimizer(registry=registry)
            return len(optimizer.inject_metadata()) // 4

        def with_metadata_and_on_demand():
            """元数据注入 + 按需加载（grilling 任务）"""
            optimizer = ContextOptimizer(registry=registry)
            state = {"task_type": "grilling"}

            metadata_tokens = len(optimizer.inject_metadata()) // 4

            loaded_tokens = 0
            for skill in registry.list_all():
                if optimizer.should_load_full_content(skill.name, state):
                    content = loader.load_skill(skill.name)
                    loaded_tokens += len(content) // 4

            return metadata_tokens + loaded_tokens

        def with_all_optimizations():
            """所有优化：元数据 + 按需加载 + 预算管理"""
            optimizer = ContextOptimizer(registry=registry)
            budget = BudgetManager(total_budget=2000, metadata_reserve=500)
            state = {"task_type": "grilling"}

            metadata_tokens = len(optimizer.inject_metadata()) // 4

            loaded_tokens = 0
            for skill in registry.list_all():
                if optimizer.should_load_full_content(skill.name, state):
                    content = loader.load_skill(skill.name)
                    skill_size = len(content) // 4

                    if budget.can_load(skill.name, skill_size):
                        budget.record_load(skill.name, skill_size)
                        loaded_tokens += skill_size

            return metadata_tokens + loaded_tokens

        # 获取各层级的 token 消耗
        baseline = baseline_full_content()
        metadata_only = with_metadata_only()
        metadata_on_demand = with_metadata_and_on_demand()
        all_optimizations = with_all_optimizations()

        print(f"\n=== 完整优化堆栈消融实验 ===")
        print(f"基线（无优化）: {baseline} tokens")
        print(f"仅元数据注入: {metadata_only} tokens (节省 {baseline - metadata_only}, {(1 - metadata_only/baseline):.1%})")
        print(f"元数据 + 按需加载: {metadata_on_demand} tokens (节省 {baseline - metadata_on_demand}, {(1 - metadata_on_demand/baseline):.1%})")
        print(f"所有优化: {all_optimizations} tokens (节省 {baseline - all_optimizations}, {(1 - all_optimizations/baseline):.1%})")

        # 验证优化层层递进
        assert metadata_only < baseline, "元数据注入应该降低消耗"
        assert metadata_on_demand < baseline, "元数据+按需加载应该降低消耗"
        assert all_optimizations < baseline, "所有优化应该降低消耗"

        # 验证完整优化达到目标
        total_reduction_ratio = 1 - (all_optimizations / baseline)
        assert total_reduction_ratio >= 0.30, f"总优化比例应该 ≥ 30%, 实际: {total_reduction_ratio:.1%}"


class TestAblationReport:
    """消融实验报告测试"""

    def test_generate_ablation_report(
        self,
        multi_skill_dir: Path,
        ablation_runner: AblationTestRunner
    ):
        """
        生成完整的消融实验报告

        Given: 运行所有消融测试
        When: 生成报告
        Then: 报告包含所有关键信息
        """
        registry = SkillRegistry(skills_dir=multi_skill_dir)
        registry.discover()

        # 运行消融测试
        ablation_runner.run_ablation_test(
            "ContextOptimizer",
            lambda: 100,
            lambda: 1000,
            "元数据注入"
        )

        ablation_runner.run_ablation_test(
            "BudgetManager",
            lambda: 500,
            lambda: 1000,
            "预算管理"
        )

        # 生成报告
        report = ablation_runner.get_report()

        # 验证报告内容
        assert "消融实验报告" in report
        assert "ContextOptimizer" in report
        assert "BudgetManager" in report
        assert "总节省" in report

        print(report)
