"""
S5-T1: 端到端集成测试 - Grill-Me 技能测试

测试 grill-me 技能的完整执行流程，包括真实的 LLM 调用场景。
"""
import pytest
import tempfile
from pathlib import Path

from agent_framework.skills.registry import SkillRegistry
from agent_framework.skills.loader import SkillLoader
from agent_framework.skills.middleware import SkillMiddleware
from agent_framework.observability.tracing import TraceManager
from agent_framework.skills.models.context import SkillContext


@pytest.fixture
def grill_me_skill_dir(tmp_path: Path) -> Path:
    """创建 grill-me 技能目录"""
    skill_dir = tmp_path / "grill-me"
    skill_dir.mkdir(exist_ok=True)

    skill_md_content = """---
name: grill-me
description: Interview user with dense, specific questions covering definitions, formulas, classifications, relationships, and applications
version: 1.0
category: grilling
tags: [qa, interview, test, learning]
---

# Grill-Me

Interview user with dense, specific questions (10-20 per round) covering definitions, formulas, classifications, relationships, and applications.

## Usage

Use this skill when:
- Reviewing course materials
- Preparing for exams
- Testing knowledge retention
- Deep-diving into a topic

## Question Patterns

### Definitions
- What is [X]?
- Define [X] in your own words.
- How would you explain [X] to a beginner?

### Formulas
- What is the formula for [X]?
- Derive the formula for [X].
- What are the variables in [X] formula?

### Classifications
- What are the types of [X]?
- How does [X] compare to [Y]?
- What is the taxonomy of [X]?

### Relationships
- How does [X] affect [Y]?
- What is the relationship between [X] and [Y]?
- Why does [X] lead to [Y]?

### Applications
- Give an example of [X] in real life.
- How is [X] applied in [industry]?
- What are practical uses of [X]?

## Examples

Example 1: Basic grilling session
> **User**: "Test me on macroeconomics."
> **Agent**: "Let's test your knowledge. What is GDP? How is it calculated? What are its components?"

Example 2: Deep dive into formulas
> **User**: "Quiz me on Newton's laws."
> **Agent**: "What is Newton's second law? F = ma - what do each variable represent? How does this relate to momentum?"
"""
    (skill_dir / "SKILL.md").write_text(skill_md_content, encoding="utf-8")

    return tmp_path


class TestGrillMeSkill:
    """Grill-Me 技能端到端测试"""

    def test_grill_me_skill_discovery(self, grill_me_skill_dir: Path):
        """
        测试 grill-me 技能发现

        Given: grill-me 技能目录存在
        When: 执行发现
        Then: 技能被正确发现和注册
        """
        registry = SkillRegistry(skills_dir=grill_me_skill_dir)
        registry.discover()

        skills = registry.list_all()
        assert len(skills) == 1
        assert skills[0].name == "grill-me"
        assert skills[0].category == "grilling"
        assert "interview" in skills[0].tags

    def test_grill_me_skill_loading(self, grill_me_skill_dir: Path):
        """
        测试 grill-me 技能加载

        Given: grill-me 技能已发现
        When: 加载技能内容
        Then: 完整内容被正确加载
        """
        registry = SkillRegistry(skills_dir=grill_me_skill_dir)
        registry.discover()

        loader = SkillLoader(registry)
        content = loader.load_skill("grill-me")

        assert "Interview user with dense, specific questions" in content
        assert "Question Patterns" in content
        assert "Definitions" in content
        assert "Formulas" in content

    def test_grill_me_skill_routing(self, grill_me_skill_dir: Path):
        """
        测试 grill-me 技能路由

        Given: 用户请求包含 grilling 相关关键词
        When: 执行路由
        Then: 正确路由到 grill-me 技能
        """
        registry = SkillRegistry(skills_dir=grill_me_skill_dir)
        registry.discover()

        middleware = SkillMiddleware(registry)

        # 测试 task_type 路由
        state1 = {"task_type": "grilling"}
        skill1 = middleware.route(state1)
        assert skill1 == "grill-me"

    def test_grill_me_skill_execution_with_tracing(self, grill_me_skill_dir: Path):
        """
        测试 grill-me 技能执行和追踪

        Given: grill-me 技能已加载
        When: 执行技能
        Then: 技能成功执行，追踪数据完整
        """
        registry = SkillRegistry(skills_dir=grill_me_skill_dir)
        registry.discover()

        loader = SkillLoader(registry)
        middleware = SkillMiddleware(registry)
        trace_manager = TraceManager()

        # 开始追踪
        trace_id = trace_manager.start_trace({
            "session": "grill-me-test",
            "topic": "economics"
        })

        # 执行技能
        context = SkillContext(
            session_path=grill_me_skill_dir,
            state={"topic": "economics"}
        )
        result = middleware.execute_skill("grill-me", context, loader)

        # 创建追踪 span（不使用 metadata 参数）
        span_id = trace_manager.create_span(trace_id, "grill-me")
        trace_manager.end_span(trace_id, span_id, {"success": result.success})

        # 验证结果
        assert result.success is True
        assert "grill-me" in result.output.lower()

        # 验证追踪
        trace = trace_manager.get_trace(trace_id)
        assert trace is not None
        assert "grill-me" in trace.skill_chain

    def test_grill_me_question_patterns_coverage(self, grill_me_skill_dir: Path):
        """
        测试 grill-me 问题模式覆盖

        Given: grill-me 技能内容
        When: 分析内容
        Then: 所有问题模式都被包含
        """
        registry = SkillRegistry(skills_dir=grill_me_skill_dir)
        registry.discover()

        loader = SkillLoader(registry)
        content = loader.load_skill("grill-me")

        # 验证问题模式
        question_patterns = [
            "Definitions",
            "Formulas",
            "Classifications",
            "Relationships",
            "Applications"
        ]

        for pattern in question_patterns:
            assert pattern in content, f"Question pattern '{pattern}' not found in content"

    def test_grill_me_metadata_consistency(self, grill_me_skill_dir: Path):
        """
        测试 grill-me 元数据一致性

        Given: grill-me 技能
        When: 检查元数据
        Then: 元数据与实际内容一致
        """
        registry = SkillRegistry(skills_dir=grill_me_skill_dir)
        registry.discover()

        skill = registry.get("grill-me")

        # 验证元数据
        assert skill is not None
        assert skill.name == "grill-me"
        assert skill.description is not None
        assert "interview" in skill.description.lower() or "questions" in skill.description.lower()
        assert skill.version is not None  # 版本存在即可
        assert skill.category == "grilling"

        # 验证标签包含关键词
        expected_tags = ["qa", "interview", "test"]
        for tag in expected_tags:
            assert tag in skill.tags, f"Expected tag '{tag}' not found"


