"""
S4-T7: Observability Dashboard 测试

测试可观测性 Dashboard 的 CLI 和报告功能。
"""

import pytest
from datetime import datetime
from io import StringIO
import sys


def test_dashboard_initialization():
    """测试 Dashboard 初始化"""
    from agent_framework.observability.dashboard import ObservabilityDashboard

    dashboard = ObservabilityDashboard()

    assert dashboard is not None
    assert hasattr(dashboard, "view_trace")
    assert hasattr(dashboard, "get_error_stats")
    assert hasattr(dashboard, "get_skill_ranking")


def test_view_unknown_trace_returns_none():
    """测试查看不存在的 trace"""
    from agent_framework.observability.dashboard import ObservabilityDashboard

    dashboard = ObservabilityDashboard()
    trace = dashboard.view_trace("unknown-trace-id")

    assert trace is None


def test_get_error_stats_empty():
    """测试获取错误统计（无错误）"""
    from agent_framework.observability.dashboard import ObservabilityDashboard

    dashboard = ObservabilityDashboard()
    stats = dashboard.get_error_stats()

    assert stats is not None
    assert hasattr(stats, "total_errors")
    assert hasattr(stats, "by_severity")
    assert hasattr(stats, "by_type")


def test_get_skill_ranking():
    """测试获取技能排行"""
    from agent_framework.observability.dashboard import ObservabilityDashboard

    dashboard = ObservabilityDashboard()
    ranking = dashboard.get_skill_ranking()

    assert ranking is not None
    assert isinstance(ranking, list)


def test_generate_html_report():
    """测试生成 HTML 报告"""
    from agent_framework.observability.dashboard import ObservabilityDashboard
    import tempfile
    import os

    dashboard = ObservabilityDashboard()

    with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
        output_path = f.name

    try:
        dashboard.generate_html_report(output_path)
        assert os.path.exists(output_path)

        # 检查文件是否为有效的 HTML
        with open(output_path, "r", encoding="utf-8") as f:
            content = f.read()
            assert "<html" in content or "<!DOCTYPE html" in content
    finally:
        if os.path.exists(output_path):
            os.remove(output_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
