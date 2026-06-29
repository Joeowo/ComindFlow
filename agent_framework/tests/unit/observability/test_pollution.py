"""
S4-T6: ContextPollutionDetector 污染检测器测试

测试上下文污染检测功能。
"""

import pytest


def test_check_by_snapshot_comparison_no_pollution():
    """测试快照对比 - 无污染"""
    from agent_framework.observability.pollution import ContextPollutionDetector

    detector = ContextPollutionDetector()

    before = {"user": "Alice", "session": "123", "data": [1, 2, 3]}
    after = {"user": "Alice", "session": "123", "data": [1, 2, 3]}

    report = detector.check_by_snapshot_comparison(
        before_state=before,
        after_state=after,
        whitelist={"user", "session", "data"}
    )

    assert report.has_pollution is False
    assert len(report.unauthorized_changes) == 0


def test_check_by_snapshot_comparison_with_pollution():
    """测试快照对比 - 有污染"""
    from agent_framework.observability.pollution import ContextPollutionDetector

    detector = ContextPollutionDetector()

    before = {"user": "Alice", "session": "123"}
    after = {"user": "Alice", "session": "456", "unauthorized_key": True}

    report = detector.check_by_snapshot_comparison(
        before_state=before,
        after_state=after,
        whitelist={"user", "session"}
    )

    assert report.has_pollution is True
    assert len(report.unauthorized_changes) > 0


def test_check_by_snapshot_comparison_session_change_allowed():
    """测试快照对比 - session 变更在白名单中"""
    from agent_framework.observability.pollution import ContextPollutionDetector

    detector = ContextPollutionDetector()

    before = {"user": "Alice", "session": "123"}
    after = {"user": "Alice", "session": "456"}

    report = detector.check_by_snapshot_comparison(
        before_state=before,
        after_state=after,
        whitelist={"user", "session"}  # session 在白名单中
    )

    assert report.has_pollution is False


def test_check_by_whitelist_violation():
    """测试白名单违规检测"""
    from agent_framework.observability.pollution import ContextPollutionDetector

    detector = ContextPollutionDetector()

    current_state = {
        "user": "Alice",
        "session": "123",
        "secret_key": "should_not_be_here",  # 不在白名单中
    }

    report = detector.check_by_whitelist(
        current_state=current_state,
        whitelist={"user", "session"}
    )

    assert report.has_pollution is True
    assert "secret_key" in [change.key for change in report.unauthorized_changes]


def test_pollution_report_contains_all_fields():
    """测试污染报告包含所有必需字段"""
    from agent_framework.observability.pollution import ContextPollutionDetector

    detector = ContextPollutionDetector()

    report = detector.check_by_snapshot_comparison(
        before_state={},
        after_state={},
        whitelist=set()
    )

    assert hasattr(report, "has_pollution")
    assert hasattr(report, "unauthorized_changes")
    assert hasattr(report, "timestamp")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