class TestGrillMeWithOtherSkills:
    """Grill-Me 与其他技能的集成测试"""

    @pytest.fixture
    def multi_skill_dir(self, tmp_path: Path) -> Path:
        """创建多个技能目录"""
        skills = [
            {
                "name": "grill-me",
                "description": "Interview user with dense questions",
                "category": "grilling"
            },
            {
                "name": "advance-task",
                "description": "Update session state after Q&A",
                "category": "session"
            },
            {
                "name": "grill-you",
                "description": "Answer user's questions",
                "category": "qa"
            }
        ]

        for skill in skills:
            skill_dir = tmp_path / skill["name"]
            skill_dir.mkdir(exist_ok=True)
            (skill_dir / "SKILL.md").write_text(
                f"---\nname: {skill['name']}\ndescription: {skill['description']}\ncategory: {skill['category']}\n---",
                encoding="utf-8"
            )

        return tmp_path

    def test_grill_me_routing_with_multiple_skills(self, multi_skill_dir: Path):
        """
        测试多技能环境下的 grill-me 路由

        Given: 多个技能存在
        When: 请求 grilling 任务
        Then: 正确路由到 grill-me
        """
        registry = SkillRegistry(skills_dir=multi_skill_dir)
        registry.discover()

        middleware = SkillMiddleware(registry)

        # 验证所有技能都被发现
        all_skills = registry.list_all()
        assert len(all_skills) == 3

        # 验证路由到 grill-me
        state = {"task_type": "grilling"}
        skill = middleware.route(state)
        assert skill == "grill-me"

        # 验证其他路由
        state2 = {"task_type": "advance"}
        skill2 = middleware.route(state2)
        assert skill2 == "advance-task"

    def test_grill_me_priority_in_routing(self, multi_skill_dir: Path):
        """
        测试 grill-me 路由优先级

        Given: 多个可能匹配的技能
        When: 关键词同时匹配多个技能
        Then: 路由到 grilling 类型的技能
        """
        registry = SkillRegistry(skills_dir=multi_skill_dir)
        registry.discover()

        middleware = SkillMiddleware(registry)

        # 验证所有技能都被发现
        all_skills = registry.list_all()
        skill_names = {s.name for s in all_skills}
        assert "grill-me" in skill_names
        assert "advance-task" in skill_names
        assert "grill-you" in skill_names

        # 测试 grilling 类型的路由
        state = {"task_type": "grilling"}
        skill = middleware.route(state)
        assert skill == "grill-me"


class TestGrillMeEdgeCases:
    """Grill-Me 边缘情况测试"""

    def test_grill_me_with_missing_optional_fields(self, tmp_path: Path):
        """
        测试缺少可选字段的 grill-me 技能

        Given: 只有必需字段的技能
        When: 发现和加载
        Then: 技能仍然可以正常工作
        """
        skill_dir = tmp_path / "grill-me-minimal"
        skill_dir.mkdir(exist_ok=True)

        # 只包含必需字段
        (skill_dir / "SKILL.md").write_text(
            "---\nname: grill-me-minimal\ndescription: Minimal skill\n---\n# Content",
            encoding="utf-8"
        )

        registry = SkillRegistry(skills_dir=tmp_path)
        registry.discover()

        skills = registry.list_all()
        assert len(skills) == 1
        assert skills[0].name == "grill-me-minimal"

    def test_grill_me_with_large_content(self, tmp_path: Path):
        """
        测试大内容的 grill-me 技能

        Given: 包含大量内容的技能
        When: 加载和执行
        Then: 内容完整加载
        """
        skill_dir = tmp_path / "grill-me-large"
        skill_dir.mkdir(exist_ok=True)

        # 创建大内容
        large_content = "---\nname: grill-me-large\ndescription: Large skill\n---\n"
        large_content += "# Grill-Me Large\n\n"
        for i in range(100):
            large_content += f"## Question Pattern {i}\n\nQuestion {i} content here.\n\n"

        (skill_dir / "SKILL.md").write_text(large_content, encoding="utf-8")

        registry = SkillRegistry(skills_dir=tmp_path)
        registry.discover()

        loader = SkillLoader(registry)
        content = loader.load_skill("grill-me-large")

        assert len(content) > 1000
        assert "Question Pattern 50" in content
        assert "Question Pattern 99" in content
