"""
配置管理模块
从 .env 文件加载配置
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

# 加载环境变量
load_dotenv(ENV_FILE)


class Config:
    """应用配置"""

    # DeepSeek API 配置
    API_KEY = os.getenv("apikey")
    BASE_URL = os.getenv("base", "https://api.deepseek.com")
    MODEL = os.getenv("model", "deepseek-v4-pro")

    # 输出配置
    OUTPUT_DIR = PROJECT_ROOT / "output"
    REPORTS_DIR = OUTPUT_DIR / "reports"

    # 研究配置
    MAX_RETRIES = 3
    TIMEOUT = 120
    MAX_TOKENS = 16000

    # WebSearch 配置
    WEB_SEARCH_ENABLED = True

    @classmethod
    def validate(cls):
        """验证配置"""
        if not cls.API_KEY:
            raise ValueError("API_KEY 未配置，请在 .env 文件中设置 apikey")

        # 创建输出目录
        cls.REPORTS_DIR.mkdir(parents=True, exist_ok=True)

        return True

    @classmethod
    def display(cls):
        """显示当前配置"""
        print("=" * 50)
        print("AutoResearch 配置")
        print("=" * 50)
        print(f"API Key: {cls.API_KEY[:20]}..." if cls.API_KEY else "未配置")
        print(f"Base URL: {cls.BASE_URL}")
        print(f"Model: {cls.MODEL}")
        print(f"输出目录: {cls.REPORTS_DIR}")
        print(f"WebSearch: {'启用' if cls.WEB_SEARCH_ENABLED else '禁用'}")
        print("=" * 50)


# 预定义的研究模板
RESEARCH_TEMPLATES = {
    "学术": {
        "description": "学术论文调研，搜索相关论文、作者、机构信息",
        "search_query_template": "{topic} 论文 research papers academic",
        "focus_areas": ["核心论文", "研究方法", "实验结果", "相关工作", "未来方向"],
    },
    "技术": {
        "description": "技术调研，了解最新技术发展、框架、工具",
        "search_query_template": "{topic} 技术 development framework tools 2025",
        "focus_areas": ["技术概述", "主流方案", "优缺点对比", "应用场景", "发展趋势"],
    },
    "市场": {
        "description": "市场调研，分析市场规模、竞争格局、趋势",
        "search_query_template": "{topic} 市场 market analysis 竞争格局 趋势",
        "focus_areas": ["市场规模", "主要玩家", "竞争分析", "发展趋势", "机会与挑战"],
    },
    "产品": {
        "description": "产品调研，了解产品功能、用户评价、竞品分析",
        "search_query_template": "{topic} 产品 review 评测 用户体验",
        "focus_areas": ["产品概述", "核心功能", "用户评价", "竞品对比", "购买建议"],
    },
    "通用": {
        "description": "通用研究，全面了解主题相关信息",
        "search_query_template": "{topic}",
        "focus_areas": ["概述", "核心信息", "详细分析", "总结", "参考资料"],
    },
}
