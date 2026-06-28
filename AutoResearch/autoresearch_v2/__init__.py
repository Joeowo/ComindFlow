"""
AutoResearch V2 - 强化置信度的自动化研究工具
基于 DeepSeek V4-Pro + WebSearch + 学术规范化
"""

from .config import Config, RESEARCH_TEMPLATES
from .researcher_v2 import DeepSeekResearcher, SearchQuery, ResearchResult, Source, SourceExtractor
from .reporter_v2 import ReportGenerator, ReferenceFormatter
from .planner import TaskPlanner, ResearchPlan

__version__ = "2.0.0"
__author__ = "AutoResearch"

__all__ = [
    # 配置
    "Config",
    "RESEARCH_TEMPLATES",
    # 研究器
    "DeepSeekResearcher",
    "SearchQuery",
    "ResearchResult",
    "Source",
    "SourceExtractor",
    # 报告生成
    "ReportGenerator",
    "ReferenceFormatter",
    # 规划器
    "TaskPlanner",
    "ResearchPlan",
]

# 导入配置
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from autoresearch.config import Config as _BaseConfig
    from autoresearch import RESEARCH_TEMPLATES as _BaseTemplates
    Config = _BaseConfig
    RESEARCH_TEMPLATES = _BaseTemplates
except ImportError:
    # 如果无法导入，使用本地配置
    from .config import Config, RESEARCH_TEMPLATES
