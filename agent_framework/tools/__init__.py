"""
Tools Layer - 工具适配层

封装现有模块（AutoResearch、review_agent、skills）为 LangChain Tools。
"""

# AutoResearch Tools
from .autoresearch_tools import (
    research_single_tool,
    research_deep_tool,
    AutoResearchAdapter,
)

# review_agent Tools
from .review_agent_tools import (
    ask_question_tool,
    generate_question_tool,
    ReviewAgentAdapter,
)

# Skills Adapters
from .skills_adapters import (
    SkillsAdapter,
    GrillMeAdapter,
    GrillYouAdapter,
    AdvanceTaskAdapter,
)

__all__ = [
    # AutoResearch Tools
    "research_single_tool",
    "research_deep_tool",
    "AutoResearchAdapter",
    # review_agent Tools
    "ask_question_tool",
    "generate_question_tool",
    "ReviewAgentAdapter",
    # Skills Adapters
    "SkillsAdapter",
    "GrillMeAdapter",
    "GrillYouAdapter",
    "AdvanceTaskAdapter",
]
