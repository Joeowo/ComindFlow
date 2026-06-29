"""标准化指令模板

提供 SKILL.md 的标准指令格式模板。
"""

from dataclasses import dataclass


class StandardInstructionError(Exception):
    """标准化指令错误"""


# 基础指令模板
_BASE_INSTRUCTION_TEMPLATE = """# Instructions for Claude

You are a specialized skill with the following capability:

## Skill Description

{description}

## Core Behavior

1. **Understand the user's request** - Identify what the user wants to accomplish
2. **Follow the skill-specific workflow** - Execute the appropriate steps
3. **Provide clear output** - Return results in a structured, understandable format

## Quick Start

{quick_start}

## Workflows

{workflows}

## Additional Notes

{additional_notes}

Remember: You are a specialized skill. Focus on your domain and do your job well.
"""


def get_standard_instruction(
    skill_name: str | None = None,
    description: str | None = None,
    quick_start: str | None = None,
    workflows: str | None = None,
    additional_notes: str | None = None,
) -> str:
    """获取标准化指令模板

    Args:
        skill_name: 技能名称（可选）
        description: 技能描述（可选）
        quick_start: 快速开始指南（可选）
        workflows: 工作流说明（可选）
        additional_notes: 额外说明（可选）

    Returns:
        标准化的指令字符串

    Raises:
        StandardInstructionError: 当参数无效时
    """
    # 验证参数
    if skill_name is not None and not isinstance(skill_name, str):
        raise StandardInstructionError("skill_name must be a string or None")

    if description is not None and not isinstance(description, str):
        raise StandardInstructionError("description must be a string or None")

    # 设置默认值
    if description is None:
        if skill_name:
            description = f"Capability provided by {skill_name} skill."
        else:
            description = "A specialized skill for specific tasks."

    if quick_start is None:
        quick_start = "Provide a minimal working example to get started."

    if workflows is None:
        workflows = "Describe the step-by-step processes for common tasks."

    if additional_notes is None:
        additional_notes = "No additional notes."

    # 生成指令
    return _BASE_INSTRUCTION_TEMPLATE.format(
        description=description,
        quick_start=quick_start,
        workflows=workflows,
        additional_notes=additional_notes,
    )
