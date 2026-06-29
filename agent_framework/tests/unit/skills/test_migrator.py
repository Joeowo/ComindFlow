"""agent_framework.skills.migrator 单元测试"""

import tempfile
from pathlib import Path

import pytest

from agent_framework.skills.migrator import (
    MigrationReport,
    SkillMigrator,
)


class TestMigrationReport:
    """迁移报告数据结构测试"""

    def test_migration_report_creation(self):
        """测试创建迁移报告

        Given: 创建一个迁移报告
        When: 使用 valid=True 和 changes=2 初始化
        Then: 报告包含正确的属性
        """
        # Arrange & Act
        report = MigrationReport(
            success=True,
            changes=2,
            errors=[],
            warnings=["Content split into REFERENCE.md"],
        )

        # Assert
        assert report.success is True
        assert report.changes == 2
        assert len(report.errors) == 0
        assert len(report.warnings) == 1

    def test_migration_report_with_errors(self):
        """测试包含错误的迁移报告

        Given: 创建一个包含错误的迁移报告
        When: 使用 errors 列表初始化
        Then: success=False
        """
        # Arrange & Act
        report = MigrationReport(
            success=False,
            changes=0,
            errors=["Failed to backup file"],
            warnings=[],
        )

        # Assert
        assert report.success is False
        assert report.changes == 0
        assert len(report.errors) == 1


class TestSkillMigrator:
    """SKILL.md 迁移工具单元测试"""

    def test_migrate_nonexistent_file_fails(self):
        """测试迁移不存在的文件失败

        Given: 一个不存在的 SKILL.md 文件
        When: 调用 migrate
        Then: 返回 success=False，errors 包含文件不存在信息
        """
        # Arrange
        migrator = SkillMigrator()
        nonexistent_path = Path("/nonexistent/SKILL.md")

        # Act
        report = migrator.migrate(nonexistent_path)

        # Assert
        assert report.success is False
        assert len(report.errors) > 0
        assert "not found" in report.errors[0].lower() or "no such" in report.errors[0].lower()

    def test_migrate_creates_backup(self):
        """测试迁移前创建备份

        Given: 一个有效的 SKILL.md 文件
        When: 调用 migrate
        Then: 创建 .bak 备份文件
        """
        # Arrange
        migrator = SkillMigrator()
        content = """---
name: test-skill
description: Test capability.
---

# Test

Content here.
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(content)
            f.flush()
            skill_path = Path(f.name)

        try:
            # Act
            report = migrator.migrate(skill_path)

            # Assert
            backup_path = skill_path.with_suffix(skill_path.suffix + ".bak")
            assert backup_path.exists(), f"Backup file should exist at {backup_path}"
            assert report.success is True
        finally:
            # Cleanup
            for path in [skill_path, skill_path.with_suffix(".md.bak")]:
                if path.exists():
                    path.unlink()

    def test_migrate_splits_long_content(self):
        """测试拆分超长内容到 REFERENCE.md

        Given: 一个超过 100 行的 SKILL.md
        When: 调用 migrate
        Then: 创建 REFERENCE.md 并减少 SKILL.md 行数
        """
        # Arrange
        migrator = SkillMigrator(max_lines=50)  # 设置较小的阈值以便测试
        long_content = """---
name: test-skill
description: Test capability.
---

# Test Skill

## Quick start

Quick start content.

## Workflows

"""
        # 添加 60 行额外内容使其超过限制
        for i in range(60):
            long_content += f"Content line {i}\n"

        with tempfile.TemporaryDirectory() as tmpdir:
            skill_path = Path(tmpdir) / "SKILL.md"
            skill_path.write_text(long_content)

            # Act
            report = migrator.migrate(skill_path)

            # Assert
            reference_path = skill_path.parent / "REFERENCE.md"
            assert report.success is True
            assert report.changes > 1  # 至少备份 + 拆分
            assert reference_path.exists(), "REFERENCE.md should be created"

            # 验证 SKILL.md 行数减少
            new_content = skill_path.read_text()
            new_lines = new_content.split("\n")
            assert len(new_lines) <= migrator.max_lines + 10  # 允许一些误差

    def test_migrate_short_content_unchanged(self):
        """测试短内容不拆分

        Given: 一个少于 100 行的 SKILL.md
        When: 调用 migrate
        Then: 不创建 REFERENCE.md，返回警告
        """
        # Arrange
        migrator = SkillMigrator()
        short_content = """---
name: test-skill
description: Test capability.
---

# Test Skill

## Quick start

Quick start.

## Workflows

Workflows here.
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            skill_path = Path(tmpdir) / "SKILL.md"
            skill_path.write_text(short_content)

            # Act
            report = migrator.migrate(skill_path)

            # Assert
            reference_path = skill_path.parent / "REFERENCE.md"
            assert report.success is True
            assert not reference_path.exists(), "REFERENCE.md should not be created"
            assert any("compliant" in w.lower() or "no migration" in w.lower() for w in report.warnings)
