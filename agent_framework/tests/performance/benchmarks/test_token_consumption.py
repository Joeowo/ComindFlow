"""
S5-T2: 性能基准测试 - Token 消耗测试

测试元数据注入和完整加载的 Token 消耗，验证优化效果。
"""
import pytest
import tempfile
from pathlib import Path

from agent_framework.skills.registry import SkillRegistry
from agent_framework.skills.context_optimizer import ContextOptimizer
from agent_framework.skills.budget_manager import BudgetManager


@pytest.fixture
def multi_skill_dir(tmp_path: Path) -> Path:
    """创建多个技能目录用于测试"""
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


class TestTokenConsumption:
    """Token 消耗测试"""

    def test_metadata_injection_token_count(self, multi_skill_dir: Path):
        """
        测试元数据注入的 Token 消耗

        Given: 多个技能
        When: 注入元数据
        Then: Token 消耗在合理范围内
        """
        registry = SkillRegistry(skills_dir=multi_skill_dir)
        registry.discover()

        optimizer = ContextOptimizer(registry=registry)
        metadata = optimizer.inject_metadata()

        # 估算 Token 数（粗略估算：1 Token ≈ 4 字符）
        estimated_tokens = len(metadata) // 4

        # 元数据注入应该控制在 1500 tokens 以内
        assert estimated_tokens < 1500, f"Metadata injection uses {estimated_tokens} tokens, exceeds 1500 limit"

        # 验证元数据包含所有技能
        skill_names = registry.list_all()
        for skill in skill_names:
            assert skill.name in metadata, f"Skill '{skill.name}' not in metadata"

    def test_full_content_token_count(self, multi_skill_dir: Path):
        """
        测试完整内容加载的 Token 消耗

        Given: 多个技能
        When: 加载完整内容
        Then: Token 消耗可测量
        """
        registry = SkillRegistry(skills_dir=multi_skill_dir)
        registry.discover()

        # 加载所有技能的完整内容
        from agent_framework.skills.loader import SkillLoader
        loader = SkillLoader(registry)

        total_tokens = 0
        for skill in registry.list_all():
            content = loader.load_skill(skill.name)
            total_tokens += len(content) // 4  # 粗略估算

        # 完整加载应该消耗更多 tokens
        assert total_tokens > 0, "Full content should consume tokens"

        # 记录基准数据
        print(f"\nFull content loading for {len(registry.list_all())} skills: ~{total_tokens} tokens")

    def test_token_reduction_ratio(self, multi_skill_dir: Path):
        """
        测试 Token 降低比例

        Given: 元数据注入 vs 完整加载
        When: 对比两者
        Then: 元数据注入显著降低 Token 消耗
        """
        registry = SkillRegistry(skills_dir=multi_skill_dir)
        registry.discover()

        optimizer = ContextOptimizer(registry=registry)

        # 元数据注入
        metadata = optimizer.inject_metadata()
        metadata_tokens = len(metadata) // 4

        # 完整加载（估算）
        from agent_framework.skills.loader import SkillLoader
        loader = SkillLoader(registry)

        total_full_tokens = 0
        for skill in registry.list_all():
            content = loader.load_skill(skill.name)
            total_full_tokens += len(content) // 4

        # 计算降低比例
        if total_full_tokens > 0:
            reduction_ratio = 1 - (metadata_tokens / total_full_tokens)
            print(f"\nToken reduction ratio: {reduction_ratio:.1%}")
            print(f"Metadata: {metadata_tokens} tokens, Full: {total_full_tokens} tokens")

            # 元数据注入应该显著降低 Token 消耗
            # 目标：降低 ≥ 30%（根据规范）
            assert reduction_ratio >= 0.30, f"Token reduction {reduction_ratio:.1%} below 30% target"

    def test_budget_manager_token_tracking(self, multi_skill_dir: Path):
        """
        测试预算管理器的 Token 追踪

        Given: 预算管理器
        When: 记录技能加载
        Then: Token 预算正确追踪
        """
        registry = SkillRegistry(skills_dir=multi_skill_dir)
        registry.discover()

        budget = BudgetManager(total_budget=8000, metadata_reserve=1000)

        # 模拟加载技能
        skill_sizes = {"grill-me": 500, "grill-you": 400, "advance-task": 300}

        for skill_name, size in skill_sizes.items():
            if budget.can_load(skill_name, size):
                budget.record_load(skill_name, size)

        # 验证预算状态
        status = budget.get_status()
        assert status["total_budget"] == 8000
        assert status["loaded_skills_count"] == 3
        assert status["available_budget"] == 8000 - 1000 - sum(skill_sizes.values())

    def test_on_demand_loading_token_efficiency(self, multi_skill_dir: Path):
        """
        测试按需加载的 Token 效率

        Given: 上下文优化器
        When: 按需加载技能
        Then: 只加载必要的技能
        """
        registry = SkillRegistry(skills_dir=multi_skill_dir)
        registry.discover()

        optimizer = ContextOptimizer(registry=registry)
        budget = BudgetManager(total_budget=8000, metadata_reserve=1000)

        # 测试场景：只加载 grilling 相关技能
        state = {"task_type": "grilling"}
        should_load = optimizer.should_load_full_content("grill-me", state)

        if should_load:
            # 模拟加载
            skill_size = 500
            if budget.can_load("grill-me", skill_size):
                budget.record_load("grill-me", skill_size)

        # 验证只加载了必要的技能
        status = budget.get_status()
        assert status["loaded_skills_count"] <= 1, "Should only load necessary skills"


