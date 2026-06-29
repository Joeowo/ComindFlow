"""agent_framework.skills.validator 单元测试"""

import tempfile
from pathlib import Path

import pytest

from agent_framework.skills.validator import SkillValidator, ValidationResult


class TestSkillValidator:
    """SKILL.md 规范验证器单元测试"""

    def test_valid_skill_passes_validation(self):
        """测试有效的 SKILL.md 通过验证

        Given: 一个符合 write-a-skill 规范的 SKILL.md 文件
        When: 验证该文件
        Then: 返回 valid=True，errors 和 warnings 为空
        """
        # Arrange
        valid_content = """---
name: test-skill
description: Test capability. Use when testing.
---

# Test Skill

## Quick start

Test quick start.

## Workflows

Test workflows.
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(valid_content)
            f.flush()
            skill_path = Path(f.name)

        try:
            # Act
            validator = SkillValidator()
            result = validator.validate(skill_path)

            # Assert
            assert result.valid is True
            assert len(result.errors) == 0
            assert len(result.warnings) == 0
        finally:
            skill_path.unlink()

    def test_missing_file_returns_invalid(self):
        """测试文件不存在返回无效

        Given: 一个不存在的文件路径
        When: 验证该文件
        Then: 返回 valid=False，errors 包含文件不存在信息
        """
        # Arrange
        nonexistent_path = Path("/nonexistent/SKILL.md")

        # Act
        validator = SkillValidator()
        result = validator.validate(nonexistent_path)

        # Assert
        assert result.valid is False
        assert len(result.errors) == 1
        assert "not found" in result.errors[0].lower()

    def test_missing_name_field_fails(self):
        """测试缺少 name 字段失败

        Given: 一个缺少 name 字段的 SKILL.md
        When: 验证该文件
        Then: 返回 valid=False，errors 包含缺少 name 字段信息
        """
        # Arrange
        invalid_content = """---
description: Test capability.
---

# Test
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(invalid_content)
            f.flush()
            skill_path = Path(f.name)

        try:
            # Act
            validator = SkillValidator()
            result = validator.validate(skill_path)

            # Assert
            assert result.valid is False
            assert "Missing required field: name" in result.errors
        finally:
            skill_path.unlink()

    def test_missing_description_field_fails(self):
        """测试缺少 description 字段失败

        Given: 一个缺少 description 字段的 SKILL.md
        When: 验证该文件
        Then: 返回 valid=False，errors 包含缺少 description 字段信息
        """
        # Arrange
        invalid_content = """---
name: test-skill
---

# Test
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(invalid_content)
            f.flush()
            skill_path = Path(f.name)

        try:
            # Act
            validator = SkillValidator()
            result = validator.validate(skill_path)

            # Assert
            assert result.valid is False
            assert "Missing required field: description" in result.errors
        finally:
            skill_path.unlink()

    def test_missing_both_fields_fails(self):
        """测试同时缺少 name 和 description 字段失败

        Given: 一个同时缺少 name 和 description 字段的 SKILL.md
        When: 验证该文件
        Then: 返回 valid=False，errors 包含两个错误信息
        """
        # Arrange
        invalid_content = """---

# Test
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(invalid_content)
            f.flush()
            skill_path = Path(f.name)

        try:
            # Act
            validator = SkillValidator()
            result = validator.validate(skill_path)

            # Assert
            assert result.valid is False
            assert len(result.errors) == 2
            assert "Missing required field: name" in result.errors
            assert "Missing required field: description" in result.errors
        finally:
            skill_path.unlink()

    def test_excessive_lines_generates_warning(self):
        """测试超过 100 行生成警告

        Given: 一个超过 100 行的 SKILL.md
        When: 验证该文件
        Then: 返回 valid=True（仍有警告），warnings 包含行数信息
        """
        # Arrange
        long_content = """---
name: test-skill
description: Test capability. Use when testing.
---

# Test Skill

"""
        # 添加足够多的行使其超过 100 行
        for i in range(95):
            long_content += f"Line {i}\n"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(long_content)
            f.flush()
            skill_path = Path(f.name)

        try:
            # Act
            validator = SkillValidator()
            result = validator.validate(skill_path)

            # Assert
            assert result.valid is True  # 仍然有效，只是有警告
            assert len(result.errors) == 0
            assert len(result.warnings) > 0
            assert any("exceeds" in w.lower() or "lines" in w.lower() for w in result.warnings)
        finally:
            skill_path.unlink()

    def test_normal_lines_no_warning(self):
        """测试正常行数无警告

        Given: 一个少于 100 行的 SKILL.md
        When: 验证该文件
        Then: 返回 valid=True，warnings 不包含行数警告
        """
        # Arrange
        normal_content = """---
name: test-skill
description: Test capability. Use when testing.
---

# Test Skill

## Quick start

Test quick start.

## Workflows

Test workflows.
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(normal_content)
            f.flush()
            skill_path = Path(f.name)

        try:
            # Act
            validator = SkillValidator()
            result = validator.validate(skill_path)

            # Assert
            assert result.valid is True
            assert len(result.errors) == 0
            assert len(result.warnings) == 0
        finally:
            skill_path.unlink()

    def test_missing_quick_start_section_warning(self):
        """测试缺少 Quick start 章节警告

        Given: 一个缺少 Quick start 章节的 SKILL.md
        When: 验证该文件
        Then: 返回 valid=True，warnings 包含缺少章节信息
        """
        # Arrange
        content = """---
name: test-skill
description: Test capability. Use when testing.
---

# Test Skill

## Workflows

Test workflows.
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(content)
            f.flush()
            skill_path = Path(f.name)

        try:
            # Act
            validator = SkillValidator()
            result = validator.validate(skill_path)

            # Assert
            assert result.valid is True
            assert len(result.errors) == 0
            assert any("quick start" in w.lower() or "Quick start" in w for w in result.warnings)
        finally:
            skill_path.unlink()

    def test_missing_workflows_section_warning(self):
        """测试缺少 Workflows 章节警告

        Given: 一个缺少 Workflows 章节的 SKILL.md
        When: 验证该文件
        Then: 返回 valid=True，warnings 包含缺少章节信息
        """
        # Arrange
        content = """---
name: test-skill
description: Test capability. Use when testing.
---

# Test Skill

## Quick start

Test quick start.
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(content)
            f.flush()
            skill_path = Path(f.name)

        try:
            # Act
            validator = SkillValidator()
            result = validator.validate(skill_path)

            # Assert
            assert result.valid is True
            assert len(result.errors) == 0
            assert any("workflows" in w.lower() or "Workflows" in w for w in result.warnings)
        finally:
            skill_path.unlink()

    def test_complete_skill_no_warnings(self):
        """测试完整的 SKILL.md 无警告

        Given: 一个包含所有必需章节的 SKILL.md
        When: 验证该文件
        Then: 返回 valid=True，无警告
        """
        # Arrange
        complete_content = """---
name: test-skill
description: Test capability. Use when testing.
---

# Test Skill

## Quick start

Test quick start.

## Workflows

Test workflows.
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(complete_content)
            f.flush()
            skill_path = Path(f.name)

        try:
            # Act
            validator = SkillValidator()
            result = validator.validate(skill_path)

            # Assert
            assert result.valid is True
            assert len(result.errors) == 0
            assert len(result.warnings) == 0
        finally:
            skill_path.unlink()
