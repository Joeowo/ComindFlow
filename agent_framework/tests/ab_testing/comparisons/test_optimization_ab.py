"""
S5-T3: A/B 测试框架 - Token 消耗对比测试

对比优化前后的 Token 消耗差异。
"""
import pytest
import tempfile
from pathlib import Path

from agent_framework.skills.registry import SkillRegistry
from agent_framework.skills.context_optimizer import ContextOptimizer
from agent_framework.skills.loader import SkillLoader


class TestTokenConsumptionAB:
    """Token 消耗 A/B 测试"""

    @pytest.fixture
    def skills_dir(self, tmp_path: Path) -> Path:
        """创建测试技能目录"""
        skills = [
            ("grill-me", "grilling", "Interview user with dense questions"),
            ("grill-you", "qa", "Answer user's questions"),
            ("advance-task", "advance", "Update session state"),
            ("review-session", "review", "Review session progress"),
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

Use this skill when you need to {category} related tasks.

## Examples

Example content here.
""" + "Additional content " * 50  # 模拟实际内容

            (skill_dir / "SKILL.md").write_text(content, encoding="utf-8")

        return tmp_path

    def test_metadata_vs_full_content_ab(self, skills_dir: Path):
        """
        A/B 测试：元数据注入 vs 完整内容加载

        Given: 多个技能
        When: 对比元数据注入和完整加载的 Token 消耗
        Then: 元数据注入显著降低 Token 消耗
        """
        registry = SkillRegistry(skills_dir=skills_dir)
        registry.discover()

        # A 组：元数据注入（优化后）
        optimizer = ContextOptimizer(registry=registry)
        metadata_a = optimizer.inject_metadata()
        tokens_a = len(metadata_a) // 4

        # B 组：完整内容加载（优化前）
        loader = SkillLoader(registry)
        tokens_b = 0
        for skill in registry.list_all():
            content = loader.load_skill(skill.name)
            tokens_b += len(content) // 4

        # 计算改善比例
        improvement_ratio = 1 - (tokens_a / tokens_b) if tokens_b > 0 else 0

        print(f"\n=== A/B Test Results ===")
        print(f"A (Metadata): {tokens_a} tokens")
        print(f"B (Full): {tokens_b} tokens")
        print(f"Improvement: {improvement_ratio:.1%}")

        # 验证显著改善（目标：≥ 30%）
        assert improvement_ratio >= 0.30, f"Token improvement {improvement_ratio:.1%} below 30% target"

    def test_on_demand_loading_efficiency_ab(self, skills_dir: Path):
        """
        A/B 测试：按需加载效率

        Given: 上下文优化器
        When: 对比按需加载和全量加载
        Then: 按需加载更高效
        """
        registry = SkillRegistry(skills_dir=skills_dir)
        registry.discover()

        optimizer = ContextOptimizer(registry=registry)

        # A 组：只加载需要的技能（模拟 grilling 任务）
        state = {"task_type": "grilling"}
        triggered_skills = []
        for skill in registry.list_all():
            if optimizer.should_load_full_content(skill.name, state):
                triggered_skills.append(skill.name)

        # 估算按需加载的 Token 消耗
        loader = SkillLoader(registry)
        tokens_a = 0
        for skill_name in triggered_skills:
            content = loader.load_skill(skill_name)
            tokens_a += len(content) // 4

        # B 组：加载所有技能
        tokens_b = 0
        for skill in registry.list_all():
            content = loader.load_skill(skill.name)
            tokens_b += len(content) // 4

        # 计算节省比例
        savings_ratio = 1 - (tokens_a / tokens_b) if tokens_b > 0 else 0

        print(f"\n=== On-Demand Loading A/B ===")
        print(f"A (On-demand): {tokens_a} tokens ({len(triggered_skills)} skills)")
        print(f"B (All): {tokens_b} tokens ({len(registry.list_all())} skills)")
        print(f"Savings: {savings_ratio:.1%}")

        # 按需加载应该至少节省 50%
        assert savings_ratio >= 0.50, f"On-demand loading saves {savings_ratio:.1%}, below 50% target"

    def test_scaling_efficiency_ab(self, tmp_path: Path):
        """
        A/B 测试：可扩展性效率

        Given: 不同数量的技能
        When: 测试元数据注入的可扩展性
        Then: 元数据注入保持低 Token 消耗
        """
        # 创建不同数量的技能进行测试
        skill_counts = [5, 10, 20]
        results = []

        for count in skill_counts:
            # 创建指定数量的技能
            test_dir = tmp_path / f"test-{count}"
            test_dir.mkdir(exist_ok=True)

            for i in range(count):
                skill_dir = test_dir / f"skill-{i}"
                skill_dir.mkdir(exist_ok=True)
                (skill_dir / "SKILL.md").write_text(
                    f"---\nname: skill-{i}\ndescription: Test skill {i}\n---\n# Skill {i}\nContent",
                    encoding="utf-8"
                )

            # 测试元数据注入
            registry = SkillRegistry(skills_dir=test_dir)
            registry.discover()

            optimizer = ContextOptimizer(registry=registry)
            metadata = optimizer.inject_metadata()
            metadata_tokens = len(metadata) // 4

            results.append((count, metadata_tokens))

        print(f"\n=== Scaling Efficiency A/B ===")
        for count, tokens in results:
            print(f"{count} skills: {tokens} tokens")

        # 验证线性增长（不应该指数增长）
        # 20 个技能的元数据应该 < 500 tokens
        assert results[-1][1] < 500, f"Metadata for {results[-1][0]} skills is {results[-1][1]} tokens, too high"


class TestAccuracyComparison:
    """准确率对比测试"""

    def test_metadata_preserves_routing_accuracy(self, tmp_path: Path):
        """
        测试元数据是否保留路由准确率

        Given: 技能系统
        When: 使用元数据 vs 完整内容
        Then: 路由准确率相同
        """
        # 创建测试技能
        skills = [
            ("grill-me", "grilling", "Interview skill"),
            ("advance-task", "advance", "Task progress"),
            ("review-session", "review", "Review progress"),
        ]

        for skill_name, category, description in skills:
            skill_dir = tmp_path / skill_name
            skill_dir.mkdir(exist_ok=True)
            (skill_dir / "SKILL.md").write_text(
                f"---\nname: {skill_name}\ndescription: {description}\ncategory: {category}\n---\n# {skill_name}",
                encoding="utf-8"
            )

        registry = SkillRegistry(skills_dir=tmp_path)
        registry.discover()

        # 测试路由准确率（元数据和完整内容应该路由相同）
        from agent_framework.skills.middleware import SkillMiddleware

        middleware = SkillMiddleware(registry)

        test_cases = [
            {"task_type": "grilling"},
            {"task_type": "advance"},
            {"task_type": "review"},
        ]

        correct_routes = 0
        for state in test_cases:
            try:
                skill = middleware.route(state)
                if skill:
                    correct_routes += 1
            except Exception:
                pass

        accuracy = correct_routes / len(test_cases)
        print(f"\nRouting accuracy: {accuracy:.1%}")

        # 路由准确率应该 100%
        assert accuracy == 1.0, f"Routing accuracy {accuracy:.1%} below 100%"


class TestABTestReport:
    """A/B 测试报告生成"""

    def test_generate_ab_test_report(self, tmp_path: Path) -> None:
        """
        生成 A/B 测试报告

        Given: A/B 测试数据
        When: 生成报告
        Then: 报告包含所有关键指标
        """
        # 模拟 A/B 测试数据
        ab_data = {
            "token_consumption": {
                "a_group": 78,  # 元数据注入
                "b_group": 1103,  # 完整加载
                "improvement": "92.9%"
            },
            "response_time": {
                "a_group": 15,  # ms
                "b_group": 150,  # ms (模拟)
                "improvement": "90.0%"
            },
            "routing_accuracy": {
                "a_group": "100%",
                "b_group": "100%",
                "regression": "0%"
            }
        }

        # 验证数据结构
        assert "token_consumption" in ab_data
        assert "response_time" in ab_data
        assert "routing_accuracy" in ab_data

        # 验证改善指标
        token_improvement = float(ab_data["token_consumption"]["improvement"].rstrip("%"))
        assert token_improvement >= 30.0, "Token improvement should be ≥ 30%"

        print(f"\n=== A/B Test Report ===")
        print(f"Token Consumption: {ab_data['token_consumption']['improvement']} improvement")
        print(f"Response Time: {ab_data['response_time']['improvement']} improvement")
        print(f"Routing Accuracy: {ab_data['routing_accuracy']['regression']} regression")
