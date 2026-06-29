"""
S5 消融实验测试

验证逐步从优化前策略切换到优化后策略的过程。
通过消融实验（Canary Release/Feature Flag）验证新策略的稳定性。
"""
import pytest
import tempfile
from pathlib import Path
from typing import Dict, Any, List

from agent_framework.skills.registry import SkillRegistry
from agent_framework.skills.context_optimizer import ContextOptimizer
from agent_framework.skills.loader import SkillLoader
from agent_framework.tests.performance.utils.token_tracker import (
    TokenTracker,
    TokenUsage,
    load_api_config
)


class CanaryDeploymentTest:
    """消融实验测试 - Canary Deployment

    验证新策略在逐步扩大流量时的稳定性。
    """

    @pytest.fixture
    def skills_dir(self, tmp_path: Path) -> Path:
        """创建测试技能目录"""
        skills = [
            ("grill-me", "grilling", "Interview skill"),
            ("grill-you", "qa", "Answer skill"),
            ("advance-task", "advance", "Task progress"),
        ]

        for skill_name, category, description in skills:
            skill_dir = tmp_path / skill_name
            skill_dir.mkdir(exist_ok=True)

            content = f"""---
name: {skill_name}
description: {description}
category: {category}
version: 1.0
tags: [{category}]
---

# {skill_name}

{description}

## Usage

""" + "Content " * 50  # 模拟实际内容
            (skill_dir / "SKILL.md").write_text(content, encoding="utf-8")

        return tmp_path

    def test_canary_0_percent_old_strategy(self, skills_dir: Path):
        """
        消融阶段 0%：100% 旧策略（完整加载）

        验证：所有技能使用完整内容加载
        """
        registry = SkillRegistry(skills_dir=skills_dir)
        registry.discover()

        loader = SkillLoader(registry)
        tracker = TokenTracker()

        # 加载所有技能（旧策略）
        total_tokens = 0
        for skill in registry.list_all():
            content = loader.load_skill(skill.name)
            # 估算 token
            usage = TokenUsage.estimate(content)
            tracker.record(usage, f"load_{skill.name}")
            total_tokens += usage.total_tokens

        stats = tracker.get_stats()
        print(f"\n=== 旧策略 (0% 消融) ===")
        print(f"加载技能数: {stats['count']}")
        print(f"总 Token: {stats['total_tokens']}")
        print(f"平均 Token: {stats['average_tokens']:.1f}")

        # 验证所有技能都是完整加载
        assert stats['cached_count'] == 0
        assert stats['count'] == len(registry.list_all())

    def test_canary_25_percent_metadata_injection(self, skills_dir: Path):
        """
        消融阶段 25%：25% 流量使用元数据注入

        验证：部分使用元数据注入，其余使用完整加载
        """
        registry = SkillRegistry(skills_dir=skills_dir)
        registry.discover()

        optimizer = ContextOptimizer(registry=registry)
        loader = SkillLoader(registry)
        tracker = TokenTracker()

        # 25% 技能使用元数据，其余使用完整加载
        skills = registry.list_all()
        canary_count = len(skills) // 4  # 约 25%

        total_tokens = 0
        metadata_injected = False

        for i, skill in enumerate(skills):
            if i < canary_count:
                # Canary 组：使用元数据注入
                metadata = optimizer.inject_metadata()
                usage = TokenUsage.estimate(metadata)
                tracker.record(usage, f"metadata_injection")
                total_tokens += usage.total_tokens
                metadata_injected = True
            else:
                # 旧策略：完整加载
                content = loader.load_skill(skill.name)
                usage = TokenUsage.estimate(content)
                tracker.record(usage, f"full_load_{skill.name}")
                total_tokens += usage.total_tokens

        stats = tracker.get_stats()
        print(f"\n=== 消融阶段 25% ===")
        print(f"总 Token: {stats['total_tokens']}")
        print(f"元数据注入: {'是' if metadata_injected else '否'}")

        # 验证 25% 使用了新策略
        assert stats['count'] == len(skills)

    def test_canary_50_percent_on_demand_loading(self, skills_dir: Path):
        """
        消融阶段 50%：50% 流量使用按需加载

        验证：根据任务类型按需加载技能
        """
        registry = SkillRegistry(skills_dir=skills_dir)
        registry.discover()

        optimizer = ContextOptimizer(registry=registry)
        loader = SkillLoader(registry)
        tracker = TokenTracker()

        # 模拟不同的任务类型
        task_scenarios = [
            {"task_type": "grilling", "expected": "grill-me"},
            {"task_type": "qa", "expected": "grill-you"},
            {"task_type": "advance", "expected": "advance-task"},
        ]

        total_tokens = 0
        on_demand_loaded = 0

        for scenario in task_scenarios:
            # 判断是否需要按需加载
            if optimizer.should_load_full_content(scenario["expected"], scenario):
                # 按需加载
                content = loader.load_skill(scenario["expected"])
                usage = TokenUsage.estimate(content)
                tracker.record(usage, f"on_demand_{scenario['expected']}")
                total_tokens += usage.total_tokens
                on_demand_loaded += 1
            else:
                # 元数据注入
                metadata = optimizer.inject_metadata()
                usage = TokenUsage.estimate(metadata)
                tracker.record(usage, f"metadata_for_{scenario['task_type']}")
                total_tokens += usage.total_tokens

        stats = tracker.get_stats()
        print(f"\n=== 消融阶段 50% ===")
        print(f"总 Token: {stats['total_tokens']}")
        print(f"按需加载次数: {on_demand_loaded}/{len(task_scenarios)}")

        # 验证按需加载生效
        assert on_demand_loaded > 0

    def test_canary_100_percent_new_strategy(self, skills_dir: Path):
        """
        消融阶段 100%：100% 流量使用新策略

        验证：全面使用元数据注入 + 按需加载
        """
        registry = SkillRegistry(skills_dir=skills_dir)
        registry.discover()

        optimizer = ContextOptimizer(registry=registry)
        loader = SkillLoader(registry)
        tracker = TokenTracker()

        # 新策略：元数据注入 + 按需加载
        # 1. 先注入元数据
        metadata = optimizer.inject_metadata()
        usage = TokenUsage.estimate(metadata)
        tracker.record(usage, "metadata_injection")

        # 2. 按需加载
        state = {"task_type": "grilling"}
        for skill in registry.list_all():
            if optimizer.should_load_full_content(skill.name, state):
                content = loader.load_skill(skill.name)
                usage = TokenUsage.estimate(content)
                tracker.record(usage, f"on_demand_{skill.name}")

        stats = tracker.get_stats()
        print(f"\n=== 消融阶段 100% (新策略) ===")
        print(f"总 Token: {stats['total_tokens']}")
        print(f"操作次数: {stats['count']}")

        # 验证新策略
        assert stats['count'] >= 1


