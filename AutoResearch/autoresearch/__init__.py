"""
AutoResearch - 自动化研究应用
基于 DeepSeek V4-Pro + WebSearch
"""

from .config import Config, RESEARCH_TEMPLATES
from .researcher import DeepSeekResearcher, SearchQuery, ResearchResult
from .reporter import ReportGenerator
from .planner import TaskPlanner, ResearchPlan

__version__ = "1.0.0"
__author__ = "AutoResearch"
__all__ = [
    "Config",
    "RESEARCH_TEMPLATES",
    "DeepSeekResearcher",
    "SearchQuery",
    "ResearchResult",
    "ReportGenerator",
    "TaskPlanner",
    "ResearchPlan",
]
