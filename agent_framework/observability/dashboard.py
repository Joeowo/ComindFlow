"""
S4-T7: 可观测性 Dashboard

提供 CLI 和 HTML 报告功能。
"""

import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Any, Optional

from agent_framework.observability.tracing import TraceManager


@dataclass(frozen=True)
class ErrorStats:
    """错误统计

    Attributes:
        total_errors: 总错误数
        by_severity: 按严重程度统计
        by_type: 按错误类型统计
    """

    total_errors: int
    by_severity: Dict[str, int] = field(default_factory=dict)
    by_type: Dict[str, int] = field(default_factory=dict)


@dataclass(frozen=True)
class SkillRankingEntry:
    """技能排行条目

    Attributes:
        skill_name: 技能名称
        call_count: 调用次数
        error_count: 错误次数
        error_rate: 错误率
    """

    skill_name: str
    call_count: int
    error_count: int
    error_rate: float


@dataclass(frozen=True)
class SkillRanking:
    """技能排行

    Attributes:
        skills: 技能排行列表
        generated_at: 生成时间
    """

    skills: List[SkillRankingEntry] = field(default_factory=list)
    generated_at: datetime = field(default_factory=datetime.now)


class ObservabilityDashboard:
    """可观测性 Dashboard

    提供查询和可视化可观测性数据的功能。
    """

    def __init__(self) -> None:
        """初始化 Dashboard"""
        self._trace_manager = TraceManager()
        self._errors: List[Any] = []  # 存储错误记录
        self._skill_calls: Dict[str, int] = {}  # 技能调用计数

    def view_trace(self, trace_id: str) -> Optional[Any]:
        """查看指定追踪数据

        Args:
            trace_id: 追踪 ID

        Returns:
            追踪数据，如果不存在返回 None
        """
        return self._trace_manager.get_trace(trace_id)

    def get_error_stats(self) -> ErrorStats:
        """获取错误统计

        Returns:
            ErrorStats: 错误统计报告
        """
        by_severity: Dict[str, int] = {}
        by_type: Dict[str, int] = {}

        for error in self._errors:
            severity = error.severity if hasattr(error, "severity") else "Unknown"
            error_type = error.error_type if hasattr(error, "error_type") else "Unknown"

            by_severity[severity] = by_severity.get(severity, 0) + 1
            by_type[error_type] = by_type.get(error_type, 0) + 1

        return ErrorStats(
            total_errors=len(self._errors),
            by_severity=by_severity,
            by_type=by_type,
        )

    def get_skill_ranking(self) -> List[SkillRankingEntry]:
        """获取技能排行

        Returns:
            List[SkillRankingEntry]: 技能排行列表
        """
        ranking = []
        for skill_name, call_count in self._skill_calls.items():
            ranking.append(
                SkillRankingEntry(
                    skill_name=skill_name,
                    call_count=call_count,
                    error_count=0,  # 简化实现
                    error_rate=0.0,
                )
            )

        # 按调用次数排序
        ranking.sort(key=lambda x: x.call_count, reverse=True)
        return ranking

    def generate_html_report(self, output_path: str) -> None:
        """生成 HTML 报告

        Args:
            output_path: 输出文件路径
        """
        stats = self.get_error_stats()
        ranking = self.get_skill_ranking()

        html_content = self._generate_html_content(stats, ranking)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)

    def _generate_html_content(
        self,
        stats: ErrorStats,
        ranking: List[SkillRankingEntry]
    ) -> str:
        """生成 HTML 内容

        Args:
            stats: 错误统计
            ranking: 技能排行

        Returns:
            HTML 内容字符串
        """
        return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>可观测性 Dashboard</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            margin: 40px;
            background: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            border-bottom: 2px solid #4CAF50;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #555;
            margin-top: 30px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background: #4CAF50;
            color: white;
        }}
        tr:hover {{
            background: #f5f5f5;
        }}
        .stat-card {{
            display: inline-block;
            margin: 10px;
            padding: 20px;
            background: #e8f5e9;
            border-radius: 8px;
            min-width: 200px;
        }}
        .stat-number {{
            font-size: 32px;
            font-weight: bold;
            color: #2e7d32;
        }}
        .timestamp {{
            color: #888;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 可观测性 Dashboard</h1>
        <p class="timestamp">生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>

        <h2>📊 错误统计</h2>
        <div class="stat-card">
            <div>总错误数</div>
            <div class="stat-number">{stats.total_errors}</div>
        </div>

        <h3>按严重程度</h3>
        <table>
            <tr>
                <th>严重程度</th>
                <th>数量</th>
            </tr>
            {"".join(f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in stats.by_severity.items())}
        </table>

        <h3>按错误类型</h3>
        <table>
            <tr>
                <th>错误类型</th>
                <th>数量</th>
            </tr>
            {"".join(f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in stats.by_type.items())}
        </table>

        <h2>🏆 技能排行</h2>
        <table>
            <tr>
                <th>技能名称</th>
                <th>调用次数</th>
                <th>错误率</th>
            </tr>
            {"".join(f"<tr><td>{s.skill_name}</td><td>{s.call_count}</td><td>{s.error_rate:.1%}</td></tr>" for s in ranking)}
        </table>
    </div>
</body>
</html>"""

    def record_skill_call(self, skill_name: str) -> None:
        """记录技能调用

        Args:
            skill_name: 技能名称
        """
        self._skill_calls[skill_name] = self._skill_calls.get(skill_name, 0) + 1

    def record_error(self, error: Any) -> None:
        """记录错误

        Args:
            error: 错误记录
        """
        self._errors.append(error)