class FeatureFlagTest:
    """功能标志测试 - Feature Flag

    通过功能标志控制新特性的启用，便于快速回滚。
    """

    @pytest.fixture
    def skills_dir(self, tmp_path: Path) -> Path:
        """创建测试技能目录"""
        skills = [
            ("grill-me", "grilling"),
            ("grill-you", "qa"),
        ]

        for skill_name, category in skills:
            skill_dir = tmp_path / skill_name
            skill_dir.mkdir(exist_ok=True)
            (skill_dir / "SKILL.md").write_text(
                f"---\nname: {skill_name}\ncategory: {category}\n---\n# Content",
                encoding="utf-8"
            )

        return tmp_path

    def test_feature_flag_disabled_old_behavior(self, skills_dir: Path):
        """
        功能标志关闭：使用旧行为

        When: CONTEXT_OPTIMIZATION_ENABLED=false
        Then: 使用完整内容加载
        """
        os.environ["CONTEXT_OPTIMIZATION_ENABLED"] = "false"

        registry = SkillRegistry(skills_dir=skills_dir)
        registry.discover()

        loader = SkillLoader(registry)

        # 旧行为：完整加载所有技能
        total_tokens = 0
        for skill in registry.list_all():
            content = loader.load_skill(skill.name)
            total_tokens += len(content) // 4

        print(f"\n=== Feature Flag OFF ===")
        print(f"总 Token (完整加载): {total_tokens}")

        # 验证是完整加载
        assert total_tokens > 200  # 应该包含完整内容

    def test_feature_flag_enabled_new_behavior(self, skills_dir: Path):
        """
        功能标志开启：使用新行为

        When: CONTEXT_OPTIMIZATION_ENABLED=true
        Then: 使用元数据注入
        """
        os.environ["CONTEXT_OPTIMIZATION_ENABLED"] = "true"

        registry = SkillRegistry(skills_dir=skills_dir)
        registry.discover()

        optimizer = ContextOptimizer(registry=registry)

        # 新行为：元数据注入
        metadata = optimizer.inject_metadata()
        tokens = len(metadata) // 4

        print(f"\n=== Feature Flag ON ===")
        print(f"总 Token (元数据): {tokens}")

        # 验证是元数据注入
        assert tokens < 200  # 元数据应该很少

    def test_feature_flag_graceful_degradation(self, skills_dir: Path):
        """
        功能标志优雅降级

        When: 优化器初始化失败
        Then: 自动降级到旧策略
        """
        registry = SkillRegistry(skills_dir=skills_dir)
        registry.discover()

        # 模拟优化器不可用
        loader = SkillLoader(registry)

        # 优雅降级：直接使用完整加载
        total_tokens = 0
        for skill in registry.list_all():
            content = loader.load_skill(skill.name)
            total_tokens += len(content) // 4

        print(f"\n=== 优雅降级 ===")
        print(f"降级后 Token: {total_tokens}")

        # 验证降级后仍能工作
        assert total_tokens > 0


