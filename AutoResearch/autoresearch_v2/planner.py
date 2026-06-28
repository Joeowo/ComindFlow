"""
任务规划模块
使用 LLM 分析用户自然语言 prompt，生成研究计划
"""
from dataclasses import dataclass
from typing import List, Optional
from .researcher_v2 import DeepSeekResearcher


@dataclass
class ResearchPlan:
    """研究计划"""
    topic: str
    research_type: str
    mode: str
    depth: str
    aspects: List[str]
    reasoning: str = ""


class TaskPlanner:
    """任务规划器 - 分析自然语言生成研究计划"""

    def __init__(self, researcher: DeepSeekResearcher = None):
        self.researcher = researcher or DeepSeekResearcher()

    def plan(self, user_prompt: str) -> ResearchPlan:
        """分析用户 prompt，生成研究计划"""
        print("\n🧠 分析研究需求...")

        system_prompt = """你是一个专业的研究规划专家。你的任务是分析用户的自然语言描述，生成结构化的研究计划。

请分析：
1. 研究主题 (topic) - 提炼核心研究主题
2. 研究类型 (type) - 从以下选择：学术、技术、市场、产品、通用
3. 研究模式 (mode) - single(简单), deep(深度), interactive(交互)
4. 研究深度 (depth) - basic, standard, comprehensive
5. 研究维度 (aspects) - 3-6个关键研究维度

请严格按照以下 JSON 格式返回，不要添加任何其他内容：

```json
{
    "topic": "研究主题",
    "research_type": "研究类型",
    "mode": "研究模式",
    "depth": "研究深度",
    "aspects": ["维度1", "维度2", "维度3", ...],
    "reasoning": "规划理由说明"
}
```

选择原则：
- 如果用户提到论文、学术、文献 → type=学术
- 如果用户提到技术、框架、开发 → type=技术
- 如果用户提到市场、竞争、趋势 → type=市场
- 如果用户提到产品、功能、评价 → type=产品
- 如果主题是综合性的 → type=通用

- 如果问题简单直接 → mode=single
- 如果需要多角度分析 → mode=deep
- 如果需要探索性研究 → mode=interactive

- 如果需要快速概览 → depth=basic
- 如果需要详细说明 → depth=standard
- 如果需要深入分析 → depth=comprehensive"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"用户需求：\n\n{user_prompt}"}
        ]

        result = self.researcher._make_request(messages, web_search=False, max_tokens=1000)

        content = result.get("choices", [{}])[0].get("message", {}).get("content", "")

        # 解析 JSON 结果
        import json
        import re

        # 提取 JSON
        json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # 尝试直接解析
            json_str = content.strip()
            # 移除可能的 markdown 代码块标记
            json_str = json_str.strip('`\n')

        try:
            plan_data = json.loads(json_str)

            return ResearchPlan(
                topic=plan_data.get("topic", "未知主题"),
                research_type=plan_data.get("research_type", "通用"),
                mode=plan_data.get("mode", "deep"),
                depth=plan_data.get("depth", "comprehensive"),
                aspects=plan_data.get("aspects", []),
                reasoning=plan_data.get("reasoning", "")
            )

        except json.JSONDecodeError as e:
            print(f"⚠️ 解析规划结果失败，使用默认计划: {e}")
            return self._default_plan(user_prompt)

    def _default_plan(self, user_prompt: str) -> ResearchPlan:
        """默认研究计划"""
        return ResearchPlan(
            topic=user_prompt[:100],
            research_type="通用",
            mode="deep",
            depth="comprehensive",
            aspects=[
                "概述与背景",
                "核心概念与技术",
                "主要方法与实现",
                "应用案例分析",
                "挑战与限制",
                "未来发展趋势"
            ],
            reasoning="使用默认研究计划"
        )

    @staticmethod
    def display_plan(plan: ResearchPlan):
        """显示研究计划"""
        print("\n" + "=" * 60)
        print("📋 研究计划")
        print("=" * 60)
        print(f"📌 主题: {plan.topic}")
        print(f"📝 类型: {plan.research_type}")
        print(f"🔧 模式: {plan.mode}")
        print(f"🔍 深度: {plan.depth}")
        print(f"\n📊 研究维度 ({len(plan.aspects)} 个):")
        for i, aspect in enumerate(plan.aspects, 1):
            print(f"   {i}. {aspect}")
        if plan.reasoning:
            print(f"\n💡 规划理由: {plan.reasoning}")
        print("=" * 60)

    @staticmethod
    def confirm_plan() -> bool:
        """确认研究计划"""
        try:
            response = input("\n是否开始执行此研究计划？(Y/n): ").strip().lower()
            return response in ("", "y", "yes")
        except (EOFError, KeyboardInterrupt):
            return True
