"""
S3-T4: 集成测试 - ContextOptimizer 与其他组件的集成

测试 ContextOptimizer 与 SkillRegistry、SkillLoader 的集成。
"""

import tempfile
from pathlib import Path
import pytest
import shutil

from agent_framework.skills.registry import SkillRegistry
from agent_framework.skills.context_optimizer import ContextOptimizer
from agent_framework.skills.budget_manager import BudgetManager


@pytest.fixture
def temp_skills_dir():
    """创建临时技能目录"""
    temp_dir = Path(tempfile.mkdtemp())

    # 创建测试技能目录和 SKILL.md 文件
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
        skill_dir = temp_dir / skill["name"]
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

    yield temp_dir

    # 清理临时目录
    shutil.rmtree(temp_dir, ignore_errors=True)


class TestContextOptimizerIntegration:
    """ContextOptimizer 集成测试"""

    def test_full_workflow_with_real_registry(self, temp_skills_dir):
        """测试完整的优化器工作流"""
        # 1. 初始化 Registry 并发现技能
        registry = SkillRegistry(skills_dir=temp_skills_dir)
        registry.discover()

        # 验证发现了所有技能
        all_skills = registry.list_all()
        assert len(all_skills) == 3
        skill_names = {s.name for s in all_skills}
        assert skill_names == {"grill-me", "grill-you", "advance-task"}

        # 2. 初始化 ContextOptimizer
        optimizer = ContextOptimizer(registry=registry)

        # 3. 注入元数据
        metadata = optimizer.inject_metadata()
        assert "## Skills Available" in metadata
        assert "grill-me" in metadata
        assert "grill-you" in metadata
        assert "advance-task" in metadata

        # 4. 验证按需加载判断
        state = {"task_type": "grilling"}
        assert optimizer.should_load_full_content("grill-me", state) is True
        assert optimizer.should_load_full_content("grill-you", state) is False

    def test_context_optimizer_with_budget_manager(self, temp_skills_dir):
        """测试 ContextOptimizer 与 BudgetManager 的集成"""
        registry = SkillRegistry(skills_dir=temp_skills_dir)
        registry.discover()

        optimizer = ContextOptimizer(registry=registry)
        budget = BudgetManager(total_budget=8000, metadata_reserve=1000)

        # 注入元数据，检查预算
        metadata = optimizer.inject_metadata()
        estimated_tokens = len(metadata) // 4

        # 元数据应该小于元数据保留预算
        assert estimated_tokens < budget.metadata_reserve

        # 模拟按需加载决策
        state = {"task_type": "grilling"}
        should_load = optimizer.should_load_full_content("grill-me", state)

        if should_load:
            # 检查是否有预算加载
            # 假设技能需要 2000 tokens
            assert budget.can_load("grill-me", 2000) is True

    def test_token_consumption_reduction(self, temp_skills_dir):
        """测试 Token 消耗降低效果"""
        registry = SkillRegistry(skills_dir=temp_skills_dir)
        registry.discover()

        optimizer = ContextOptimizer(registry=registry)

        # 只注入元数据的 Token 消耗
        metadata_only = optimizer.inject_metadata()
        metadata_tokens = len(metadata_only) // 4

        # 如果注入完整内容的估算（假设每个技能 ~2000 tokens）
        full_content_estimate = len(registry.list_all()) * 2000

        # 验证元数据注入显著降低了 Token 消耗
        # 目标：降低 30% 以上
        reduction_ratio = 1 - (metadata_tokens / full_content_estimate)
        assert reduction_ratio >= 0.30, f"Token reduction {reduction_ratio:.1%} below 30% target"

    def test_multiple_skills_loading_scenario(self, temp_skills_dir):
        """测试多技能加载场景"""
        registry = SkillRegistry(skills_dir=temp_skills_dir)
        registry.discover()

        optimizer = ContextOptimizer(registry=registry)
        budget = BudgetManager(total_budget=8000, metadata_reserve=1000)

        # 模拟多个技能被触发
        triggered_skills = ["grill-me", "grill-you"]
        skill_sizes = {"grill-me": 2000, "grill-you": 1500}

        # 检查预算并加载
        for skill_name in triggered_skills:
            skill_size = skill_sizes[skill_name]
            if budget.can_load(skill_name, skill_size):
                budget.record_load(skill_name, skill_size)

        # 验证预算状态
        status = budget.get_status()
        assert status["loaded_skills_count"] == 2
        assert status["available_budget"] == 3500  # 7000 - 2000 - 1500


class TestEdgeCases:
    """边缘情况测试"""

    def test_empty_skills_directory(self):
        """测试空技能目录"""
        temp_dir = Path(tempfile.mkdtemp())
        try:
            registry = SkillRegistry(skills_dir=temp_dir)
            registry.discover()

            optimizer = ContextOptimizer(registry=registry)
            metadata = optimizer.inject_metadata()

            assert "## Skills Available" in metadata
            assert len(registry.list_all()) == 0
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_malformed_skill_files(self, temp_skills_dir):
        """测试包含格式错误的技能目录"""
        # 添加一个格式错误的 SKILL.md
        bad_skill_dir = temp_skills_dir / "bad-skill"
        bad_skill_dir.mkdir(exist_ok=True)
        (bad_skill_dir / "SKILL.md").write_text("This is not valid markdown", encoding="utf-8")

        registry = SkillRegistry(skills_dir=temp_skills_dir)
        registry.discover()

        # 应该跳过格式错误的文件，只加载有效的技能
        all_skills = registry.list_all()
        skill_names = {s.name for s in all_skills}

        # 应该只包含有效的技能
        assert "bad-skill" not in skill_names
        assert "grill-me" in skill_names