class TestTokenConsumptionBaseline:
    """Token 消耗基准测试"""

    def test_baseline_5_skills(self, tmp_path: Path):
        """
        基准测试：5 个技能的 Token 消耗

        记录基准数据用于性能目标设定
        """
        # 创建 5 个标准技能
        for i in range(5):
            skill_dir = tmp_path / f"skill-{i}"
            skill_dir.mkdir(exist_ok=True)
            content = f"""---
name: skill-{i}
description: Test skill {i}
version: 1.0
category: test
tags: [test]
---

# Skill {i}

Content for skill {i}.
""" + "This is test content. " * 20  # 约 200 tokens per skill
            (skill_dir / "SKILL.md").write_text(content, encoding="utf-8")

        registry = SkillRegistry(skills_dir=tmp_path)
        registry.discover()

        # 测试元数据注入
        optimizer = ContextOptimizer(registry=registry)
        metadata = optimizer.inject_metadata()
        metadata_tokens = len(metadata) // 4

        # 测试完整加载
        from agent_framework.skills.loader import SkillLoader
        loader = SkillLoader(registry)

        total_full_tokens = 0
        for skill in registry.list_all():
            content = loader.load_skill(skill.name)
            total_full_tokens += len(content) // 4

        print(f"\n=== Baseline: 5 Skills ===")
        print(f"Metadata injection: {metadata_tokens} tokens")
        print(f"Full content loading: {total_full_tokens} tokens")
        print(f"Reduction ratio: {1 - (metadata_tokens / total_full_tokens):.1%}")

        # 基准数据
        assert metadata_tokens < 1000  # 元数据应该小于 1000 tokens
        assert total_full_tokens > 0  # 完整加载应该消耗 tokens

    def test_baseline_10_skills(self, tmp_path: Path):
        """
        基准测试：10 个技能的 Token 消耗

        记录基准数据用于性能目标设定
        """
        # 创建 10 个标准技能
        for i in range(10):
            skill_dir = tmp_path / f"skill-{i}"
            skill_dir.mkdir(exist_ok=True)
            content = f"""---
name: skill-{i}
description: Test skill {i}
version: 1.0
category: test
tags: [test]
---

# Skill {i}

Content for skill {i}.
""" + "This is test content. " * 20
            (skill_dir / "SKILL.md").write_text(content, encoding="utf-8")

        registry = SkillRegistry(skills_dir=tmp_path)
        registry.discover()

        optimizer = ContextOptimizer(registry=registry)
        metadata = optimizer.inject_metadata()
        metadata_tokens = len(metadata) // 4

        from agent_framework.skills.loader import SkillLoader
        loader = SkillLoader(registry)

        total_full_tokens = 0
        for skill in registry.list_all():
            content = loader.load_skill(skill.name)
            total_full_tokens += len(content) // 4

        print(f"\n=== Baseline: 10 Skills ===")
        print(f"Metadata injection: {metadata_tokens} tokens")
        print(f"Full content loading: {total_full_tokens} tokens")
        print(f"Reduction ratio: {1 - (metadata_tokens / total_full_tokens):.1%}")

        # 验证可扩展性
        assert metadata_tokens < 2000  # 10 个技能的元数据应该小于 2000 tokens


class TestTokenConsumptionEdgeCases:
    """Token 消耗边缘情况测试"""

    def test_empty_skills_directory(self, tmp_path: Path):
        """测试空技能目录的 Token 消耗"""
        registry = SkillRegistry(skills_dir=tmp_path)
        registry.discover()

        optimizer = ContextOptimizer(registry=registry)
        metadata = optimizer.inject_metadata()

        # 空目录应该仍然生成有效的元数据结构
        assert "## Skills Available" in metadata
        assert len(metadata) < 500  # 应该很小

    def test_single_skill(self, tmp_path: Path):
        """测试单个技能的 Token 消耗"""
        skill_dir = tmp_path / "single-skill"
        skill_dir.mkdir(exist_ok=True)
        (skill_dir / "SKILL.md").write_text(
            "---\nname: single-skill\ndescription: Single skill\n---\n# Content",
            encoding="utf-8"
        )

        registry = SkillRegistry(skills_dir=tmp_path)
        registry.discover()

        optimizer = ContextOptimizer(registry=registry)
        metadata = optimizer.inject_metadata()

        metadata_tokens = len(metadata) // 4

        # 单个技能应该消耗很少的 tokens
        assert metadata_tokens < 200
