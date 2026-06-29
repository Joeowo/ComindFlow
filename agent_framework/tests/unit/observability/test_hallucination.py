"""
S4-T4/T5: HallucinationDetector 幻觉检测器测试

测试基于引用源验证和 LLM 自我评估的幻觉检测。
"""

import pytest


def test_check_by_source_validation_no_hallucination():
    """测试引用源验证 - 无幻觉"""
    from agent_framework.observability.hallucination import HallucinationDetector

    detector = HallucinationDetector()

    report = detector.check_by_source_validation(
        output="The capital of France is Paris.",
        sources=["France is a country in Europe with capital Paris."]
    )

    assert report.has_hallucination is False
    # 由于关键词匹配算法的简化，贴地度可能不会很高
    # 只要不低于阈值就算无幻觉
    assert report.grounding_score >= 0.5


def test_check_by_source_validation_with_hallucination():
    """测试引用源验证 - 有幻觉"""
    from agent_framework.observability.hallucination import HallucinationDetector

    detector = HallucinationDetector()

    report = detector.check_by_source_validation(
        output="The capital of France is London.",
        sources=["France is a country in Europe with capital Paris."]
    )

    assert report.has_hallucination is True
    assert report.grounding_score < 0.5


def test_check_by_source_validation_empty_output():
    """测试引用源验证 - 空输出"""
    from agent_framework.observability.hallucination import HallucinationDetector

    detector = HallucinationDetector()

    report = detector.check_by_source_validation(
        output="",
        sources=["Some source text."]
    )

    assert report.grounding_score == 0.0


def test_check_by_source_validation_no_sources():
    """测试引用源验证 - 无引用源"""
    from agent_framework.observability.hallucination import HallucinationDetector

    detector = HallucinationDetector()

    report = detector.check_by_source_validation(
        output="Some output without sources.",
        sources=[]
    )

    # 无引用源时，无法验证
    assert report.grounding_score == 0.0


def test_check_by_llm_self_critique():
    """测试 LLM 自我评估（同步版本）"""
    from agent_framework.observability.hallucination import HallucinationDetector

    detector = HallucinationDetector()

    # 使用 mock 结果（同步版本不实际调用 LLM）
    report = detector.check_by_llm_self_critique(
        output="Test output",
        context={"question": "Test question"}
    )

    assert report.critique_result is not None
    assert hasattr(report, "has_hallucination")


def test_combined_hallucination_check():
    """测试组合幻觉检测"""
    from agent_framework.observability.hallucination import HallucinationDetector

    detector = HallucinationDetector()

    report = detector.check_combined(
        output="The capital of France is Paris.",
        sources=["France is a country with capital Paris."],
        context={"question": "What is the capital of France?"}
    )

    assert hasattr(report, "grounding_score")
    assert hasattr(report, "has_hallucination")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
