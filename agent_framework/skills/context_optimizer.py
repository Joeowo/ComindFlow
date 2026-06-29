"""
S3-T1: ContextOptimizer - 上下文优化器

实现元数据注入和按需加载功能，降低上下文Token消耗。
"""

from loguru import logger


class ContextOptimizer:
    """上下文优化器

    通过"目录注入+按需加载"策略，将单次任务的Token消耗降低30%以上。

    Attributes:
        registry: 技能注册表，用于查询已注册的技能元数据
    """

    def __init__(self, registry) -> None:
        """初始化上下文优化器

        Args:
            registry: SkillRegistry 实例
        """
        self.registry = registry
        logger.info("ContextOptimizer initialized")

    def inject_metadata(self) -> str:
        """注入所有 Skills 的元数据

        只注入 YAML frontmatter 和章节结构，不注入完整内容。

        Returns:
            注入的上下文字符串（包含技能名称、描述、标签等）
        """
        metadata_injection = ["## Skills Available\n"]

        for skill in self.registry.list_all():
            metadata_injection.append(f"\n### {skill.name}")
            metadata_injection.append(f"{skill.description}")
            if skill.tags:
                metadata_injection.append(f"**Tags:** {', '.join(skill.tags)}")

        result = "\n".join(metadata_injection)
        logger.info(
            "Metadata injected",
            skill_count=len(self.registry.list_all()),
            estimated_tokens=len(result) // 4
        )
        return result

    def should_load_full_content(self, skill_name: str, state: dict) -> bool:
        """判断是否需要加载完整内容

        根据触发条件决定是否加载技能的完整 SKILL.md 内容：
        1. 任务类型匹配技能的 category
        2. 用户查询包含技能的标签
        3. 待处理技能调用列表包含该技能

        Args:
            skill_name: 技能名称
            state: 当前执行状态，包含 task_type, user_query, pending_skill_calls 等字段

        Returns:
            是否需要加载完整内容
        """
        try:
            skill = self.registry.get(skill_name)
        except Exception:
            # 技能不存在，不加载
            logger.debug("Skill not found, skipping load", skill=skill_name)
            return False

        # 检查任务类型匹配
        task_type = state.get("task_type")
        if task_type and task_type == skill.category:
            logger.info(
                "Loading full content by task_type match",
                skill=skill_name,
                task_type=task_type
            )
            return True

        # 检查用户查询匹配标签
        user_query = state.get("user_query", "")
        if user_query and skill.tags:
            # 将用户查询转为小写进行匹配
            query_lower = user_query.lower()
            for tag in skill.tags:
                if tag.lower() in query_lower:
                    logger.info(
                        "Loading full content by user_query tag match",
                        skill=skill_name,
                        tag=tag
                    )
                    return True

        # 检查待处理技能调用列表
        pending_calls = state.get("pending_skill_calls", [])
        if pending_calls and skill_name in pending_calls:
            logger.info(
                "Loading full content by pending_skill_calls",
                skill=skill_name
            )
            return True

        # 没有触发条件，不加载
        return False
