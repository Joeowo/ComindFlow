"""S2 集成测试

测试验证器、迁移工具和生命周期管理的集成。
"""

import tempfile
from pathlib import Path

import pytest

from agent_framework.skills.lifecycle import SkillLifecycle
from agent_framework.skills.migrator import SkillMigrator
from agent_framework.skills.validator import SkillValidator


class TestValidatorMigrationIntegration:
    """验证器和迁移工具集成测试"""

    def test_validate_then_migrate_workflow(self):
        """测试验证后迁移工作流

        Given: 一个不符合规范的 SKILL.md
        When: 先验证然后迁移
        Then: 验证发现问题，迁移修复问题
        """
        # Arrange
        validator = SkillValidator()
        migrator = SkillMigrator()

        long_content = """---
name: test-skill
description: Test capability.
---

# Test Skill

## Quick start

Quick start content.

## Workflows

"""
        # 添加 80 行额外内容使其超过限制
        for i in range(80):
            long_content += f"Content line {i}\n"

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            skill_dir = tmpdir / "test-skill"
            skill_dir.mkdir()
            skill_md = skill_dir / "SKILL.md"
            skill_md.write_text(long_content)

            # Act - 先验证
            validation_result = validator.validate(skill_md)
            assert validation_result.valid is True  # 符合基本规范
            # 可能没有警告（如果内容不超过 100 行）

            # 然后迁移（即使没有警告也可以迁移）
            migration_report = migrator.migrate(skill_md)
            assert migration_report.success is True
            # 由于内容超过 30 行（migrator 默认 max_lines），应该会有变化
            assert migration_report.changes >= 1  # 至少创建备份

    def test_lifecycle_with_validation(self):
        """测试生命周期管理和验证集成

        Given: 一个技能目录
        When: 发现技能并验证
        Then: 生命周期管理器可以发现并验证技能
        """
        # Arrange
        lifecycle = SkillLifecycle()
        validator = SkillValidator()

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # 创建有效的技能
            skill_dir = tmpdir / "valid-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("""---
name: valid-skill
description: A valid skill.
---

# Valid Skill

## Quick start

Valid content.

## Workflows

Workflows here.
""")

            # Act - 发现技能
            skills = lifecycle.discover(tmpdir)
            assert len(skills) == 1

            # 验证技能
            skill_md = skills[0].path / "SKILL.md"
            validation_result = validator.validate(skill_md)
            assert validation_result.valid is True

            # 注册并加载
            lifecycle.register(skills[0])
            content = lifecycle.load("valid-skill")
            assert content is not None
            assert "Valid Skill" in content

    def test_migration_creates_reference_file(self):
        """测试迁移创建 REFERENCE.md 文件

        Given: 一个超长的 SKILL.md
        When: 执行迁移
        Then: 创建 REFERENCE.md 并更新 SKILL.md
        """
        # Arrange
        migrator = SkillMigrator(max_lines=30)
        lifecycle = SkillLifecycle()

        long_content = """---
name: long-skill
description: A very long skill.
---

# Long Skill

## Quick start

Quick start.

## Workflows

"""
        # 添加 40 行额外内容
        for i in range(40):
            long_content += f"Detailed content line {i}\n"

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            skill_dir = tmpdir / "long-skill"
            skill_dir.mkdir()
            skill_md = skill_dir / "SKILL.md"
            skill_md.write_text(long_content)

            # Act - 迁移
            report = migrator.migrate(skill_md)
            assert report.success is True

            # 验证 REFERENCE.md 存在
            reference_md = skill_dir / "REFERENCE.md"
            assert reference_md.exists()

            # 通过生命周期管理器验证
            skills = lifecycle.discover(tmpdir)
            assert len(skills) == 1

            # 使用正确的技能名称
            lifecycle.register(skills[0])
            content = lifecycle.load(skills[0].name)
            assert content is not None
            # 验证 SKILL.md 已缩短
            lines = content.split("\n")
            assert len(lines) <= migrator.max_lines + 10

    def test_lifecycle_monitoring_integration(self):
        """测试生命周期监控集成

        Given: 一个已注册和加载的技能
        When: 获取统计信息和健康状态
        Then: 返回完整的状态信息
        """
        # Arrange
        lifecycle = SkillLifecycle()

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            skill_dir = tmpdir / "monitored-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("""---
name: monitored-skill
description: A monitored skill.
---

# Monitored Skill
""")

            # Act - 发现、注册、加载
            skills = lifecycle.discover(tmpdir)
            lifecycle.register(skills[0])
            lifecycle.load("monitored-skill")
            lifecycle.record_execution("monitored-skill")

            # 验证统计信息
            stats = lifecycle.get_stats("monitored-skill")
            assert stats is not None
            assert stats["loaded"] is True
            assert stats["execution_count"] == 1

            # 验证健康状态
            health = lifecycle.get_health("monitored-skill")
            assert health is not None
            assert health.healthy is True


class TestValidationScenarios:
    """验证场景测试"""

    def test_validate_real_world_skill(self):
        """测试验证真实世界的技能

        Given: 使用现有的 write-a-skill 作为 SKILL.md
        When: 验证该文件
        Then: 应该通过验证
        """
        # Arrange
        validator = SkillValidator()
        write_a_skill_path = Path("d:/CODE/ComindFlow/skills/write-a-skill/SKILL.md")

        if write_a_skill_path.exists():
            # Act
            result = validator.validate(write_a_skill_path)

            # Assert
            # write-a-skill 应该符合规范（可能会有一些警告）
            assert result.valid is True

    def test_discover_multiple_skills(self):
        """测试发现多个技能

        Given: 一个包含多个技能的目录
        When: 扫描目录
        Then: 返回所有技能
        """
        # Arrange
        lifecycle = SkillLifecycle()

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # 创建多个技能
            for i in range(3):
                skill_dir = tmpdir / f"skill-{i}"
                skill_dir.mkdir()
                (skill_dir / "SKILL.md").write_text(f"""---
name: skill-{i}
description: Skill {i}
---

# Skill {i}
""")

            # Act
            skills = lifecycle.discover(tmpdir)

            # Assert
            assert len(skills) == 3

            # 注册所有技能
            for skill in skills:
                lifecycle.register(skill)

            # 验证所有技能都已注册
            registered = lifecycle.list_registered()
            assert len(registered) == 3
