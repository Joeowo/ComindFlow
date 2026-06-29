"""标准化指令集和工具接口

提供 SKILL.md 的标准格式模板和验证。
"""

from agent_framework.skills.standards.instructions import (
    get_standard_instruction,
    StandardInstructionError,
)

__all__ = [
    "get_standard_instruction",
    "StandardInstructionError",
]