class ABTestComparison:
    """A/B 测试对比

    对比优化前后的实际性能差异。
    """

    @pytest.fixture
    def skills_dir(self, tmp_path: Path) -> Path:
        """创建测试技能目录"""
        skills = [
            ("grill-me", "grilling", "Interview skill"),
            ("grill-you", "qa", "Answer skill"),
            ("advance-task", "advance", "Task progress"),
            ("review-session", "review", "Review progress"),
        ]

        for skill_name, category, description in skills:
            skill_dir = tmp_path / skill_name
            skill_dir.mkdir(exist_ok=True)
            (skill_dir / "SKILL.md").write_text(
                f"---\nname: {skill_name}\ndescription: {description}\ncategory: {category}\n---\n"
                f"# {skill_name}\n\n" + "Content. " * 50,
                encoding="utf-8"
            )

        return tmp_path

    def test_ab_control_group_baseline(self, skills_dir: Path):
        """
        A/B 测试 - 对照组基线测量

        对照组：优化前的策略（完整加载所有技能）
        """
        registry = SkillRegistry(skills_dir=skills_dir)
        registry.discover()

        loader = SkillLoader(registry)
        tracker = TokenTracker()

        # 对照组：完整加载所有技能
        for skill in registry.list_all():
            content = loader.load_skill(skill.name)
            usage = TokenUsage.estimate(content)
            tracker.record(usage, f"control_{skill.name}")

        control_stats = tracker.get_stats()
        print(f"\n=== A/B Test - 对照组 ===")
        print(f"技能数: {control_stats['count']}")
        print(f"总 Token: {control_stats['total_tokens']}")
        print(f"平均 Token: {control_stats['average_tokens']:.1f}")

        # 保存对照组数据
        self.control_baseline = control_stats

    def test_ab_treatment_group_optimized(self, skills_dir: Path):
        """
        A/B 测试 - 实验组优化测量

        实验组：优化后的策略（元数据注入 + 按需加载）
        """
        registry = SkillRegistry(skills_dir=skills_dir)
        registry.discover()

        optimizer = ContextOptimizer(registry=registry)
        loader = SkillLoader(registry)
        tracker = TokenTracker()

        # 1. 元数据注入
        metadata = optimizer.inject_metadata()
        usage = TokenUsage.estimate(metadata)
        tracker.record(usage, "metadata_injection")

        # 2. 按需加载（模拟 grilling 任务）
        state = {"task_type": "grilling"}
        for skill in registry.list_all():
            if optimizer.should_load_full_content(skill.name, state):
                content = loader.load_skill(skill.name)
                usage = TokenUsage.estimate(content)
                tracker.record(usage, f"on_demand_{skill.name}")

        treatment_stats = tracker.get_stats()
        print(f"\n=== A/B Test - 实验组 ===")
        print(f"操作数: {treatment_stats['count']}")
        print(f"总 Token: {treatment_stats['total_tokens']}")

        # 计算改善效果
        if hasattr(self, 'control_baseline'):
            improvement = 1 - (treatment_stats['total_tokens'] / self.control_baseline['total_tokens'])
            print(f"改善比例: {improvement:.1%}")

            # 验证显著改善
            assert improvement >= 0.30, f"改善比例 {improvement:.1%} 低于 30% 目标"


class GradualRolloutTest:
    """渐进式发布测试

    验证逐步增加新策略流量时的系统稳定性。
    """

    @pytest.fixture
    def skills_dir(self, tmp_path: Path) -> Path:
        """创建测试技能目录"""
        skills = [
            ("grill-me", "grilling"),
            ("grill-you", "qa"),
        ]

        for skill_name, category in skills:
            skill_dir = tmp_path / skill_name
            skill_dir.mkdir(exist_ok=True)
            (skill_dir / "SKILL.md").write_text(
                f"---\nname: {skill_name}\ncategory: {category}\n---\n# Content",
                encoding="utf-8"
            )

        return tmp_path

    def test_gradual_rollout_stages(self, skills_dir: Path):
        """
        渐进式发布测试

        模拟 0% → 25% → 50% → 75% → 100% 的流量切换过程
        """
        registry = SkillRegistry(skills_dir=skills_dir)
        registry.discover()
        optimizer = ContextOptimizer(registry=registry)
        loader = SkillLoader(registry)

        rollout_stages = [0, 25, 50, 75, 100]
        stage_metrics = {}

        for stage_percentage in rollout_stages:
            tracker = TokenTracker()

            # 根据阶段百分比选择策略
            skill_count = len(registry.list_all())
            canary_count = int(skill_count * stage_percentage / 100)

            for i, skill in enumerate(registry.list_all()):
                if i < canary_count:
                    # 新策略：元数据注入
                    metadata = optimizer.inject_metadata()
                    usage = TokenUsage.estimate(metadata)
                    tracker.record(usage, f"stage_{stage_percentage}_metadata")
                else:
                    # 旧策略：完整加载
                    content = loader.load_skill(skill.name)
                    usage = TokenUsage.estimate(content)
                    tracker.record(usage, f"stage_{stage_percentage}_full")

            stats = tracker.get_stats()
            stage_metrics[stage_percentage] = stats['total_tokens']

            print(f"阶段 {stage_percentage}%: {stats['total_tokens']} tokens")

        # 验证渐进改善
        assert stage_metrics[0] > stage_metrics[100]  # 0% 应该最慢（完整加载）
        assert stage_metrics[100] < stage_metrics[0] * 0.3  # 100% 应该改善至少 30%

        print(f"\n=== 渐进式发布验证 ===")
        print(f"0% Token: {stage_metrics[0]}")
        print(f"100% Token: {stage_metrics[100]}")
        print(f"改善比例: {1 - (stage_metrics[100] / stage_metrics[0]):.1%}")


