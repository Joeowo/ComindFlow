"""
S4-T4/T5: 幻觉检测器

提供基于引用源验证和 LLM 自我评估的幻觉检测功能。
"""

import re
from typing import List, Dict, Any, Optional

from agent_framework.observability.models.hallucination import HallucinationReport


class HallucinationDetector:
    """幻觉检测器

    提供两种幻觉检测方法：
    1. 引用源验证：检查输出是否基于给定的引用源
    2. LLM 自我评估：让 LLM 评估自己输出的幻觉概率（同步版本）
    """

    # 简单的关键词提取模式（用于演示）
    _KEYWORD_PATTERN = re.compile(r"\b[A-Z][a-z]+\b")

    def check_by_source_validation(
        self,
        output: str,
        sources: List[str]
    ) -> HallucinationReport:
        """通过引用源验证检测幻觉

        Args:
            output: LLM 输出
            sources: 引用源列表

        Returns:
            HallucinationReport: 幻觉检测报告
        """
        if not output:
            return HallucinationReport(
                has_hallucination=False,
                grounding_score=0.0,
            )

        if not sources:
            return HallucinationReport(
                has_hallucination=False,
                grounding_score=0.0,
            )

        # 将所有源文本合并
        all_source_text = " ".join(sources).lower()
        output_lower = output.lower()

        # 简单的关键词匹配法（演示用）
        # 提取输出中的关键词
        output_keywords = set(self._KEYWORD_PATTERN.findall(output))

        # 计算有多少关键词在源中出现
        matched_keywords = sum(
            1 for kw in output_keywords
            if kw.lower() in all_source_text
        )

        # 计算贴地度分数
        if output_keywords:
            grounding_score = matched_keywords / len(output_keywords)
        else:
            grounding_score = 0.0

        # 判断是否有幻觉
        has_hallucination = grounding_score < 0.5

        # 收集无依据的主张
        ungrounded_claims = []
        if output_keywords:
            for kw in output_keywords:
                if kw.lower() not in all_source_text:
                    ungrounded_claims.append(kw)

        return HallucinationReport(
            has_hallucination=has_hallucination,
            grounding_score=grounding_score,
            ungrounded_claims=ungrounded_claims,
        )

    def check_by_llm_self_critique(
        self,
        output: str,
        context: Dict[str, Any]
    ) -> HallucinationReport:
        """通过 LLM 自我评估检测幻觉（同步版本）

        注意：这是同步版本，不实际调用 LLM，返回模拟结果。
        在生产环境中，这里应该调用 LLM API 进行自我评估。

        Args:
            output: LLM 输出
            context: 上下文信息

        Returns:
            HallucinationReport: 幻觉检测报告
        """
        # 模拟评估结果
        # 在实际实现中，这里应该调用 LLM API
        critique_result = "同步版本 - 模拟评估结果"

        return HallucinationReport(
            has_hallucination=False,  # 默认无幻觉
            grounding_score=0.8,  # 默认较高贴地度
            critique_result=critique_result,
        )

    def check_combined(
        self,
        output: str,
        sources: List[str],
        context: Dict[str, Any]
    ) -> HallucinationReport:
        """组合两种方法进行幻觉检测

        Args:
            output: LLM 输出
            sources: 引用源列表
            context: 上下文信息

        Returns:
            HallucinationReport: 幻觉检测报告
        """
        # 优先使用引用源验证
        source_report = self.check_by_source_validation(output, sources)

        # 如果有引用源，使用引用源验证结果
        if sources:
            return source_report

        # 否则使用 LLM 自我评估
        return self.check_by_llm_self_critique(output, context)
