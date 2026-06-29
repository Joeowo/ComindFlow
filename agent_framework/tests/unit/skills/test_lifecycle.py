"""agent_framework.skills.lifecycle 单元测试"""

import tempfile
from pathlib import Path

import pytest

from agent_framework.skills.lifecycle import (
    SkillLifecycle,
    SkillRegistration,
    SkillHealthStatus,
)


class TestSkillRegistration:
    """技能注册数据结构测试"""

    def test_skill_registration_creation(self):
        """测试创建技能注册记录

        Given: 创建一个技能注册记录
        When: 使用必需参数初始化
        Then: 记录包含正确的属性
        """
        # Arrange & Act
        registration = SkillRegistration(
            name="test-skill",
            path=Path("/skills/test"),
            version="1.0",
        )

        # Assert
        assert registration.name == "test-skill"
        assert registration.path == Path("/skills/test")
        assert registration.version == "1.0"
        assert registration.active is True


class TestSkillLifecycle:
    """技能生命周期管理单元测试"""

    def test_discover_finds_skills_in_directory(self):
        """测试扫描目录发现技能

        Given: 一个包含 SKILL.md 文件的目录
        When: 调用 discover
        Then: 返回发现的技能列表
        """
        # Arrange
        lifecycle = SkillLifecycle()
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            skill_dir = tmpdir / "test-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("""---
name: test-skill
description: Test capability.
---

# Test Skill
""")

            # Act
            skills = lifecycle.discover(tmpdir)

            # Assert
            assert len(skills) == 1
            assert skills[0].name == "test-skill"

    def test_discover_ignores_non_skill_files(self):
        """测试扫描忽略非 SKILL.md 文件

        Given: 一个包含 README.md 但没有 SKILL.md 的目录
        When: 调用 discover
        Then: 返回空列表
        """
        # Arrange
        lifecycle = SkillLifecycle()
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            (tmpdir / "README.md").write_text("Readme content")

            # Act
            skills = lifecycle.discover(tmpdir)

            # Assert
            assert len(skills) == 0

    def test_register_adds_skill_to_tracking(self):
        """测试注册技能到跟踪列表

        Given: 一个技能注册记录
        When: 调用 register
        Then: 技能被添加到跟踪列表
        """
        # Arrange
        lifecycle = SkillLifecycle()
        registration = SkillRegistration(
            name="test-skill",
            path=Path("/skills/test"),
        )

        # Act
        lifecycle.register(registration)

        # Assert
        assert "test-skill" in lifecycle.list_registered()
        assert lifecycle.is_registered("test-skill")

    def test_unregister_removes_skill_from_tracking(self):
        """测试注销技能

        Given: 一个已注册的技能
        When: 调用 unregister
        Then: 技能从跟踪列表中移除
        """
        # Arrange
        lifecycle = SkillLifecycle()
        registration = SkillRegistration(
            name="test-skill",
            path=Path("/skills/test"),
        )
        lifecycle.register(registration)

        # Act
        lifecycle.unregister("test-skill")

        # Assert
        assert "test-skill" not in lifecycle.list_registered()
        assert not lifecycle.is_registered("test-skill")

    def test_register_duplicate_raises_error(self):
        """测试重复注册抛出错误

        Given: 一个已注册的技能名称
        When: 再次调用 register
        Then: 抛出 ValueError
        """
        # Arrange
        lifecycle = SkillLifecycle()
        registration = SkillRegistration(
            name="test-skill",
            path=Path("/skills/test"),
        )
        lifecycle.register(registration)

        # Act & Assert
        with pytest.raises(ValueError, match="already registered"):
            lifecycle.register(registration)

    def test_unregister_nonexistent_is_noop(self):
        """测试注销不存在的技能无操作

        Given: 一个不存在的技能名称
        When: 调用 unregister
        Then: 不抛出错误，无操作
        """
        # Arrange
        lifecycle = SkillLifecycle()

        # Act & Assert - 不应抛出错误
        lifecycle.unregister("nonexistent-skill")
        assert len(lifecycle.list_registered()) == 0


class TestSkillLifecycleLoadUnload:
    """技能加载和卸载测试"""

    def test_load_registered_skill(self):
        """测试加载已注册的技能

        Given: 一个已注册的技能
        When: 调用 load
        Then: 返回技能内容并标记为已加载
        """
        # Arrange
        lifecycle = SkillLifecycle()
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            skill_dir = tmpdir / "test-skill"
            skill_dir.mkdir()
            skill_md = skill_dir / "SKILL.md"
            skill_md.write_text("""---
name: test-skill
description: Test capability.
---

# Test Skill