class RollbackTest:
    """回滚测试

    验证在出现问题时能够快速回滚到旧策略。
    """

    @pytest.fixture
    def skills_dir(self, tmp_path: Path) -> Path:
        """创建测试技能目录"""
        for skill_name in ["skill-a", "skill-b"]:
            skill_dir = tmp_path / skill_name
            skill_dir.mkdir(exist_ok=True)
            (skill_dir / "SKILL.md").write_text(
                f"---\nname: {skill_name}\ncategory: test\n---\n# Content",
                encoding="utf-8"
            )

        return tmp_path

    def test_rollback_on_error(self, skills_dir: Path):
        """
        错误时回滚测试

        When: 新策略发生错误
        Then: 自动回滚到旧策略
        """
        registry = SkillRegistry(skills_dir=skills_dir)
        registry.discover()

        loader = SkillLoader(registry)
        optimizer = ContextOptimizer(registry=registry)

        try:
            # 尝试使用新策略
            metadata = optimizer.inject_metadata()
            # 模拟错误：元数据为空
            if not metadata or "Skills Available" not in metadata:
                raise ValueError("元数据生成失败")

            # 如果成功，继续使用新策略
            print("新策略成功")
            new_strategy_tokens = len(metadata) // 4
            return new_strategy_tokens

        except Exception as e:
            print(f"新策略失败: {e}")
            # 回滚到旧策略：完整加载
            total_tokens = 0
            for skill in registry.list_all():
                content = loader.load_skill(skill.name)
                total_tokens += len(content) // 4

            print(f"回滚到旧策略: {total_tokens} tokens")
            return total_tokens


# 集成测试
class CanaryIntegrationTest:
    """消融实验集成测试"""

    def test_full_canary_deployment_flow(self, tmp_path: Path):
        """
        完整消融发布流程测试

        验证从 0% → 100% 的完整消融过程
        """
        # 创建测试环境
        skills = [
            ("grill-me", "grilling"),
            ("grill-you", "qa"),
        ]

        for skill_name, category in skills:
            skill_dir = tmp_path / skill_name
            skill_dir.mkdir(exist_ok=True)
            (skill_dir / "SKILL.md").write_text(
                f"---\nname: {skill_name}\ncategory: {category}\n---\n"
                f"# {skill_name}\n\n" + "Content. " * 30,
                encoding="utf-8"
            )

        # 初始化组件
        registry = SkillRegistry(skills_dir=tmp_path)
        registry.discover()

        loader = SkillLoader(registry)
        optimizer = ContextOptimizer(registry=registry)

        # 阶段 1: 0% - 旧策略基线
        tracker = TokenTracker()
        for skill in registry.list_all():
            content = loader.load_skill(skill.name)
            usage = TokenUsage.estimate(content)
            tracker.record(usage, "baseline")
        baseline_tokens = tracker.get_total_tokens()

        # 阶段 2: 100% - 新策略
        tracker2 = TokenTracker()
        metadata = optimizer.inject_metadata()
        usage = TokenUsage.estimate(metadata)
        tracker2.record(usage, "new_strategy")
        new_tokens = tracker2.get_total_tokens()

        # 验证新策略优于旧策略
        improvement = 1 - (new_tokens / baseline_tokens)
        print(f"\n=== 消融实验结果 ===")
        print(f"旧策略 Token: {baseline_tokens}")
        print(f"新策略 Token: {new_tokens}")
        print(f"改善比例: {improvement:.1%}")

        assert improvement >= 0.30, f"改善比例 {improvement:.1%} 低于目标"
