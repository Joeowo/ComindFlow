"""
S3-T1: ContextOptimizer 单元测试

测试上下文优化器的元数据注入和按需加载功能。
"""

from pathlib import Path
import pytest
from agent_framework.skills.models.metadata import SkillMetadata
from agent_framework.skills.registry import SkillRegistry


@pytest.fixture
def mock_registry():
    """创建一个用于测试的 Mock Registry"""
    registry = SkillRegistry(skills_dir=Path("/tmp/test_skills"))

    # 添加几个测试技能
    registry.register(SkillMetadata(
        name="grill-me",
        description="Interview user with dense questions",
        path=Path("/tmp/skills/grill-me/SKILL.md"),
        version="1.0",
        category="grilling",
        tags=["qa", "interview"]
    ))

    registry.register(SkillMetadata(
        name="grill-you",
        description="Answer user's questions",
        path=Path("/tmp/skills/grill-you/SKILL.md"),
        version="1.0",
        category="qa",
        tags=["answer", "help"]
    ))

    return registry


class TestContextOptimizerMetadataInjection:
    """元数据注入功能测试"""

    def test_metadata_injection_contains_all_skills(self, mock_registry):
        """测试元数据注入包含所有已注册的技能"""
        from agent_framework.skills.context_optimizer import ContextOptimizer

        optimizer = ContextOptimizer(registry=mock_registry)
        result = optimizer.inject_metadata()

        # 验证包含所有技能名称
        assert "grill-me" in result
        assert "grill-you" in result

        # 验证包含描述
        assert "Interview user with dense questions" in result
        assert "Answer user's questions" in result

    def test_metadata_injection_token_estimate_under_limit(self, mock_registry):
        """测试元数据注入预估 Token 数小于 1500"""
        from agent_framework.skills.context_optimizer import ContextOptimizer

        optimizer = ContextOptimizer(registry=mock_registry)
        result = optimizer.inject_metadata()

        # 粗略预估：1 Token ≈ 4 字符
        estimated_tokens = len(result) // 4
        assert estimated_tokens < 1500, f"Token estimate {estimated_tokens} exceeds limit 1500"

    def test_metadata_injection_empty_registry(self):
        """测试空注册表的元数据注入"""
        from agent_framework.skills.context_optimizer import ContextOptimizer

        empty_registry = SkillRegistry(skills_dir=Path("/tmp/empty_skills"))
        optimizer = ContextOptimizer(registry=empty_registry)
        result = optimizer.inject_metadata()

        # 应该只包含标题，没有技能信息
        assert "## Skills Available" in result
        assert "###" not in result  # 没有技能条目

    def test_metadata_injection_format(self, mock_registry):
        """测试元数据注入格式正确"""
        from agent_framework.skills.context_optimizer import ContextOptimizer

        optimizer = ContextOptimizer(registry=mock_registry)
        result = optimizer.inject_metadata()

        # 验证格式：标题、技能条目结构
        assert result.startswith("## Skills Available")
        assert "\n### grill-me" in result
        assert "\n### grill-you" in result

    def test_metadata_injection_with_tags(self, mock_registry):
        """测试元数据注入包含标签"""
        from agent_framework.skills.context_optimizer import ContextOptimizer

        optimizer = ContextOptimizer(registry=mock_registry)
        result = optimizer.inject_metadata()

        # 验证标签正确显示
        assert "**Tags:** qa, interview" in result
        assert "**Tags:** answer, help" in result


class TestContextOptimizerOnDemandLoading:
    """按需加载功能测试"""

    def test_should_load_by_task_type(self, mock_registry):
        """测试基于任务类型触发加载"""
        from agent_framework.skills.context_optimizer import ContextOptimizer

        optimizer = ContextOptimizer(registry=mock_registry)
        state = {"task_type": "grilling"}

        # grill-me 的 category 是 grilling，应该触发加载
        assert optimizer.should_load_full_content("grill-me", state) is True

        # grill-you 的 category 是 qa，不应该触发加载
        assert optimizer.should_load_full_content("grill-you", state) is False

    def test_should_load_by_user_query_tags(self, mock_registry):
        """测试基于用户查询包含标签触发加载"""
        from agent_framework.skills.context_optimizer import ContextOptimizer

        optimizer = ContextOptimizer(registry=mock_registry)
        state = {"user_query": "I need help with interview preparation"}

        # 用户查询包含 "interview" 标签，应该触发加载 grill-me
        assert optimizer.should_load_full_content("grill-me", state) is True

        # 用户查询包含 "help" 标签，应该触发加载 grill-you
        assert optimizer.should_load_full_content("grill-you", state) is True

    def test_should_load_by_pending_skill_calls(self, mock_registry):
        """测试基于待处理技能调用触发加载"""
        from agent_framework.skills.context_optimizer import ContextOptimizer

        optimizer = ContextOptimizer(registry=mock_registry)
        state = {"pending_skill_calls": ["grill-me"]}

        # grill-me 在待处理列表中，应该触发加载
        assert optimizer.should_load_full_content("grill-me", state) is True

        # grill-you 不在待处理列表中，不应该触发加载
        assert optimizer.should_load_full_content("grill-you", state) is False

    def test_should_load_nonexistent_skill(self, mock_registry):
        """测试不存在的技能不触发加载"""
        from agent_framework.skills.context_optimizer import ContextOptimizer

        optimizer = ContextOptimizer(registry=mock_registry)
        state = {"task_type": "grilling"}

        # 不存在的技能不应该触发加载
        assert optimizer.should_load_full_content("nonexistent-skill", state) is False

    def test_should_load_empty_state(self, mock_registry):
        """测试空状态不触发加载"""
        from agent_framework.skills.context_optimizer import ContextOptimizer

        optimizer = ContextOptimizer(registry=mock_registry)
        state = {}

        # 空状态不应该触发任何加载
        assert optimizer.should_load_full_content("grill-me", state) is False
        assert optimizer.should_load_full_content("grill-you", state) is False