Content here.
""")

            registration = SkillRegistration(name="test-skill", path=skill_dir)
            lifecycle.register(registration)

            # Act
            content = lifecycle.load("test-skill")

            # Assert
            assert content is not None
            assert "Test Skill" in content
            assert lifecycle.is_loaded("test-skill")

    def test_load_unregistered_skill_fails(self):
        """测试加载未注册的技能失败

        Given: 一个未注册的技能名称
        When: 调用 load
        Then: 返回 None
        """
        # Arrange
        lifecycle = SkillLifecycle()

        # Act
        content = lifecycle.load("nonexistent-skill")

        # Assert
        assert content is None

    def test_unload_skill_removes_from_loaded(self):
        """测试卸载技能

        Given: 一个已加载的技能
        When: 调用 unload
        Then: 技能不再标记为已加载
        """
        # Arrange
        lifecycle = SkillLifecycle()
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            skill_dir = tmpdir / "test-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("Content")

            registration = SkillRegistration(name="test-skill", path=skill_dir)
            lifecycle.register(registration)
            lifecycle.load("test-skill")

            # Act
            lifecycle.unload("test-skill")

            # Assert
            assert not lifecycle.is_loaded("test-skill")

    def test_unload_nonexistent_is_noop(self):
        """测试卸载不存在的技能无操作

        Given: 一个不存在的技能名称
        When: 调用 unload
        Then: 不抛出错误
        """
        # Arrange
        lifecycle = SkillLifecycle()

        # Act & Assert - 不应抛出错误
        lifecycle.unload("nonexistent-skill")

    def test_list_loaded_returns_loaded_skills(self):
        """测试列出已加载的技能

        Given: 多个已注册的技能，部分已加载
        When: 调用 list_loaded
        Then: 返回已加载的技能列表
        """
        # Arrange
        lifecycle = SkillLifecycle()
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # 创建两个技能
            for i in range(2):
                skill_dir = tmpdir / f"skill-{i}"
                skill_dir.mkdir()
                (skill_dir / "SKILL.md").write_text(f"Skill {i} content")
                registration = SkillRegistration(name=f"skill-{i}", path=skill_dir)
                lifecycle.register(registration)

            # 只加载第一个
            lifecycle.load("skill-0")

            # Act
            loaded = lifecycle.list_loaded()

            # Assert
            assert len(loaded) == 1
            assert "skill-0" in loaded
            assert "skill-1" not in loaded


class TestSkillLifecycleMonitoring:
    """技能监控和诊断测试"""

    def test_get_stats_returns_skill_statistics(self):
        """测试获取技能统计信息

        Given: 一个已注册和加载的技能
        When: 调用 get_stats
        Then: 返回包含执行统计的字典
        """
        # Arrange
        lifecycle = SkillLifecycle()
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            skill_dir = tmpdir / "test-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("Content")

            registration = SkillRegistration(name="test-skill", path=skill_dir)
            lifecycle.register(registration)
            lifecycle.load("test-skill")

            # Act
            stats = lifecycle.get_stats("test-skill")

            # Assert
            assert stats is not None
            assert "loaded" in stats
            assert stats["loaded"] is True
            assert "registered_at" in stats

    def test_get_stats_for_unregistered_skill_returns_none(self):
        """测试获取未注册技能的统计信息

        Given: 一个未注册的技能名称
        When: 调用 get_stats
        Then: 返回 None
        """
        # Arrange
        lifecycle = SkillLifecycle()

        # Act
        stats = lifecycle.get_stats("nonexistent-skill")

        # Assert
        assert stats is None

    def test_get_health_returns_healthy_status(self):
        """测试获取健康状态

        Given: 一个已注册且可访问的技能
        When: 调用 get_health
        Then: 返回 healthy=True
        """
        # Arrange
        lifecycle = SkillLifecycle()
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            skill_dir = tmpdir / "test-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("Content")

            registration = SkillRegistration(name="test-skill", path=skill_dir)
            lifecycle.register(registration)

            # Act
            health = lifecycle.get_health("test-skill")

            # Assert
            assert health is not None
            assert health.healthy is True

    def test_get_health_for_missing_skill_file_returns_unhealthy(self):
        """测试 SKILL.md 缺失时不健康

        Given: 一个注册的技能，但 SKILL.md 文件缺失
        When: 调用 get_health
        Then: 返回 healthy=False
        """
        # Arrange
        lifecycle = SkillLifecycle()
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            skill_dir = tmpdir / "test-skill"
            skill_dir.mkdir()
            # 不创建 SKILL.md

            registration = SkillRegistration(name="test-skill", path=skill_dir)
            lifecycle.register(registration)

            # Act
            health = lifecycle.get_health("test-skill")

            # Assert
            assert health is not None
            assert health.healthy is False

    def test_increment_execution_count(self):
        """测试增加执行计数

        Given: 一个已注册的技能
        When: 调用 record_execution
        Then: 执行计数增加
        """
        # Arrange
        lifecycle = SkillLifecycle()
        registration = SkillRegistration(name="test-skill", path=Path("/test"))
        lifecycle.register(registration)

        # Act
        lifecycle.record_execution("test-skill")
        lifecycle.record_execution("test-skill")

        # Assert
        stats = lifecycle.get_stats("test-skill")
        assert stats["execution_count"] == 2
